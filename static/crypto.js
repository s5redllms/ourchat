/**
 * Client-side encryption utilities for end-to-end encryption
 * Uses Web Crypto API with AES-GCM encryption
 */

class E2EEncryption {
    constructor() {
        this.algorithm = 'AES-GCM';
        this.keyLength = 256;
        this.ivLength = 12; // 96 bits for GCM
        this.tagLength = 16; // 128 bits for GCM
        this.saltLength = 16; // 128 bits for PBKDF2
        this.iterations = 100000; // PBKDF2 iterations
        this.cache = new Map(); // Cache for derived keys
    }

    /**
     * Derive AES key from passphrase using PBKDF2
     * @param {string} passphrase - User's encryption passphrase
     * @param {Uint8Array} salt - Salt for key derivation
     * @returns {Promise<CryptoKey>} - Derived AES key
     */
    async deriveKey(passphrase, salt) {
        // Check cache first
        const cacheKey = passphrase + ':' + Array.from(salt).join(',');
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey);
        }

        try {
            // Import passphrase as key material
            const keyMaterial = await crypto.subtle.importKey(
                'raw',
                new TextEncoder().encode(passphrase),
                'PBKDF2',
                false,
                ['deriveKey']
            );

            // Derive AES key
            const key = await crypto.subtle.deriveKey(
                {
                    name: 'PBKDF2',
                    salt: salt,
                    iterations: this.iterations,
                    hash: 'SHA-256'
                },
                keyMaterial,
                {
                    name: this.algorithm,
                    length: this.keyLength
                },
                false,
                ['encrypt', 'decrypt']
            );

            // Cache the key
            this.cache.set(cacheKey, key);
            return key;
        } catch (error) {
            console.error('Key derivation failed:', error);
            throw new Error('Failed to derive encryption key');
        }
    }

    /**
     * Encrypt plaintext message
     * @param {string} plaintext - Message to encrypt
     * @param {string} passphrase - User's encryption passphrase
     * @returns {Promise<string>} - Base64 encoded encrypted data
     */
    async encrypt(plaintext, passphrase) {
        if (!plaintext || !passphrase) {
            throw new Error('Plaintext and passphrase are required');
        }

        try {
            // Generate random salt and IV
            const salt = crypto.getRandomValues(new Uint8Array(this.saltLength));
            const iv = crypto.getRandomValues(new Uint8Array(this.ivLength));

            // Derive encryption key
            const key = await this.deriveKey(passphrase, salt);

            // Encrypt the message
            const encoder = new TextEncoder();
            const data = encoder.encode(plaintext);

            const encryptedData = await crypto.subtle.encrypt(
                {
                    name: this.algorithm,
                    iv: iv,
                    tagLength: this.tagLength * 8 // Convert to bits
                },
                key,
                data
            );

            // Combine salt + iv + encrypted data
            const combined = new Uint8Array(
                salt.length + iv.length + encryptedData.byteLength
            );
            
            combined.set(salt, 0);
            combined.set(iv, salt.length);
            combined.set(new Uint8Array(encryptedData), salt.length + iv.length);

            // Return base64 encoded result
            return this.arrayBufferToBase64(combined);
        } catch (error) {
            console.error('Encryption failed:', error);
            throw new Error('Failed to encrypt message');
        }
    }

    /**
     * Decrypt encrypted message
     * @param {string} encryptedText - Base64 encoded encrypted data
     * @param {string} passphrase - User's encryption passphrase
     * @returns {Promise<string>} - Decrypted plaintext message
     */
    async decrypt(encryptedText, passphrase) {
        if (!encryptedText || !passphrase) {
            throw new Error('Encrypted text and passphrase are required');
        }

        try {
            // Decode from base64
            const combined = this.base64ToArrayBuffer(encryptedText);

            // Extract salt, iv, and encrypted data
            const salt = combined.slice(0, this.saltLength);
            const iv = combined.slice(this.saltLength, this.saltLength + this.ivLength);
            const encryptedData = combined.slice(this.saltLength + this.ivLength);

            // Derive decryption key
            const key = await this.deriveKey(passphrase, salt);

            // Decrypt the message
            const decryptedData = await crypto.subtle.decrypt(
                {
                    name: this.algorithm,
                    iv: iv,
                    tagLength: this.tagLength * 8 // Convert to bits
                },
                key,
                encryptedData
            );

            // Convert back to string
            const decoder = new TextDecoder();
            return decoder.decode(decryptedData);
        } catch (error) {
            console.error('Decryption failed:', error);
            throw new Error('Failed to decrypt message');
        }
    }

    /**
     * Check if a message appears to be encrypted
     * @param {string} text - Text to check
     * @returns {boolean} - True if text appears encrypted
     */
    isEncrypted(text) {
        if (!text || typeof text !== 'string') return false;
        
        // Check if it's a valid base64 string
        const base64Regex = /^[A-Za-z0-9+/]+=*$/;
        if (!base64Regex.test(text)) return false;
        
        // More lenient minimum length check - just ensure it's long enough to contain our structure
        // Salt (16) + IV (12) + minimal data (1) + tag (16) = 45 bytes minimum
        // Base64 encoding: 45 bytes * 4/3 ≈ 60 characters minimum
        const minLength = 60;
        const result = text.length >= minLength;
        
        // Debug logging
        console.log('🔍 isEncrypted check:', {
            text: text.substring(0, 30) + '...',
            length: text.length,
            minLength: minLength,
            passesRegex: base64Regex.test(text),
            passesLength: result,
            result: result
        });
        
        return result;
    }

    /**
     * Convert ArrayBuffer to base64
     * @param {ArrayBuffer|Uint8Array} buffer - Buffer to convert
     * @returns {string} - Base64 string
     */
    arrayBufferToBase64(buffer) {
        const bytes = new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary);
    }

    /**
     * Convert base64 to ArrayBuffer
     * @param {string} base64 - Base64 string
     * @returns {Uint8Array} - Array buffer
     */
    base64ToArrayBuffer(base64) {
        const binary = atob(base64);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
            bytes[i] = binary.charCodeAt(i);
        }
        return bytes;
    }

    /**
     * Clear the key cache (call on logout)
     */
    clearCache() {
        this.cache.clear();
    }

    /**
     * Generate a test to verify encryption/decryption works
     * @param {string} passphrase - Passphrase to test with
     * @returns {Promise<boolean>} - True if test passes
     */
    async testEncryption(passphrase) {
        try {
            const testMessage = 'Hello, this is a test message for E2E encryption!';
            const encrypted = await this.encrypt(testMessage, passphrase);
            const decrypted = await this.decrypt(encrypted, passphrase);
            return testMessage === decrypted;
        } catch (error) {
            console.error('Encryption test failed:', error);
            return false;
        }
    }
}

// Create global instance
window.e2eEncryption = new E2EEncryption();

// Export for modules if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = E2EEncryption;
}
