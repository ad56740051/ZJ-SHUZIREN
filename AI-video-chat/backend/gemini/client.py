import json
import os
from websockets import connect
from typing import Dict, Optional, Any
import edge_tts
import asyncio

class GeminiConnection:
    """
    Client for connecting to the Gemini Multimodal API
    Handles WebSocket communication, audio/video streaming, and response processing
    """
    
    def __init__(self):
        """Initialize the Gemini connection with API key from environment"""
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
            
        self.model = "gemini-2.0-flash-live-001"
        self.uri = (
            "wss://generativelanguage.googleapis.com/ws/"
            "google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent"
            f"?key={self.api_key}"
        )
        self.ws = None
        self.config = None
        self.edge_tts_voice = "zh-CN-XiaoxiaoNeural"  # Fixed EdgeTTS voice
        self.system_prompt = (
            "你的名字叫春儿,英文名Chuner,你的爸爸叫张静,今年2025年。你18岁，"
            "你来自南宋奉贤，你是从2024年穿越到奉贤张静爸爸家。你擅长弹古筝和琵琶，"
            "擅长舞剑。喜欢古典文学。每次回答问题你都要喊一声爸爸。"
        )

    def set_config(self, config_data: Dict[str, Any]) -> None:
        """
        Store configuration options
        
        Args:
            config_data: Dict containing configuration like:
                {
                  'googleSearch': True,
                  'allowInterruptions': False
                }
        """
        self.config = {
            'googleSearch': config_data.get('googleSearch', True),
            'allowInterruptions': config_data.get('allowInterruptions', False)
        }

    async def text_to_speech(self, text: str) -> bytes:
        """
        Convert text to speech using EdgeTTS
        
        Args:
            text: Text to convert to speech
            
        Returns:
            bytes: Audio data in PCM format
        """
        print(f"Converting text to speech: {text}")
        print(f"Using voice: {self.edge_tts_voice}")
        
        try:
            communicate = edge_tts.Communicate(text, self.edge_tts_voice)
            audio_data = b""
            
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
                    print(f"Received audio chunk of size: {len(chunk['data'])} bytes")
            
            print(f"Total audio data size: {len(audio_data)} bytes")
            if len(audio_data) == 0:
                print("Warning: No audio data generated")
            
            return audio_data
        except Exception as e:
            print(f"Error in text_to_speech: {str(e)}")
            return b""

    async def connect(self) -> None:
        """
        Establish WebSocket connection and send initial setup message
        Must send the 'setup' message as the first message to Gemini,
        describing model, voice, system instructions, etc.
        
        Raises:
            ValueError: If configuration is not set
            ConnectionError: If connection fails
        """
        if not self.config:
            raise ValueError("Configuration must be set before connecting.")

        try:
            self.ws = await connect(
                self.uri, 
                additional_headers={"Content-Type": "application/json"}
            )

            # Build 'setup' payload from config
            setup_message = {
                "setup": {
                    "model": f"models/{self.model}",
                    "generation_config": {
                        "response_modalities": ["TEXT"],  # Only request text responses
                    },
                    "system_instruction": {
                        "parts": [
                            {
                                "text": self.system_prompt
                            }
                        ]
                    }
                }
            }

            # Send setup as the first message
            await self.ws.send(json.dumps(setup_message))

            # Read the initial response from Gemini (often just an ack)
            setup_response = await self.ws.recv()
            print("Gemini setup response:", setup_response)
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Gemini API: {str(e)}")

    async def send_audio(self, base64_pcm: str) -> None:
        """
        Send 16-bit PCM audio (base64) to Gemini under 'realtime_input'.
        
        Args:
            base64_pcm: Base64 encoded 16-bit PCM audio data
        """
        if not self.ws:
            return
            
        payload = {
            "realtime_input": {
                "media_chunks": [
                    {
                        "data": base64_pcm,
                        "mime_type": "audio/pcm"
                    }
                ]
            }
        }
        await self.ws.send(json.dumps(payload))

    async def send_text(self, text: str) -> None:
        """
        Send text message to Gemini.
        
        Args:
            text: Text content to send
        """
        if not self.ws:
            return
            
        text_msg = {
            "client_content": {
                "turns": [
                    {
                        "role": "user",
                        "parts": [{"text": text}]
                    }
                ],
                "turn_complete": True
            }
        }
        await self.ws.send(json.dumps(text_msg))

    async def send_image(self, base64_jpeg: str) -> None:
        """
        Send image data to Gemini.
        
        Args:
            base64_jpeg: Base64 encoded JPEG image data
        """
        if not self.ws:
            return
            
        payload = {
            "realtime_input": {
                "media_chunks": [
                    {
                        "data": base64_jpeg,
                        "mime_type": "image/jpeg"
                    }
                ]
            }
        }
        await self.ws.send(json.dumps(payload))

    async def receive(self) -> Optional[str]:
        """
        Wait for next message from Gemini.
        
        Returns:
            JSON response string or None if connection is closed
        """
        if not self.ws:
            return None
        return await self.ws.recv()

    async def close(self) -> None:
        """Close the WebSocket connection."""
        if self.ws:
            await self.ws.close()
            self.ws = None