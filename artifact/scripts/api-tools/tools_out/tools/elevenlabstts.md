# ElevenLabs Text-to-Speech Tool Documentation

## Overview
The ElevenLabs TTS tool provides high-quality text-to-speech synthesis with multiple voices, emotions, and languages. It supports both synchronous and asynchronous generation, with features for voice cloning and customization.

## Required Credentials
```python
ELEVENLABS_API_KEY="your_elevenlabs_api_key"  # Required for all operations
```

## Input Parameters

### Required Parameters
- `text` (str): The text to convert to speech
- `voice_id` (str): Voice identifier or name

### Optional Parameters
```python
{
    "model_id": str,           # Model to use (e.g., 'eleven_monolingual_v1')
    "stability": float,        # 0.0-1.0, voice stability
    "similarity_boost": float, # 0.0-1.0, voice clarity
    "style": float,           # 0.0-1.0, speaking style intensity
    "use_speaker_boost": bool, # Enhance speaker clarity
    "language": str,          # ISO language code
    "optimize_streaming": bool # Optimize for streaming output
}
```

## Output Format

### Synchronous Generation
```python
{
    "audio": bytes,           # Raw audio data
    "metadata": {
        "text": str,          # Original text
        "voice_id": str,      # Used voice
        "voice_settings": {}, # Applied settings
        "duration": float,    # Audio duration in seconds
        "word_markers": []    # Word timing markers
    }
}
```

### Streaming Response
```python
for chunk in audio_stream:
    chunk.audio_data  # Raw audio bytes
    chunk.timestamp   # Timestamp in ms
    chunk.text       # Corresponding text
```

## Voice Options

### Pre-made Voices
- Rachel: Natural, professional female voice
- Josh: Clear, engaging male voice
- Emily: Warm, friendly female voice
- Adam: Authoritative male voice

### Voice Settings
```python
{
    "stability": 0.75,        # Default stability
    "similarity_boost": 0.75, # Default similarity
    "style": 0.0,            # Default style
    "use_speaker_boost": True # Default speaker boost
}
```

## Rate Limits
- Character limit: Based on subscription
- Concurrent requests: Based on subscription
- Monthly character quota: Subscription dependent
- API calls per minute: Subscription dependent

## Error Handling
```python
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Error description",
        "details": {}
    }
}
```

Common error codes:
- `INVALID_API_KEY`
- `VOICE_NOT_FOUND`
- `TEXT_TOO_LONG`
- `RATE_LIMIT_EXCEEDED`
- `INVALID_AUDIO_FORMAT`

## Example Usage

### Basic Text-to-Speech
```python
from tools.elevenlabsTTS import ElevenLabsTTS

tts = ElevenLabsTTS()
audio = tts.generate_speech(
    text="Hello, this is a test message.",
    voice_id="Rachel"
)
```

### Advanced Usage
```python
response = tts.generate_speech(
    text="This is a professional announcement.",
    voice_id="Josh",
    model_id="eleven_monolingual_v1",
    stability=0.8,
    similarity_boost=0.7,
    style=0.3,
    language="en-US"
)
```

### Streaming Audio
```python
for chunk in tts.stream_speech(
    text="Long text to stream...",
    voice_id="Emily"
):
    # Process audio chunks
    process_audio(chunk.audio_data)
```

## Common Applications

### Content Creation
1. Podcast generation
2. Video narration
3. Audiobook creation
4. Educational content

### Accessibility
1. Screen readers
2. Text-to-speech interfaces
3. Accessibility tools
4. Audio descriptions

### Business Applications
1. IVR systems
2. Customer service
3. Presentations
4. Training materials

## Integration Examples

### With Mistral AI
```python
from tools.mistral import MistralAI
from tools.elevenlabsTTS import ElevenLabsTTS

def generate_and_speak(prompt):
    # Generate text
    text = MistralAI().generate(prompt)
    
    # Convert to speech
    audio = ElevenLabsTTS().generate_speech(
        text=text['response']['content'],
        voice_id="Rachel"
    )
    return audio
```

### With File Management
```python
from tools.elevenlabsTTS import ElevenLabsTTS
from tools.files import FileManager

def create_audio_file(text, filename):
    # Generate audio
    audio = ElevenLabsTTS().generate_speech(text)
    
    # Save to file
    FileManager().save_audio(
        audio_data=audio['audio'],
        filename=filename,
        format='mp3'
    )
```

## Best Practices

### Text Preparation
1. Clean input text
2. Add punctuation
3. Format numbers
4. Handle abbreviations
5. Consider pacing

### Voice Selection
1. Match content tone
2. Consider audience
3. Test multiple voices
4. Maintain consistency

### Audio Quality
1. Optimize settings
2. Monitor stability
3. Check pronunciations
4. Validate output

## Performance Optimization

### Resource Management
1. Cache common phrases
2. Use streaming for long text
3. Batch similar requests
4. Monitor API usage

### Quality Control
1. Validate input text
2. Check audio quality
3. Monitor word timing
4. Test different settings

### Cost Optimization
1. Use appropriate models
2. Optimize text length
3. Cache results
4. Monitor usage

## Troubleshooting

### Common Issues
1. Audio quality problems
   - Solution: Adjust stability/similarity
2. Rate limiting
   - Solution: Implement backoff
3. Pronunciation errors
   - Solution: Use SSML or modify text
4. Streaming issues
   - Solution: Check network/buffer

### Quality Improvements
1. Use SSML tags
2. Adjust voice settings
3. Pre-process text
4. Post-process audio

## Additional Features

### Voice Cloning
```python
voice = tts.clone_voice(
    name="Custom Voice",
    files=["sample1.mp3", "sample2.mp3"],
    description="Custom voice description"
)
```

### Voice Library
```python
voices = tts.get_voices()
for voice in voices:
    print(f"Name: {voice.name}")
    print(f"ID: {voice.voice_id}")
    print(f"Preview: {voice.preview_url}")
``` 