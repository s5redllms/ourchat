document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const appContainer = document.getElementById('appContainer');
    const loginBtn = document.getElementById('loginBtn');
    const registerBtn = document.getElementById('registerBtn');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const loginMessage = document.getElementById('loginMessage');
    const registerMessage = document.getElementById('registerMessage');
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const contactsList = document.getElementById('contactsList');
    const searchInput = document.getElementById('searchInput');
    const logoutBtn = document.getElementById('logoutBtn');
    const authSection = document.getElementById('authSection');
    const contactsSection = document.getElementById('contactsSection');
    const chatSection = document.getElementById('chatSection');
    const adminDashboard = document.getElementById('adminDashboard');
    const currentUser = document.getElementById('currentUser');
    const backToContacts = document.getElementById('backToContacts');
    const backToMain = document.getElementById('backToMain');
    const chatContactName = document.getElementById('chatContactName');
    const chatContactStatus = document.getElementById('chatContactStatus');
    const chatMessages = document.getElementById('chatMessages');
    const messageInput = document.getElementById('messageInput');
    const sendMessageBtn = document.getElementById('sendMessageBtn');
    const adminDashboardLink = document.getElementById('adminDashboardLink');
    const adminDashboardBtn = document.getElementById('adminDashboardBtn');
    
    // Admin elements
    const refreshUsers = document.getElementById('refreshUsers');
    const refreshMessages = document.getElementById('refreshMessages');
    const saveSettings = document.getElementById('saveSettings');
    const usersList = document.getElementById('usersList');
    const messagesList = document.getElementById('messagesList');
    const totalUsers = document.getElementById('totalUsers');
    const totalMessages = document.getElementById('totalMessages');
    const totalContacts = document.getElementById('totalContacts');
    const maintenanceMode = document.getElementById('maintenanceMode');
    const maxUsers = document.getElementById('maxUsers');
    const messageRetention = document.getElementById('messageRetention');
    
    // Navigation elements
    const contactsLink = document.getElementById('contactsLink');
    const addContactLink = document.getElementById('addContactLink');
    const settingsLink = document.getElementById('settingsLink');
    // Commented out elements that are still hidden in HTML
    // const aiAssistantLink = document.getElementById('aiAssistantLink');
    
    // Add Contact elements
    const addContactSection = document.getElementById('addContactSection');
    const addContactForm = document.getElementById('addContactForm');
    const backToContactsFromAdd = document.getElementById('backToContactsFromAdd');
    const cancelAddContact = document.getElementById('cancelAddContact');
    const addContactMessage = document.getElementById('addContactMessage');
    
    // Settings elements
    const settingsSection = document.getElementById('settingsSection');
    const backToContactsFromSettings = document.getElementById('backToContactsFromSettings');
    const userCodeDisplay = document.getElementById('userCodeDisplay');
    const copyUserCode = document.getElementById('copyUserCode');
    const settingsUsername = document.getElementById('settingsUsername');
    const settingsEmail = document.getElementById('settingsEmail');
    const passwordChangeForm = document.getElementById('passwordChangeForm');
    const passwordChangeMessage = document.getElementById('passwordChangeMessage');
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    
    // Profile and media elements
    const profilePictureInput = document.getElementById('profilePictureInput');
    const uploadProfileBtn = document.getElementById('uploadProfileBtn');
    const removeProfileBtn = document.getElementById('removeProfileBtn');
    const profilePicturePreview = document.getElementById('profilePicturePreview');
    const displayNameForm = document.getElementById('displayNameForm');
    const displayNameInput = document.getElementById('displayNameInput');
    const displayNameMessage = document.getElementById('displayNameMessage');
    
    // Media buttons
    const imageBtn = document.getElementById('imageBtn');
    const videoBtn = document.getElementById('videoBtn');
    const fileBtn = document.getElementById('fileBtn');
    const imageInput = document.getElementById('imageInput');
    const videoInput = document.getElementById('videoInput');
    const fileInput = document.getElementById('fileInput');
    
    // Image modal
    const imageModal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    
    // Current chat state
    let currentChatContact = null;
    let currentUserData = null;
    let messagePollingInterval = null;
    let lastMessageCount = 0;
    
    // Cache for encryption keys to avoid repeated API calls
    let encryptionKeyCache = new Map();
    
    // Expose variables for debugging
    window.debugCurrentUser = null;
    window.debugEncryptionCache = encryptionKeyCache;
    
    // Helper function to get encryption key with caching
    async function getEncryptionKey(userId) {
        // Check cache first
        if (encryptionKeyCache.has(userId)) {
            return encryptionKeyCache.get(userId);
        }
        
        try {
            const keyResponse = await fetch(`/api/user/${userId}/encryption-key`);
            const keyData = await keyResponse.json();
            if (!keyResponse.ok || !keyData.encryption_key) {
                console.error('Failed to get encryption key for user:', userId);
                return null;
            }
            
            // Cache the key
            encryptionKeyCache.set(userId, keyData.encryption_key);
            return keyData.encryption_key;
        } catch (error) {
            console.error('Error fetching encryption key:', error);
            return null;
        }
    }
    
    // Check authentication status
    checkAuthStatus();
    
    // Form switching
    loginBtn.addEventListener('click', function() {
        loginBtn.classList.add('active');
        registerBtn.classList.remove('active');
        loginForm.classList.add('active');
        registerForm.classList.remove('active');
        clearMessages();
    });
    
    registerBtn.addEventListener('click', function() {
        registerBtn.classList.add('active');
        loginBtn.classList.remove('active');
        registerForm.classList.add('active');
        loginForm.classList.remove('active');
        clearMessages();
    });
    
    // Login form submission
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;
        
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });
            
            const data = await response.json();
            
            if (data.success) {
                currentUserData = data.user;
                window.debugCurrentUser = data.user; // Expose for debugging
                showMessage(loginMessage, 'Login successful! Redirecting...', 'success');
                setTimeout(() => {
                    showContactsSection();
                    updateAdminDashboardVisibility();
                }, 1000);
            } else {
                showMessage(loginMessage, data.error || 'Login failed', 'error');
            }
        } catch (error) {
            showMessage(loginMessage, 'Network error. Please try again.', 'error');
        }
    });
    
    // Register form submission
    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const username = document.getElementById('registerUsername').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;
        
        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, email, password })
            });
            
            const data = await response.json();
            
            if (data.success) {
                currentUserData = data.user;
                window.debugCurrentUser = data.user; // Expose for debugging
                showMessage(registerMessage, 'Registration successful! Welcome!', 'success');
                setTimeout(() => {
                    showContactsSection();
                    updateAdminDashboardVisibility();
                }, 1000);
            } else {
                showMessage(registerMessage, data.error || 'Registration failed', 'error');
            }
        } catch (error) {
            showMessage(registerMessage, 'Network error. Please try again.', 'error');
        }
    });
    
    // Sidebar toggle functionality
    sidebarToggle.addEventListener('click', function() {
        sidebar.classList.toggle('visible');
        // Also toggle the content margin
        const mainContent = document.getElementById('mainContent');
        mainContent.classList.toggle('sidebar-open');
    });
    
    // Logout functionality
    logoutBtn.addEventListener('click', async function(e) {
        e.preventDefault();
        try {
            await fetch('/api/auth/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            showAuthSection();
        } catch (error) {
            console.error('Logout error:', error);
            showAuthSection(); // Force logout anyway
        }
    });
    
    // Navigation links
    contactsLink.addEventListener('click', function(e) {
        e.preventDefault();
        showContactsSection();
    });
    
    addContactLink.addEventListener('click', function(e) {
        e.preventDefault();
        showAddContactSection();
    });
    
    settingsLink.addEventListener('click', async function(e) {
        e.preventDefault();
        await showSettingsSection();
    });
    
    // Event listeners for remaining hidden menu items are commented out
    /*
    aiAssistantLink.addEventListener('click', function(e) {
        e.preventDefault();
        // This feature is not implemented yet
    });
    */
    
    // Admin Dashboard button
    adminDashboardBtn.addEventListener('click', function(e) {
        e.preventDefault();
        showAdminDashboard();
    });
    
    // Back buttons
    backToContacts.addEventListener('click', function() {
        stopMessagePolling();
        showContactsSection();
    });
    
    backToMain.addEventListener('click', function() {
        stopMessagePolling();
        showContactsSection();
    });
    
    backToContactsFromAdd.addEventListener('click', function() {
        showContactsSection();
    });
    
    cancelAddContact.addEventListener('click', function() {
        showContactsSection();
    });
    
    backToContactsFromSettings.addEventListener('click', function() {
        showContactsSection();
    });
    
    // Copy user code functionality
    copyUserCode.addEventListener('click', function() {
        const userCode = userCodeDisplay.textContent;
        navigator.clipboard.writeText(userCode).then(() => {
            const originalText = this.textContent;
            this.textContent = '✓ Copied!';
            setTimeout(() => {
                this.textContent = originalText;
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy: ', err);
            alert('Failed to copy user code. Please copy manually: ' + userCode);
        });
    });
    
    // Admin action buttons
    refreshUsers.addEventListener('click', loadAllUsers);
    refreshMessages.addEventListener('click', loadAllMessages);
    saveSettings.addEventListener('click', saveAdminSettings);
    
    // Send message functionality
    sendMessageBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Add Contact form submission
    addContactForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        await submitAddContactForm();
    });
    
    // Password change form submission
    passwordChangeForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        await submitPasswordChange();
    });
    
    // Theme toggle button
    themeToggleBtn.addEventListener('click', function() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        toggleDarkMode(newTheme === 'dark');
        updateThemeButton(newTheme);
    });
    
    // Profile picture upload
    uploadProfileBtn.addEventListener('click', function() {
        profilePictureInput.click();
    });
    
    profilePictureInput.addEventListener('change', function(e) {
        if (e.target.files[0]) {
            uploadProfilePicture(e.target.files[0]);
        }
    });
    
    removeProfileBtn.addEventListener('click', removeProfilePicture);
    
    // Display name form
    displayNameForm.addEventListener('submit', function(e) {
        e.preventDefault();
        updateDisplayName();
    });
    
    // Media buttons
    imageBtn.addEventListener('click', function() {
        imageInput.click();
    });
    
    videoBtn.addEventListener('click', function() {
        videoInput.click();
    });
    
    fileBtn.addEventListener('click', function() {
        fileInput.click();
    });
    
    // File inputs
    imageInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            for (let file of e.target.files) {
                uploadMediaFile(file);
            }
            e.target.value = '';
        }
    });
    
    videoInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            for (let file of e.target.files) {
                uploadMediaFile(file);
            }
            e.target.value = '';
        }
    });
    
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            for (let file of e.target.files) {
                uploadMediaFile(file);
            }
            e.target.value = '';
        }
    });
    
    // Image modal
    imageModal.addEventListener('click', function() {
        imageModal.style.display = 'none';
    });
    
    // Load contacts from backend
    async function loadContacts() {
        try {
            contactsList.innerHTML = '<div class="loading">Loading contacts...</div>';
            
            const response = await fetch('/api/contacts');
            const contacts = await response.json();
            
            displayContacts(contacts);
        } catch (error) {
            console.error('Error loading contacts:', error);
            contactsList.innerHTML = '<div class="loading">Error loading contacts</div>';
        }
    }
    
    // Display contacts in the UI
    function displayContacts(contacts) {
        if (contacts.length === 0) {
            contactsList.innerHTML = '<div class="loading">No contacts found</div>';
            return;
        }
        
        contactsList.innerHTML = contacts.map(contact => {
            const displayName = contact.display_name || contact.name;
            const avatarContent = contact.profile_picture 
                ? `<img src="/uploads/${contact.profile_picture}" alt="${displayName}">`
                : getInitials(displayName);
                
            return `
                <div class="contact-item" data-contact-id="${contact.id}" data-contact-record-id="${contact.contact_id}" data-contact-name="${contact.name}" data-contact-display-name="${displayName}" data-contact-status="${contact.status}" data-contact-profile="${contact.profile_picture || ''}">
                    <div class="contact-avatar">${avatarContent}</div>
                    <div class="contact-info">
                        <div class="contact-name">${displayName}</div>
                        <div class="contact-status">${contact.status}</div>
                    </div>
                    <div class="contact-actions">
                        <button class="delete-contact-btn" data-contact-record-id="${contact.contact_id}" title="Delete Contact">🗑️</button>
                    </div>
                </div>
            `;
        }).join('');
        
        // Add click functionality to contact items
        document.querySelectorAll('.contact-item').forEach(item => {
            item.addEventListener('click', function(e) {
                // Don't open chat if delete button was clicked
                if (e.target.classList.contains('delete-contact-btn')) {
                    return;
                }
                
                const contactId = parseInt(this.getAttribute('data-contact-id'));
                const contactName = this.getAttribute('data-contact-name');
                const contactDisplayName = this.getAttribute('data-contact-display-name');
                const contactStatus = this.getAttribute('data-contact-status');
                const contactProfile = this.getAttribute('data-contact-profile');
                openChat(contactId, contactDisplayName, contactStatus, contactProfile);
            });
        });
        
        // Add click functionality to delete buttons
        document.querySelectorAll('.delete-contact-btn').forEach(btn => {
            btn.addEventListener('click', async function(e) {
                e.stopPropagation(); // Prevent opening chat
                
                const contactRecordId = this.getAttribute('data-contact-record-id');
                const contactName = this.closest('.contact-item').getAttribute('data-contact-name');
                
                if (confirm(`Are you sure you want to delete ${contactName} from your contacts?`)) {
                    await deleteContact(contactRecordId);
                }
            });
        });
    }
    
    // Open chat with a contact
    function openChat(contactId, contactName, contactStatus, contactProfile) {
        currentChatContact = {
            id: contactId,
            name: contactName,
            status: contactStatus,
            profile: contactProfile
        };
        
        // Update chat header
        chatContactName.textContent = contactName;
        chatContactStatus.textContent = contactStatus;
        
        // Update chat header avatar
        const chatAvatar = document.querySelector('.chat-contact-info .contact-avatar');
        if (chatAvatar) {
            chatAvatar.innerHTML = contactProfile 
                ? `<img src="/uploads/${contactProfile}" alt="${contactName}">`
                : getInitials(contactName);
        }
        
        // Show chat section
        contactsSection.style.display = 'none';
        chatSection.style.display = 'flex';
        adminDashboard.style.display = 'none';
        addContactSection.style.display = 'none';
        settingsSection.style.display = 'none';
        
        // Load chat messages and start polling
        loadChatMessages(contactId);
        startMessagePolling();
    }
    
    
    // Display messages in the chat
    async function displayMessages(messages) {
        if (messages.length === 0) {
            chatMessages.innerHTML = '<div class="no-messages">No messages yet. Start a conversation!</div>';
            lastMessageCount = 0;
            return;
        }
        
        // Use currentUserData for consistent user ID access
        const currentUserId = currentUserData ? currentUserData.id : null;
        
        if (!currentUserId) {
            console.error('Current user data not available');
            return;
        }
        
        // Check if we should scroll to bottom (only if user is at bottom already or new messages arrived)
        const shouldScrollToBottom = chatMessages.scrollTop + chatMessages.clientHeight >= chatMessages.scrollHeight - 5 || messages.length > lastMessageCount;
        
        const messageElements = await Promise.all(messages.map(async msg => {
            const isSent = msg.sender_id === currentUserId;
            const messageClass = isSent ? 'sent' : 'received';
            const timestamp = formatTime(msg.timestamp);
            
            let messageContent = '';
            
            if (msg.message_type === 'text') {
                // Decrypt message content if it's encrypted
                let displayContent = msg.content;
                if (currentUserData && currentUserData.encryption_key && window.e2eEncryption.isEncrypted(msg.content)) {
                    console.log('🔐 Processing encrypted message:', {
                        messageId: msg.id,
                        senderId: msg.sender_id,
                        receiverId: msg.receiver_id,
                        currentUserId: currentUserId,
                        isSentByMe: msg.sender_id === currentUserId,
                        contentPreview: msg.content.substring(0, 50) + '...',
                        myEncryptionKey: currentUserData.encryption_key.substring(0, 20) + '...',
                        isDetectedAsEncrypted: window.e2eEncryption.isEncrypted(msg.content)
                    });
                    
                    try {
                        // For received messages, they were encrypted with our key
                        // For sent messages, we need to get the receiver's key to decrypt
                        let decryptionKey;
                        
                        if (msg.sender_id === currentUserId) {
                            // This is a message we sent - it was encrypted with receiver's key
                            console.log('📤 Decrypting sent message, fetching receiver key for user:', msg.receiver_id);
                            decryptionKey = await getEncryptionKey(msg.receiver_id);
                            if (!decryptionKey) {
                                throw new Error('Could not get receiver key for sent message');
                            }
                            console.log('🔑 Using receiver key for sent message:', decryptionKey.substring(0, 20) + '...');
                        } else {
                            // This is a message we received - it was encrypted with our key
                            console.log('📥 Decrypting received message with our key');
                            decryptionKey = currentUserData.encryption_key;
                            console.log('🔑 Using our key for received message:', decryptionKey.substring(0, 20) + '...');
                        }
                        
                        console.log('🔓 Attempting decryption...');
                        displayContent = await window.e2eEncryption.decrypt(msg.content, decryptionKey);
                        console.log('✅ Decryption successful:', displayContent);
                    } catch (decryptError) {
                        console.error('❌ Decryption failed for message:', msg.id, decryptError);
                        console.error('Full error details:', {
                            error: decryptError.message,
                            stack: decryptError.stack,
                            messageContent: msg.content,
                            decryptionKey: decryptionKey ? decryptionKey.substring(0, 20) + '...' : 'null'
                        });
                        displayContent = '[🔒 Decryption Failed: ' + decryptError.message + ']';
                    }
                } else {
                    console.log('ℹ️ Message not encrypted or missing requirements:', {
                        hasCurrentUser: !!currentUserData,
                        hasEncryptionKey: !!(currentUserData && currentUserData.encryption_key),
                        isEncrypted: window.e2eEncryption.isEncrypted(msg.content),
                        contentPreview: msg.content.substring(0, 50)
                    });
                    
                    // Fallback: try to decrypt any base64-looking content
                    if (currentUserData && currentUserData.encryption_key && 
                        msg.content && /^[A-Za-z0-9+/]+=*$/.test(msg.content) && msg.content.length > 40) {
                        console.log('🔄 Attempting fallback decryption for base64-like content:', {
                            messageId: msg.id,
                            contentLength: msg.content.length,
                            isSentByMe: msg.sender_id === currentUserId
                        });
                        try {
                            let fallbackDecrypted;
                            if (msg.sender_id === currentUserId) {
                                // Sent message - try receiver's key
                                console.log('🔑 Getting receiver key for sent message, receiver_id:', msg.receiver_id);
                                const receiverKey = await getEncryptionKey(msg.receiver_id);
                                console.log('🔑 Got receiver key:', receiverKey.substring(0, 20) + '...');
                                fallbackDecrypted = await window.e2eEncryption.decrypt(msg.content, receiverKey);
                            } else {
                                // Received message - try our key
                                console.log('🔑 Using our key for received message');
                                fallbackDecrypted = await window.e2eEncryption.decrypt(msg.content, currentUserData.encryption_key);
                            }
                            console.log('✅ Fallback decryption successful:', fallbackDecrypted);
                            displayContent = fallbackDecrypted;
                        } catch (fallbackError) {
                            console.log('❌ Fallback decryption failed:', fallbackError.message);
                            console.log('❌ Full error:', fallbackError);
                        }
                    } else {
                        console.log('🙅 Skipping fallback decryption:', {
                            hasUser: !!currentUserData,
                            hasKey: !!(currentUserData && currentUserData.encryption_key),
                            hasContent: !!msg.content,
                            isBase64: /^[A-Za-z0-9+/]+=*$/.test(msg.content || ''),
                            contentLength: msg.content ? msg.content.length : 0
                        });
                    }
                }
                messageContent = `<div class="message-content">${escapeHtml(displayContent)}</div>`;
            } else if (msg.message_type === 'image' || msg.message_type === 'gif') {
                messageContent = `
                    <div class="message-content">
                        <div class="media-message">
                            <img src="/uploads/${msg.file_path}" alt="${escapeHtml(msg.file_name)}" onclick="showImageModal('/uploads/${msg.file_path}')">
                        </div>
                        ${msg.content ? `<div style="margin-top: 8px;">${escapeHtml(msg.content)}</div>` : ''}
                    </div>
                `;
            } else if (msg.message_type === 'video') {
                messageContent = `
                    <div class="message-content">
                        <div class="media-message">
                            <video controls>
                                <source src="/uploads/${msg.file_path}" type="video/mp4">
                                Your browser does not support the video tag.
                            </video>
                        </div>
                        ${msg.content ? `<div style="margin-top: 8px;">${escapeHtml(msg.content)}</div>` : ''}
                    </div>
                `;
            } else if (msg.message_type === 'file') {
                messageContent = `
                    <div class="message-content">
                        <div class="file-message" onclick="downloadFile('/uploads/${msg.file_path}', '${escapeHtml(msg.file_name)}')">
                            <div class="file-icon">📄</div>
                            <div class="file-info">
                                <div class="file-name">${escapeHtml(msg.file_name)}</div>
                                <div class="file-size">${formatFileSize(msg.file_size)}</div>
                            </div>
                        </div>
                        ${msg.content ? `<div style="margin-top: 8px;">${escapeHtml(msg.content)}</div>` : ''}
                    </div>
                `;
            }
            
            return `
                <div class="message ${messageClass}">
                    ${messageContent}
                    <div class="message-time">${timestamp}</div>
                </div>
            `;
        }));
        
        chatMessages.innerHTML = messageElements.join('');
        
        // Update message count
        lastMessageCount = messages.length;
        
        // Scroll to bottom if needed
        if (shouldScrollToBottom) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    // Send message
    async function sendMessage() {
        const messageText = messageInput.value.trim();
        if (!messageText || !currentChatContact || !currentUserData) return;
        
        try {
            // Get receiver's encryption key for proper E2E encryption
            console.log('📤 Sending message to user:', currentChatContact.id);
            let receiverKey = await getEncryptionKey(currentChatContact.id);
            if (!receiverKey) {
                alert('Failed to get encryption key. Please try again.');
                return;
            }
            console.log('🔑 Got receiver key:', receiverKey.substring(0, 20) + '...');
            
            // Encrypt the message with receiver's key
            console.log('🔐 Encrypting message:', messageText);
            let encryptedContent;
            try {
                encryptedContent = await window.e2eEncryption.encrypt(messageText, receiverKey);
                console.log('✅ Encryption successful, encrypted length:', encryptedContent.length);
            } catch (encryptError) {
                console.error('❌ Encryption failed:', encryptError);
                alert('Failed to encrypt message. Please check your connection.');
                return;
            }
            
            const response = await fetch('/api/messages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    receiver_id: currentChatContact.id,
                    content: encryptedContent  // Send encrypted content
                })
            });
            
            const message = await response.json();
            
            if (response.ok) {
                // Add message to chat immediately for better UX (show decrypted version)
                const messageElement = document.createElement('div');
                messageElement.className = 'message sent';
                messageElement.innerHTML = `
                    <div class="message-content">${escapeHtml(messageText)}</div>
                    <div class="message-time">${formatTime(message.timestamp)}</div>
                `;
                
                chatMessages.appendChild(messageElement);
                
                // Clear input and scroll to bottom
                messageInput.value = '';
                chatMessages.scrollTop = chatMessages.scrollHeight;
            } else {
                alert('Failed to send message: ' + message.error);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            alert('Failed to send message. Please try again.');
        }
    }
    
    // Format timestamp
    function formatTime(timestamp) {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return date.getHours().toString().padStart(2, '0') + ':' + 
               date.getMinutes().toString().padStart(2, '0');
    }
    
    // Escape HTML to prevent XSS
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Search functionality
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const contactItems = document.querySelectorAll('.contact-item');
        
        contactItems.forEach(item => {
            const contactName = item.querySelector('.contact-name').textContent.toLowerCase();
            if (contactName.includes(searchTerm)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    });
    
    // Admin Dashboard Functions
    async function showAdminDashboard() {
        // Load admin stats
        await loadAdminStats();
        
        // Load all users
        await loadAllUsers();
        
        // Load all messages
        await loadAllMessages();
        
        // Load admin settings
        await loadAdminSettings();
        
        authSection.style.display = 'none';
        contactsSection.style.display = 'none';
        chatSection.style.display = 'none';
        addContactSection.style.display = 'none';
        settingsSection.style.display = 'none';
        adminDashboard.style.display = 'block';
        sidebarToggle.style.display = 'block';
        sidebar.classList.remove('visible');
    }
    
    async function loadAdminStats() {
        try {
            const response = await fetch('/api/admin/stats');
            const stats = await response.json();
            
            if (response.ok) {
                totalUsers.textContent = stats.total_users;
                totalMessages.textContent = stats.total_messages;
                totalContacts.textContent = stats.total_contacts;
            } else {
                alert('Failed to load admin stats: ' + stats.error);
            }
        } catch (error) {
            console.error('Error loading admin stats:', error);
            alert('Failed to load admin stats. Please try again.');
        }
    }
    
    async function loadAllUsers() {
        try {
            usersList.innerHTML = '<div class="loading">Loading users...</div>';
            
            const response = await fetch('/api/admin/users');
            const users = await response.json();
            
            if (response.ok) {
                displayUsers(users);
            } else {
                usersList.innerHTML = '<div class="loading">Error: ' + users.error + '</div>';
            }
        } catch (error) {
            console.error('Error loading users:', error);
            usersList.innerHTML = '<div class="loading">Error loading users</div>';
        }
    }
    
    function displayUsers(users) {
        if (users.length === 0) {
            usersList.innerHTML = '<div class="loading">No users found</div>';
            return;
        }
        
        usersList.innerHTML = users.map(user => `
            <div class="user-item">
                <div class="user-info">
                    <div class="user-details">
                        <div class="user-name">${escapeHtml(user.username)}</div>
                        <div class="user-email">${escapeHtml(user.email)}</div>
                    </div>
                    <div class="user-meta">
                        ID: ${user.id}
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    async function loadAllMessages() {
        try {
            messagesList.innerHTML = '<div class="loading">Loading messages...</div>';
            
            const response = await fetch('/api/admin/messages');
            const messages = await response.json();
            
            if (response.ok) {
                displayMessagesAdmin(messages);
            } else {
                messagesList.innerHTML = '<div class="loading">Error: ' + messages.error + '</div>';
            }
        } catch (error) {
            console.error('Error loading messages:', error);
            messagesList.innerHTML = '<div class="loading">Error loading messages</div>';
        }
    }
    
    function displayMessagesAdmin(messages) {
        if (messages.length === 0) {
            messagesList.innerHTML = '<div class="loading">No messages found</div>';
            return;
        }
        
        messagesList.innerHTML = messages.map(msg => {
            const timestamp = msg.timestamp ? new Date(msg.timestamp).toLocaleString() : 'Unknown';
            const contentPreview = msg.content.length > 50 ? msg.content.substring(0, 50) + '...' : msg.content;
            
            return `
                <div class="message-item">
                    <div class="message-info">
                        <div class="message-details">
                            <div class="message-content-preview">${escapeHtml(contentPreview)}</div>
                            <div class="message-meta">
                                From: ${escapeHtml(msg.sender_username)} | 
                                To: User ${msg.receiver_id} | 
                                ${timestamp}
                            </div>
                        </div>
                        <div class="message-id">
                            ID: ${msg.id}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    async function loadAdminSettings() {
        try {
            const response = await fetch('/api/admin/settings');
            const settings = await response.json();
            
            if (response.ok) {
                maintenanceMode.value = settings.maintenance_mode || 'off';
                maxUsers.value = settings.max_users || 1000;
                messageRetention.value = settings.message_retention_days || 30;
            }
        } catch (error) {
            console.error('Error loading admin settings:', error);
        }
    }
    
    async function saveAdminSettings() {
        try {
            const settings = {
                maintenance_mode: maintenanceMode.value,
                max_users: parseInt(maxUsers.value),
                message_retention_days: parseInt(messageRetention.value)
            };
            
            const response = await fetch('/api/admin/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settings)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                alert('Settings saved successfully!');
            } else {
                alert('Failed to save settings: ' + result.error);
            }
        } catch (error) {
            console.error('Error saving admin settings:', error);
            alert('Failed to save settings. Please try again.');
        }
    }
    
    // Utility functions
    function showMessage(element, message, type) {
        element.textContent = message;
        element.className = 'form-message ' + type;
    }
    
    function clearMessages() {
        loginMessage.textContent = '';
        registerMessage.textContent = '';
        loginMessage.className = 'form-message';
        registerMessage.className = 'form-message';
    }
    
    async function checkAuthStatus() {
        try {
            const response = await fetch('/api/auth/check');
            const data = await response.json();
            
            if (data.authenticated) {
                currentUserData = data.user;
                window.debugCurrentUser = data.user; // Expose for debugging
                sessionStorage.setItem('userId', data.user.id);
                showContactsSection();
                loadContacts(); // Load contacts for authenticated user
                currentUser.textContent = `Hello, ${data.user.username}`;
                currentUser.style.display = 'block';
                updateAdminDashboardVisibility();
            } else {
                showAuthSection();
            }
        } catch (error) {
            console.error('Auth check error:', error);
            showAuthSection();
        }
    }
    
    function updateAdminDashboardVisibility() {
        if (currentUserData && currentUserData.is_admin) {
            adminDashboardLink.style.display = 'block';
        } else {
            adminDashboardLink.style.display = 'none';
        }
    }
    
    function showAuthSection() {
        authSection.style.display = 'block';
        contactsSection.style.display = 'none';
        chatSection.style.display = 'none';
        adminDashboard.style.display = 'none';
        addContactSection.style.display = 'none';
        settingsSection.style.display = 'none';
        sidebarToggle.style.display = 'none'; // Hide sidebar toggle for login screen
        currentUser.style.display = 'none'; // Hide current user
        sidebar.classList.remove('visible'); // Hide sidebar
        document.getElementById('mainContent').classList.remove('sidebar-open'); // Reset content margin
        adminDashboardLink.style.display = 'none'; // Hide admin dashboard link
        
        // Stop message polling
        stopMessagePolling();
        
        // Clear encryption cache
        if (window.e2eEncryption) {
            window.e2eEncryption.clearCache();
        }
        
        // Clear encryption key cache
        encryptionKeyCache.clear();
        
        // Clear user session data
        currentUserData = null;
        currentChatContact = null;
        sessionStorage.removeItem('userId');
        
        // Clear forms
        document.getElementById('loginUsername').value = '';
        document.getElementById('loginPassword').value = '';
        document.getElementById('registerUsername').value = '';
        document.getElementById('registerEmail').value = '';
        document.getElementById('registerPassword').value = '';
        clearMessages();
    }
    
    function showContactsSection() {
        authSection.style.display = 'none';
        contactsSection.style.display = 'block';
        chatSection.style.display = 'none';
        adminDashboard.style.display = 'none';
        addContactSection.style.display = 'none';
        settingsSection.style.display = 'none';
        sidebarToggle.style.display = 'block'; // Show sidebar toggle for logged-in users
        sidebar.classList.remove('visible'); // Hide sidebar by default, but available
        document.getElementById('mainContent').classList.remove('sidebar-open'); // Reset content margin
        // Load contacts
        loadContacts();
    }
    
    function showAddContactSection() {
        authSection.style.display = 'none';
        contactsSection.style.display = 'none';
        chatSection.style.display = 'none';
        adminDashboard.style.display = 'none';
        addContactSection.style.display = 'block';
        settingsSection.style.display = 'none';
        sidebarToggle.style.display = 'block';
        sidebar.classList.remove('visible');
        document.getElementById('mainContent').classList.remove('sidebar-open'); // Reset content margin
        
        // Clear form
        clearAddContactForm();
    }
    
    async function showSettingsSection() {
        authSection.style.display = 'none';
        contactsSection.style.display = 'none';
        chatSection.style.display = 'none';
        adminDashboard.style.display = 'none';
        addContactSection.style.display = 'none';
        settingsSection.style.display = 'block';
        sidebarToggle.style.display = 'block';
        sidebar.classList.remove('visible');
        document.getElementById('mainContent').classList.remove('sidebar-open'); // Reset content margin
        
        // Load user settings (now async to fetch fresh data)
        await loadUserSettings();
    }
    
    function clearAddContactForm() {
        document.getElementById('contactDisplayName').value = '';
        document.getElementById('contactUserCode').value = '';
        addContactMessage.textContent = '';
        addContactMessage.className = 'form-message';
    }
    
    async function submitAddContactForm() {
        const displayName = document.getElementById('contactDisplayName').value.trim();
        const userCode = document.getElementById('contactUserCode').value.trim();
        
        if (!displayName || !userCode) {
            showMessage(addContactMessage, 'Both display name and user code are required', 'error');
            return;
        }
        
        if (userCode.length !== 6 || !userCode.match(/^\d{6}$/)) {
            showMessage(addContactMessage, 'User code must be exactly 6 digits', 'error');
            return;
        }
        
        try {
            const response = await fetch('/api/contacts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    display_name: displayName,
                    user_code: userCode
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showMessage(addContactMessage, 'Contact added successfully!', 'success');
                setTimeout(() => {
                    showContactsSection();
                }, 1500);
            } else {
                showMessage(addContactMessage, data.error || 'Failed to add contact', 'error');
            }
        } catch (error) {
            console.error('Error adding contact:', error);
            showMessage(addContactMessage, 'Network error. Please try again.', 'error');
        }
    }
    
    async function deleteContact(contactRecordId) {
        try {
            const response = await fetch(`/api/contacts/${contactRecordId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Reload contacts to reflect the deletion
                loadContacts();
            } else {
                alert('Failed to delete contact: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error deleting contact:', error);
            alert('Failed to delete contact. Please try again.');
        }
    }
    
    // Settings functions
    async function loadUserSettings() {
        try {
            // Always fetch fresh user data from server
            const response = await fetch('/api/auth/check');
            const data = await response.json();
            
            if (data.authenticated && data.user) {
                // Update currentUserData with fresh data
                currentUserData = data.user;
                
                // Display user information
                userCodeDisplay.textContent = currentUserData.user_code || '------';
                settingsUsername.textContent = currentUserData.username || '-';
                settingsEmail.textContent = currentUserData.email || '-';
                
                // Load profile picture
                updateProfilePictureDisplay();
                
                // Load display name
                displayNameInput.value = currentUserData.display_name || '';
                
                // Load dark mode preference
                const isDarkMode = localStorage.getItem('darkMode') === 'true';
                const theme = isDarkMode ? 'dark' : 'light';
                document.documentElement.setAttribute('data-theme', theme);
                updateThemeButton(theme);
                
                // Clear password form
                passwordChangeForm.reset();
                passwordChangeMessage.textContent = '';
                passwordChangeMessage.className = 'form-message';
            } else {
                // Not authenticated, redirect to login
                showAuthSection();
            }
        } catch (error) {
            console.error('Error loading user settings:', error);
            showAuthSection();
        }
    }
    
    async function submitPasswordChange() {
        const currentPassword = document.getElementById('currentPassword').value;
        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        // Validate inputs
        if (!currentPassword || !newPassword || !confirmPassword) {
            showMessage(passwordChangeMessage, 'All fields are required', 'error');
            return;
        }
        
        if (newPassword !== confirmPassword) {
            showMessage(passwordChangeMessage, 'New passwords do not match', 'error');
            return;
        }
        
        if (newPassword.length < 6) {
            showMessage(passwordChangeMessage, 'New password must be at least 6 characters', 'error');
            return;
        }
        
        try {
            const response = await fetch('/api/user/change-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showMessage(passwordChangeMessage, 'Password changed successfully!', 'success');
                passwordChangeForm.reset();
            } else {
                showMessage(passwordChangeMessage, data.error || 'Failed to change password', 'error');
            }
        } catch (error) {
            console.error('Error changing password:', error);
            showMessage(passwordChangeMessage, 'Network error. Please try again.', 'error');
        }
    }
    
    // Dark Mode Functions
    function toggleDarkMode(isDark) {
        document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
        localStorage.setItem('darkMode', isDark);
    }
    
    function initializeDarkMode() {
        const isDarkMode = localStorage.getItem('darkMode') === 'true';
        const theme = isDarkMode ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', theme);
        updateThemeButton(theme);
    }
    
    function updateThemeButton(theme) {
        if (!themeToggleBtn) return;
        
        const themeIcon = themeToggleBtn.querySelector('.theme-icon');
        const themeText = themeToggleBtn.querySelector('.theme-text');
        
        if (theme === 'dark') {
            themeIcon.textContent = '☀️';
            themeText.textContent = 'Light Mode';
        } else {
            themeIcon.textContent = '🌙';
            themeText.textContent = 'Dark Mode';
        }
    }
    
    // Real-time messaging functions
    function startMessagePolling() {
        // Clear any existing polling
        stopMessagePolling();
        
        // Start polling every 2 seconds
        messagePollingInterval = setInterval(() => {
            if (currentChatContact) {
                loadChatMessages(currentChatContact.id, true); // true = silent refresh
            }
        }, 2000);
    }
    
    function stopMessagePolling() {
        if (messagePollingInterval) {
            clearInterval(messagePollingInterval);
            messagePollingInterval = null;
        }
    }
    
    // Update loadChatMessages to support silent refresh
    async function loadChatMessages(contactId, silent = false) {
        try {
            if (!silent) {
                chatMessages.innerHTML = '<div class="loading">Loading messages...</div>';
            }
            
            const response = await fetch(`/api/messages/${contactId}`);
            const messages = await response.json();
            
            displayMessages(messages);
        } catch (error) {
            console.error('Error loading messages:', error);
            if (!silent) {
                chatMessages.innerHTML = '<div class="loading">Error loading messages</div>';
            }
        }
    }
    
    // Profile Picture Functions
    function updateProfilePictureDisplay() {
        if (currentUserData && currentUserData.profile_picture) {
            profilePicturePreview.innerHTML = `<img src="/uploads/${currentUserData.profile_picture}" alt="Profile Picture">`;
            removeProfileBtn.style.display = 'block';
        } else {
            // Show initials avatar when no profile picture
            const initials = getInitials(currentUserData?.display_name || currentUserData?.username || 'U');
            profilePicturePreview.innerHTML = `<div class="profile-avatar">${initials}</div>`;
            removeProfileBtn.style.display = 'none';
        }
    }
    
    async function uploadProfilePicture(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/api/user/profile-picture', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                currentUserData.profile_picture = data.profile_picture;
                updateProfilePictureDisplay();
                showMessage({ textContent: '', className: 'form-message' }, 'Profile picture updated successfully!', 'success');
            } else {
                alert('Failed to upload profile picture: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error uploading profile picture:', error);
            alert('Failed to upload profile picture. Please try again.');
        }
    }
    
    async function removeProfilePicture() {
        // This would require a separate API endpoint to remove the profile picture
        // For now, we'll just hide the remove button functionality
        alert('Remove profile picture functionality would be implemented here.');
    }
    
    async function updateDisplayName() {
        const displayName = displayNameInput.value.trim();
        
        if (!displayName) {
            showMessage(displayNameMessage, 'Display name is required', 'error');
            return;
        }
        
        try {
            const response = await fetch('/api/user/display-name', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ display_name: displayName })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                currentUserData.display_name = data.display_name;
                updateProfilePictureDisplay();
                showMessage(displayNameMessage, 'Display name updated successfully!', 'success');
            } else {
                showMessage(displayNameMessage, data.error || 'Failed to update display name', 'error');
            }
        } catch (error) {
            console.error('Error updating display name:', error);
            showMessage(displayNameMessage, 'Network error. Please try again.', 'error');
        }
    }
    
    // Media Upload Functions
    async function uploadMediaFile(file) {
        if (!currentChatContact) {
            alert('Please select a contact first');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('receiver_id', currentChatContact.id);
        
        try {
            const response = await fetch('/api/upload/media', {
                method: 'POST',
                body: formData
            });
            
            const message = await response.json();
            
            if (response.ok) {
                // Refresh messages to show the new media
                loadChatMessages(currentChatContact.id, true);
            } else {
                alert('Failed to send file: ' + (message.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error uploading file:', error);
            alert('Failed to send file. Please try again.');
        }
    }
    
    // Utility Functions
    function getInitials(name) {
        if (!name) return 'U';
        return name.split(' ')
            .map(word => word.charAt(0).toUpperCase())
            .slice(0, 2)
            .join('');
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    function showImageModal(imageSrc) {
        modalImage.src = imageSrc;
        imageModal.style.display = 'flex';
    }
    
    function downloadFile(filePath, fileName) {
        const link = document.createElement('a');
        link.href = filePath;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    // Make functions available globally for onclick handlers
    window.showImageModal = showImageModal;
    window.downloadFile = downloadFile;
    
    // Initialize dark mode on page load
    initializeDarkMode();
});
