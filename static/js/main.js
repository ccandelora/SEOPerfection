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
    socket = io();
    chatWidget = document.getElementById('chatWidget');
    chatMessages = document.getElementById('chatMessages');
    messageInput = document.getElementById('messageInput');
    
    // Socket connection handling
    socket.on('connect', () => {
        console.log('Connected to chat server');
    });

    socket.on('response', (data) => {
        console.log('Server response:', data);
    });

    socket.on('new_message', (data) => {
        console.log('Received message:', data);
        appendMessage(data.message, data.timestamp, data.is_user);
    });
    
    if (document.querySelector('.nav-link.text-light[href="/profile"]')) {
        loadChatHistory();
    }
});

// Chat message handling
function appendMessage(message, timestamp, isUser) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${isUser ? 'user-message' : 'support-message'}`;
    messageDiv.innerHTML = `
        <div class="message-content">${message}</div>
        <small class="message-time">${timestamp}</small>
    `;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Form submission handling
function sendMessage(event) {
    event.preventDefault();
    const message = messageInput.value.trim();
    
    if (message) {
        socket.emit('send_message', {
            message: message,
            session_id: 'default'
        });
        messageInput.value = '';
    }
}

// Chat widget visibility toggle
function toggleChat() {
    const messagesDiv = document.getElementById('chatMessages');
    const inputDiv = document.querySelector('.chat-input');
    
    if (messagesDiv.style.display === 'none') {
        messagesDiv.style.display = 'flex';
        inputDiv.style.display = 'block';
    } else {
        messagesDiv.style.display = 'none';
        inputDiv.style.display = 'none';
    }
}

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
