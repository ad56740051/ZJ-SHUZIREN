/**
 * Main application entry point
 * Initializes all components and sets up event listeners
 */

import { AudioManager } from './audio-manager.js';
import { VideoManager } from './video-manager.js';
import { WebSocketClient } from './websocket-client.js';
import { UIController } from './ui-controller.js';

class GeminiApp {
  constructor() {
    // Initialize managers
    this.audioManager = new AudioManager();
    this.videoManager = new VideoManager();
    this.webSocketClient = new WebSocketClient();
    this.uiController = new UIController();
    
    // App state
    this.isStreaming = false;
    this.currentMode = null; // 'audio', 'camera', or 'screen'
    this.heartbeatInterval = null;
    
    // Initialize
    this.initEventListeners();
  }
  
  /**
   * Set up event listeners for UI buttons
   */
  initEventListeners() {
    try {
      // Button references
      this.startAudioBtn = document.getElementById('startAudioBtn');
      this.startCameraBtn = document.getElementById('startCameraBtn');
      this.startScreenBtn = document.getElementById('startScreenBtn');
      this.stopButton = document.getElementById('stopButton');
      
      if (!this.startAudioBtn || !this.startCameraBtn || !this.startScreenBtn || !this.stopButton) {
        throw new Error('Required UI elements not found');
      }
      
      // Add click handlers
      this.startAudioBtn.addEventListener('click', () => this.startStream('audio'));
      this.startCameraBtn.addEventListener('click', () => this.startStream('camera'));
      this.startScreenBtn.addEventListener('click', () => this.startStream('screen'));
      this.stopButton.addEventListener('click', () => this.stopStream());
      
      console.log('Event listeners initialized successfully');
    } catch (error) {
      console.error('Error initializing event listeners:', error);
      alert('Error initializing application: ' + error.message);
    }
  }
  
  /**
   * Start streaming with the selected mode (audio, camera, screen)
   */
  async startStream(mode) {
    if (this.isStreaming) {
      console.log('Already streaming, ignoring start request');
      return;
    }
    
    console.log('Starting stream in mode:', mode);
    this.currentMode = mode;
    
    try {
      // Get configuration from UI
      const config = this.uiController.getConfig();
      console.log('Using config:', config);
      
      // Initialize WebSocket connection
      await this.webSocketClient.connect(config, {
        onMessage: this.handleWebSocketMessage.bind(this),
        onClose: this.handleWebSocketClose.bind(this),
        onError: this.handleWebSocketError.bind(this)
      });
      console.log('WebSocket connected');
      
      // Initialize audio capture
      await this.audioManager.startCapture((audioData) => {
        this.webSocketClient.sendAudio(audioData);
      });
      console.log('Audio capture initialized');
      
      // Initialize video if needed
      if (mode !== 'audio') {
        await this.videoManager.startCapture(mode, (imageData) => {
          this.webSocketClient.sendImage(imageData);
        });
        this.uiController.showVideoPreview();
        console.log('Video capture initialized');
      }
      
      // Update UI state
      this.isStreaming = true;
      this.uiController.updateUIForStreaming(true);
      console.log('Stream started successfully');
      this.startHeartbeat();
    } catch (error) {
      console.error('Error starting stream:', error);
      this.uiController.showError(`Failed to start: ${error.message}`);
      this.stopStream(); // Clean up on error
    }
  }
  
  /**
   * Stop all streaming and clean up resources
   */
  stopStream() {
    if (!this.isStreaming) {
      console.log('Not streaming, ignoring stop request');
      return;
    }
    
    console.log('Stopping stream');
    
    // Clean up resources
    this.webSocketClient.disconnect();
    this.audioManager.stopCapture();
    this.videoManager.stopCapture();
    
    // Reset state
    this.isStreaming = false;
    this.currentMode = null;
    
    // Update UI
    this.uiController.updateUIForStreaming(false);
    this.uiController.hideVideoPreview();
    this.stopHeartbeat();
    
    console.log('Stream stopped successfully');
  }
  
  /**
   * Handle incoming WebSocket messages
   */
  async handleWebSocketMessage(response) {
    try {
      console.log('Received WebSocket message:', response);
      
      switch (response.type) {
        case 'audio':
          console.log('Received audio data, length:', response.data.length);
          await this.audioManager.playAudio(response.data);
          break;
          
        case 'text':
          console.log('Received text:', response.text);
          this.uiController.appendMessage(`[春儿说] ${response.text}`);
          break;
          
        case 'turn_complete':
          console.log('Turn complete received');
          this.uiController.appendMessage('[对话完毕]');
          break;
          
        case 'error':
          console.error('Server error:', response.message);
          this.uiController.showError(`Server error: ${response.message}`);
          break;
          
        default:
          console.warn('Unknown message type:', response.type);
          this.uiController.appendMessage(`[Unknown] ${JSON.stringify(response)}`);
      }
    } catch (error) {
      console.error('Error handling WebSocket message:', error);
      this.uiController.showError(`Error processing message: ${error.message}`);
    }
  }
  
  /**
   * Handle WebSocket connection close
   */
  handleWebSocketClose() {
    console.log('WebSocket connection closed');
    this.uiController.appendMessage('WebSocket closed');
    this.stopStream();
  }
  
  /**
   * Handle WebSocket errors
   */
  handleWebSocketError(error) {
    console.error('WebSocket error:', error);
    this.uiController.showError(`WebSocket error: ${error.message}`);
  }
  
  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.webSocketClient.isConnected() && this.webSocketClient.websocket) {
        this.webSocketClient.websocket.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000); // 30秒
  }
  
  stopHeartbeat() {
    if (this.heartbeatInterval) clearInterval(this.heartbeatInterval);
    this.heartbeatInterval = null;
  }
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM loaded, initializing app');
  try {
    window.app = new GeminiApp();
    console.log('App initialized successfully');
  } catch (error) {
    console.error('Error initializing app:', error);
    alert('Error initializing application: ' + error.message);
  }
});