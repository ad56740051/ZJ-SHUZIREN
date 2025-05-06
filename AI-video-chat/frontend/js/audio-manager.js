/**
 * Audio Manager class
 * Handles audio capture from microphone and playback of received audio
 */
export class AudioManager {
    constructor() {
      // Audio capture
      this.captureAudioContext = null;
      this.scriptProcessor = null;
      this.mediaStream = null;
      this.mediaSource = null;
      this.onAudioData = null;
      
      // Audio playback
      this.playbackAudioContext = null;
      this.currentSource = null;  // Track current audio source
    }
    
    /**
     * Start audio capture from microphone
     * @param {Function} onAudioData - Callback for captured audio data
     * @returns {Promise} - Resolves when audio capture is initialized
     */
    async startCapture(onAudioData) {
      this.onAudioData = onAudioData;
      
      try {
        // Get microphone access at system rate, resampled to 16 kHz by AudioContext
        this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Create audio context for capture at 16kHz (Gemini's input requirement)
        this.captureAudioContext = new AudioContext({ sampleRate: 16000 });
        
        // Create media source from mic stream
        this.mediaSource = this.captureAudioContext.createMediaStreamSource(this.mediaStream);
        
        // Create script processor for audio processing (buffer size 512, mono)
        this.scriptProcessor = this.captureAudioContext.createScriptProcessor(512, 1, 1);
        
        // Set up audio processing callback
        this.scriptProcessor.onaudioprocess = (event) => {
          // Get audio samples as Float32Array (-1.0 to 1.0)
          const floatSamples = event.inputBuffer.getChannelData(0);
          
          // Convert to PCM 16-bit and send base64 encoded data
          const pcm16 = this.float32ToPcm16(floatSamples);
          const base64Audio = this.pcm16ToBase64(pcm16);
          
          // Send data through callback
          if (this.onAudioData) {
            this.onAudioData(base64Audio);
          }
        };
        
        // Connect the audio processing chain
        this.mediaSource.connect(this.scriptProcessor);
        this.scriptProcessor.connect(this.captureAudioContext.destination);
        
      } catch (error) {
        console.error('Error initializing audio capture:', error);
        throw new Error(`Microphone access denied: ${error.message}`);
      }
    }
    
    /**
     * Stop audio capture and release resources
     */
    stopCapture() {
      // Stop any playing audio
      if (this.currentSource) {
        this.currentSource.stop();
        this.currentSource = null;
      }
      
      // Disconnect and release audio processing
      if (this.scriptProcessor) {
        this.scriptProcessor.disconnect();
        this.scriptProcessor = null;
      }
      
      if (this.mediaSource) {
        this.mediaSource.disconnect();
        this.mediaSource = null;
      }
      
      // Close audio contexts
      if (this.captureAudioContext) {
        this.captureAudioContext.close();
        this.captureAudioContext = null;
      }
      
      if (this.playbackAudioContext) {
        this.playbackAudioContext.close();
        this.playbackAudioContext = null;
      }
      
      // Stop all audio tracks
      if (this.mediaStream) {
        this.mediaStream.getTracks().forEach(track => track.stop());
        this.mediaStream = null;
      }
    }
    
    /**
     * Play received audio data (EdgeTTS MP3, decode and play directly)
     * @param {string} hexAudio - Hex encoded audio data from EdgeTTS
     */
    async playAudio(hexAudio) {
      try {
        // Stop any currently playing audio
        if (this.currentSource) {
          this.currentSource.stop();
          this.currentSource = null;
        }
        
        // Convert hex string to ArrayBuffer
        const bytes = new Uint8Array(hexAudio.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
        const arrayBuffer = bytes.buffer;

        // Create or resume AudioContext
        if (!this.playbackAudioContext) {
          this.playbackAudioContext = new AudioContext();
        }
        
        // Ensure AudioContext is running (required by modern browsers)
        if (this.playbackAudioContext.state === 'suspended') {
          await this.playbackAudioContext.resume();
        }

        // Decode and play MP3
        const audioBuffer = await this.playbackAudioContext.decodeAudioData(arrayBuffer);
        const source = this.playbackAudioContext.createBufferSource();
        this.currentSource = source;  // Store reference to current source
        
        source.buffer = audioBuffer;
        source.connect(this.playbackAudioContext.destination);
        
        // Handle playback completion
        source.onended = () => {
          this.currentSource = null;
        };
        
        source.start();
        
        console.log('Audio playback started successfully');
      } catch (error) {
        console.error('Error playing audio:', error);
        // Try to recover by creating a new AudioContext
        if (this.playbackAudioContext) {
          await this.playbackAudioContext.close();
          this.playbackAudioContext = null;
        }
      }
    }
    
    /**
     * Convert Float32Array samples (-1.0 to 1.0) to 16-bit PCM
     * @param {Float32Array} float32Array - Audio samples
     * @returns {Int16Array} - 16-bit PCM data
     * @private
     */
    float32ToPcm16(float32Array) {
      const pcm16 = new Int16Array(float32Array.length);
      
      for (let i = 0; i < float32Array.length; i++) {
        // Clamp values to -1.0...1.0 range
        const sample = Math.max(-1, Math.min(1, float32Array[i]));
        
        // Convert to 16-bit range: negative values to -32768..0, positive to 0..32767
        pcm16[i] = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
      }
      
      return pcm16;
    }
    
    /**
     * Convert PCM 16-bit data to base64 string
     * @param {Int16Array} pcm16 - 16-bit PCM data
     * @returns {string} - Base64 encoded data
     * @private
     */
    pcm16ToBase64(pcm16) {
      const bytes = new Uint8Array(pcm16.buffer);
      let binary = "";
      
      for (let i = 0; i < bytes.length; i++) {
        binary += String.fromCharCode(bytes[i]);
      }
      
      return btoa(binary);
    }
}