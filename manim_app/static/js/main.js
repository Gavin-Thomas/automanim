// Main JavaScript for Manim Animation Generator

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const descriptionInput = document.getElementById('description');
    const generateBtn = document.getElementById('generate-btn');
    const initialStatus = document.getElementById('initial-status');
    const loadingStatus = document.getElementById('loading-status');
    const statusText = document.getElementById('status-text');
    const errorMessage = document.getElementById('error-message');
    const videoContainer = document.getElementById('video-container');
    const animationVideo = document.getElementById('animation-video');
    const codeContainer = document.getElementById('code-container');
    const generatedCode = document.getElementById('generated-code');
    const copyCodeBtn = document.getElementById('copy-code-btn');
    
    // Set example text in the description textarea
    window.setExample = function(text) {
        descriptionInput.value = text;
        descriptionInput.focus();
    };
    
    // Copy generated code to clipboard
    copyCodeBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(generatedCode.textContent)
            .then(() => {
                const originalText = copyCodeBtn.textContent;
                copyCodeBtn.textContent = 'Copied!';
                setTimeout(() => {
                    copyCodeBtn.textContent = originalText;
                }, 2000);
            })
            .catch(err => {
                console.error('Failed to copy code: ', err);
            });
    });
    
    // Generate animation when button is clicked
    generateBtn.addEventListener('click', () => {
        const description = descriptionInput.value.trim();
        
        if (!description) {
            showError('Please enter a description for your animation.');
            return;
        }
        
        // Reset UI
        resetUI();
        
        // Show loading state
        initialStatus.style.display = 'none';
        loadingStatus.style.display = 'block';
        generateBtn.disabled = true;
        
        // Update status messages during generation
        let statusMessages = [
            'Analyzing your description...',
            'Generating Manim code...',
            'Running animation...',
            'Rendering video...'
        ];
        
        let messageIndex = 0;
        statusText.textContent = statusMessages[messageIndex];
        
        // Cycle through status messages to show progress
        const messageInterval = setInterval(() => {
            messageIndex = (messageIndex + 1) % statusMessages.length;
            statusText.textContent = statusMessages[messageIndex];
        }, 3000);
        
        // Send request to backend
        fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ description })
        })
        .then(response => {
            clearInterval(messageInterval);
            
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Failed to generate animation');
                });
            }
            return response.json();
        })
        .then(data => {
            // Update status
            statusText.textContent = 'Animation generated successfully!';
            
            // Display video
            animationVideo.src = data.video_url;
            videoContainer.style.display = 'block';
            
            // Add event listener for video loaded
            animationVideo.onloadeddata = function() {
                // Hide loading spinner once video is ready
                loadingStatus.style.display = 'none';
            };
            
            // Display code
            generatedCode.textContent = data.code;
            codeContainer.style.display = 'block';
            
            // Handle video loading error
            animationVideo.onerror = function() {
                showError('Error loading the video. Please try again.');
            };
        })
        .catch(error => {
            clearInterval(messageInterval);
            showError(error.message || 'An error occurred while generating the animation.');
        })
        .finally(() => {
            generateBtn.disabled = false;
        });
    });
    
    // Show error message
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        loadingStatus.style.display = 'none';
    }
    
    // Reset UI elements
    function resetUI() {
        errorMessage.style.display = 'none';
        videoContainer.style.display = 'none';
        codeContainer.style.display = 'none';
        animationVideo.src = '';
        generatedCode.textContent = '';
    }
    
    // Check if the Enter key is pressed in the textarea
    descriptionInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && event.ctrlKey) {
            event.preventDefault();
            generateBtn.click();
        }
    });
    
    // Add placeholder text focus/blur effects
    descriptionInput.addEventListener('focus', function() {
        if (this.placeholder.startsWith('e.g.,')) {
            this.placeholder = 'Describe your animation here...';
        }
    });
    
    descriptionInput.addEventListener('blur', function() {
        if (this.placeholder === 'Describe your animation here...') {
            this.placeholder = 'e.g., \'Create a blue circle and transform it into a red square\' or \'Write the text "Hello, Manim!" and draw a circle below it\'';
        }
    });
});
