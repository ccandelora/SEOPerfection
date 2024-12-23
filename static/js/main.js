// Main JavaScript file for Prime Insurance Services website

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href && href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Lazy loading for images
    const images = document.querySelectorAll('img[data-src]');
    const imageOptions = {
        threshold: 0,
        rootMargin: '0px 0px 50px 0px'
    };

    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add('fade-in');
                observer.unobserve(img);
            }
        });
    }, imageOptions);

    images.forEach(img => imageObserver.observe(img));

    // Mobile menu toggle
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            document.querySelector('.navbar-collapse').classList.toggle('show');
        });
    }

    // Add animation class to elements when they come into view
    const animateOnScroll = (entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    };

    const animationObserver = new IntersectionObserver(animateOnScroll, {
        threshold: 0.1
    });

    document.querySelectorAll('.animate-on-scroll').forEach(element => {
        animationObserver.observe(element);
    });

    // Handle quote form submission
    const quoteForm = document.getElementById('quote-form');
    if (quoteForm) {
        quoteForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Add form submission logic here
            console.log('Quote form submitted');
        });
    }

    // Handle contact form submission
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Add form submission logic here
            console.log('Contact form submitted');
        });
    }

    // Add scroll to top button functionality
    const scrollToTopButton = document.getElementById('scroll-to-top');
    if (scrollToTopButton) {
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 100) {
                scrollToTopButton.style.display = 'block';
            } else {
                scrollToTopButton.style.display = 'none';
            }
        });

        scrollToTopButton.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
});
// Chat Widget functionality
let socket;
let chatWidget;
let chatMessages;
let messageInput;

// Initialize chat elements after DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    try {
        socket = io();
        chatWidget = document.getElementById('chatWidget');
        chatMessages = document.getElementById('chatMessages');
        messageInput = document.getElementById('messageInput');
        
        // Socket connection handling
        socket.on('connect', () => {
            console.log('Connected to chat server');
            appendMessage('Connected to chat support.', new Date().toLocaleTimeString(), false);
        });

        socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            appendMessage('Connection error. Please try again later.', new Date().toLocaleTimeString(), false);
        });

        socket.on('response', (data) => {
            console.log('Server response:', data);
        });

        socket.on('new_message', (data) => {
            console.log('Received message:', data);
            appendMessage(data.message, data.timestamp, data.is_user);
        });
        
        // Load chat history for logged-in users
        const profileLink = document.querySelector('.nav-link.text-light[href="/profile"]');
        if (profileLink) {
            loadChatHistory();
        }
    } catch (error) {
        console.error('Error initializing chat:', error);
    }
});

// Chat message handling
function getESTTime() {
    const date = new Date();
    return date.toLocaleTimeString('en-US', {
        timeZone: 'America/New_York',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    }).toLowerCase() + ' est';
}

function formatMessage(message) {
    // Basic markdown-like formatting
    return message
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\[(.*?)\]/g, '<span class="highlight">$1</span>');
}

function appendMessage(message, timestamp, isUser, options = {}) {
    if (!chatMessages) {
        console.error('Chat messages container not found');
        return;
    }
    
    const theme = options.theme || 'modern';
    const type = options.type || '';
    const formattedMessage = formatMessage(message);
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${isUser ? 'user-message' : 'support-message'} theme-${theme} ${type ? 'message-' + type : ''}`;
    messageDiv.style.opacity = '0';  // Start invisible
    messageDiv.innerHTML = `
        <div class="message-content">${formattedMessage}</div>
        <small class="message-time">${typeof timestamp === 'string' ? timestamp : getESTTime()} EST</small>
    `;
    
    chatMessages.appendChild(messageDiv);
    
    // Trigger reflow for animation
    messageDiv.offsetHeight;
    messageDiv.style.opacity = '1';
    
    // Smooth scroll to bottom
    chatMessages.scrollTo({
        top: chatMessages.scrollHeight,
        behavior: 'smooth'
    });
    
    // Add animation end listener
    messageDiv.addEventListener('animationend', () => {
        messageDiv.style.transform = 'none';  // Reset transform after animation
    });
}

// Form submission handling
function sendMessage(event) {
    event.preventDefault();
    const message = messageInput.value.trim();
    
    if (message && socket) {
        socket.emit('send_message', {
            message: message,
            session_id: 'default'
        });
        messageInput.value = '';
    }
}

// Chat widget visibility toggle
function toggleChat() {
    const chatContent = document.querySelector('.chat-content');
    const minimizeIcon = document.querySelector('.chat-minimize i');
    
    if (chatContent && minimizeIcon) {
        const isCollapsed = chatContent.classList.contains('collapsed');
        
        if (isCollapsed) {
            chatContent.classList.remove('collapsed');
            minimizeIcon.className = 'fas fa-minus';
        } else {
            chatContent.classList.add('collapsed');
            minimizeIcon.className = 'fas fa-plus';
        }
    }
}

// Initialize chat in collapsed state
document.addEventListener('DOMContentLoaded', function() {
    const chatContent = document.querySelector('.chat-content');
    const minimizeIcon = document.querySelector('.chat-minimize i');
    
    if (chatContent && minimizeIcon) {
        chatContent.classList.add('collapsed');
        minimizeIcon.className = 'fas fa-plus';
    }
});

// Load chat history when logged in
function loadChatHistory() {
    fetch('/chat/history')
        .then(response => response.json())
        .then(messages => {
            messages.reverse().forEach(msg => {
                appendMessage(msg.content, msg.timestamp, msg.is_user);
            });
        })
        .catch(error => console.error('Error loading chat history:', error));
}

// Load chat history if user is logged in
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.nav-link.text-light[href="/profile"]')) {
        loadChatHistory();
    }
});
