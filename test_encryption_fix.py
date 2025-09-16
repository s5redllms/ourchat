#!/usr/bin/env python3
"""
Test script to verify E2E encryption is working properly.
This will help identify issues with the encryption implementation.
"""

import os
import sys
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_encryption_in_browser():
    """Test the encryption functionality directly in browser"""
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("http://localhost:5000")
        
        # Test the encryption functions in browser console
        test_script = """
        // Test encryption/decryption functionality
        async function testE2EEncryption() {
            const testMessage = "Hello, this is a test message for E2E encryption!";
            const testKey = "alpha-bravo-charlie-1234";
            
            console.log("Testing E2E encryption...");
            console.log("Test message:", testMessage);
            console.log("Test key:", testKey);
            
            try {
                // Test encryption
                const encrypted = await window.e2eEncryption.encrypt(testMessage, testKey);
                console.log("Encrypted:", encrypted);
                console.log("Encryption successful:", encrypted ? "✓" : "✗");
                
                // Test decryption
                const decrypted = await window.e2eEncryption.decrypt(encrypted, testKey);
                console.log("Decrypted:", decrypted);
                console.log("Decryption successful:", decrypted === testMessage ? "✓" : "✗");
                
                // Test with wrong key
                try {
                    const wrongDecrypt = await window.e2eEncryption.decrypt(encrypted, "wrong-key-test-9999");
                    console.log("Decryption with wrong key should fail but got:", wrongDecrypt);
                } catch (error) {
                    console.log("Decryption with wrong key correctly failed:", error.message);
                }
                
                return {
                    encrypted: encrypted,
                    decrypted: decrypted,
                    success: decrypted === testMessage
                };
            } catch (error) {
                console.error("Encryption test failed:", error);
                return { success: false, error: error.message };
            }
        }
        
        // Run the test and return results
        return testE2EEncryption();
        """
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Execute the test
        result = driver.execute_script(f"return {test_script}")
        
        print("Encryption Test Results:")
        print(f"Success: {result.get('success', False)}")
        if result.get('encrypted'):
            print(f"Encrypted length: {len(result['encrypted'])} chars")
        if result.get('decrypted'):
            print(f"Decrypted: {result['decrypted']}")
        if result.get('error'):
            print(f"Error: {result['error']}")
            
        return result.get('success', False)
        
    except Exception as e:
        print(f"Browser test failed: {e}")
        return False
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    print("Testing E2E encryption functionality...")
    print("Make sure the Flask app is running on http://localhost:5000")
    
    # Check if Flask app is running
    try:
        import requests
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code != 200:
            print("Flask app is not responding properly")
            sys.exit(1)
    except:
        print("Flask app is not running. Please start it first.")
        sys.exit(1)
    
    success = test_encryption_in_browser()
    if success:
        print("✓ Encryption test passed!")
        sys.exit(0)
    else:
        print("✗ Encryption test failed!")
        sys.exit(1)
