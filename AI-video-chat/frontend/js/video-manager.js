/**
 * Video Manager class
 * Handles video/screen capture and frame extraction
 */
export class VideoManager {
    constructor() {
      this.videoStream = null;
      this.videoElement = document.getElementById('videoElem');
      this.canvasElement = document.getElementById('canvasElem');
      this.videoInterval = null;
      this.onImageData = null;
      
      if (!this.videoElement || !this.canvasElement) {
        console.error('Video or canvas element not found');
      }
    }
    
    /**
     * Start video capture from camera or screen
     * @param {string} mode - 'camera' or 'screen'
     * @param {Function} onImageData - Callback for captured image data
     * @returns {Promise} - Resolves when video capture is initialized
     */
    async startCapture(mode, onImageData) {
      this.onImageData = onImageData;
      
      try {
        // Get video stream based on mode
        if (mode === 'camera') {
          this.videoStream = await navigator.mediaDevices.getUserMedia({
            video: { width: { ideal: 320 }, height: { ideal: 240 } }
          });
        } else if (mode === 'screen') {
          this.videoStream = await navigator.mediaDevices.getDisplayMedia({
            video: { width: { ideal: 640 }, height: { ideal: 360 } }
          });
        } else {
          throw new Error(`Invalid capture mode: ${mode}`);
        }
        
        // Set video source
        this.videoElement.srcObject = this.videoStream;
        
        // Wait for video to be ready
        await new Promise((resolve) => {
          this.videoElement.onloadedmetadata = () => {
            this.videoElement.play();
            resolve();
          };
        });
        
        // Start capturing frames (lower frame rate: 1 frame per 2 seconds)
        this.videoInterval = setInterval(() => {
          this.captureAndSendFrame();
        }, 2000); // 2秒一帧
        
      } catch (error) {
        console.error('Error initializing video capture:', error);
        throw new Error(`Video capture failed: ${error.message}`);
      }
    }
    
    /**
     * Stop video capture and release resources
     */
    stopCapture() {
      // Stop frame capture
      if (this.videoInterval) {
        clearInterval(this.videoInterval);
        this.videoInterval = null;
      }
      
      // Stop video tracks
      if (this.videoStream) {
        this.videoStream.getTracks().forEach(track => track.stop());
        this.videoStream = null;
      }
      
      // Clear video source
      if (this.videoElement) {
        this.videoElement.srcObject = null;
      }
    }
    
    /**
     * Capture current video frame and send through callback
     * @private
     */
    captureAndSendFrame() {
      if (!this.videoStream || !this.onImageData || !this.videoElement || !this.canvasElement) {
        return;
      }
      
      try {
        const ctx = this.canvasElement.getContext('2d');
        if (!ctx) {
          console.error('Failed to get canvas context');
          return;
        }
        
        // Set canvas size to match video dimensions
        this.canvasElement.width = this.videoElement.videoWidth;
        this.canvasElement.height = this.videoElement.videoHeight;
        
        // Draw video frame to canvas
        ctx.drawImage(this.videoElement, 0, 0, this.videoElement.videoWidth, this.videoElement.videoHeight);
        
        // Get JPEG image as base64
        const base64Image = this.canvasElement.toDataURL('image/jpeg').split(',')[1];
        
        // Send through callback
        this.onImageData(base64Image);
      } catch (error) {
        console.error('Error capturing frame:', error);
      }
    }
}