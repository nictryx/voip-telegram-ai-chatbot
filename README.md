# VoIP Telegram AI Chatbot

An AI-powered Telegram chatbot that supports **voice-to-voice and text-to-text conversations** using Groq AI.

The project combines speech recognition, AI-generated responses, text-to-speech, and conversational memory to provide a more natural way to interact with a chatbot through Telegram.

## Features

- Text-to-text AI conversations
- Voice-to-voice conversations
- Voice message transcription
- AI-generated text responses
- AI-generated voice responses
- Conversation memory
- Telegram bot integration
- Groq AI integration
- Speech-to-text using Whisper
- Text-to-speech output

## How It Works

### Text Conversation

When the user sends a text message:

1. The message is sent to the AI model.
2. The AI generates a response.
3. The response is returned as a Telegram text message.

### Voice Conversation

When the user sends a voice message:

1. The voice message is converted to text.
2. The transcription is displayed in the chat.
3. The transcription is sent to the AI model.
4. The AI generates a response.
5. The response is displayed as text.
6. The same response is converted to speech and returned as a voice message.

## Tech Stack

- Python
- Telegram Bot API
- Groq API
- GPT-OSS
- Whisper
- Orpheus Text-to-Speech
- python-telegram-bot
