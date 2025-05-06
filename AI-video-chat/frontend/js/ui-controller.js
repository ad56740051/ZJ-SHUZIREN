/**
 * UI Controller class
 * Handles all UI updates and user interactions
 */
export class UIController {
    constructor() {
      // Cache DOM elements
      this.elements = {
        enableGoogleSearch: document.getElementById('enableGoogleSearch'),
        allowInterruptions: document.getElementById('allowInterruptions'),
        startAudioBtn: document.getElementById('startAudioBtn'),
        startCameraBtn: document.getElementById('startCameraBtn'),
        startScreenBtn: document.getElementById('startScreenBtn'),
        stopButton: document.getElementById('stopButton'),
        messages: document.getElementById('messages'),
        videoContainer: document.getElementById('videoContainer')
      };
    }
    
    /**
     * Get current configuration from UI elements
     * @returns {Object} Configuration object
     */
    getConfig() {
      return {
        googleSearch: this.elements.enableGoogleSearch.checked,
        allowInterruptions: this.elements.allowInterruptions.checked
      };
    }
    
    /**
     * Update UI elements based on streaming state
     * @param {boolean} isStreaming - Whether streaming is active
     */
    updateUIForStreaming(isStreaming) {
      this.elements.startAudioBtn.disabled = isStreaming;
      this.elements.startCameraBtn.disabled = isStreaming;
      this.elements.startScreenBtn.disabled = isStreaming;
      this.elements.stopButton.disabled = !isStreaming;
    }
    
    /**
     * Show video preview container
     */
    showVideoPreview() {
      this.elements.videoContainer.classList.remove('hidden');
    }
    
    /**
     * Hide video preview container
     */
    hideVideoPreview() {
      this.elements.videoContainer.classList.add('hidden');
    }
    
    /**
     * Append a message to the conversation area
     * @param {string} message - Message text to display
     */
    appendMessage(message) {
      const messageDiv = document.createElement('div');
      messageDiv.className = 'message';
      messageDiv.textContent = message;
      
      this.elements.messages.appendChild(messageDiv);
      this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
    }
    
    /**
     * Show an error message
     * @param {string} errorText - Error message to display
     */
    showError(errorText) {
      const errorDiv = document.createElement('div');
      errorDiv.className = 'message';
      errorDiv.style.borderLeftColor = 'var(--accent-danger)';
      errorDiv.textContent = `Error: ${errorText}`;
      
      this.elements.messages.appendChild(errorDiv);
      this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
      
      console.error(errorText);
    }
}