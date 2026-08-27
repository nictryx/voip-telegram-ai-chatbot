import os
import tempfile

from groq import Groq
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

client = Groq(api_key=GROQ_API_KEY)

CHAT_MODEL = "openai/gpt-oss-20b"
STT_MODEL = "whisper-large-v3-turbo"
TTS_MODEL = "canopylabs/orpheus-v1-english"
TTS_VOICE = "troy"

SYSTEM_PROMPT = """
You are a helpful AI assistant.
Answer clearly and naturally.
Do not start your response with "My master" because the application
will add it automatically.
"""

conversations = {}


def get_history(chat_id):
    if chat_id not in conversations:
        conversations[chat_id] = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

    return conversations[chat_id]


def generate_response(chat_id, user_message):
    messages = get_history(chat_id)

    messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages
    )

    reply = response.choices[0].message.content.strip()

    messages.append(
        {
            "role": "assistant",
            "content": reply
        }
    )

    return f"My master, {reply}"


def text_to_speech(text, output_path):
    response = client.audio.speech.create(
        model=TTS_MODEL,
        voice=TTS_VOICE,
        input=text,
        response_format="wav"
    )

    response.write_to_file(output_path)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "My master, send me a text or voice message."
    )


async def clear_memory(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    chat_id = update.effective_chat.id

    conversations.pop(chat_id, None)

    await update.message.reply_text(
        "My master, conversation memory has been cleared."
    )


async def text_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    chat_id = update.effective_chat.id
    user_text = update.message.text

    try:
        reply = generate_response(
            chat_id,
            user_text
        )

        await update.message.reply_text(
            reply
        )

    except Exception as error:
        print(error)

        await update.message.reply_text(
            "My master, something went wrong."
        )


async def voice_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    chat_id = update.effective_chat.id

    voice_file = await update.message.voice.get_file()

    with tempfile.TemporaryDirectory() as temp_dir:

        input_path = os.path.join(
            temp_dir,
            "voice.ogg"
        )

        output_path = os.path.join(
            temp_dir,
            "response.wav"
        )

        await voice_file.download_to_drive(
            input_path
        )

        try:
            with open(input_path, "rb") as audio:
                transcription = client.audio.transcriptions.create(
                    file=audio,
                    model=STT_MODEL,
                    response_format="json"
                )

            transcript = transcription.text.strip()

            await update.message.reply_text(
                f"You: {transcript}"
            )

            reply = generate_response(
                chat_id,
                transcript
            )

            await update.message.reply_text(
                reply
            )

            text_to_speech(
                reply,
                output_path
            )

            with open(output_path, "rb") as voice:
                await update.message.reply_voice(
                    voice=voice
                )

        except Exception as error:
            print(error)

            await update.message.reply_text(
                "My master, something went wrong while processing your voice message."
            )


def main():

    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is missing."
        )

    if not TELEGRAM_BOT_TOKEN:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN is missing."
        )

    app = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CommandHandler(
            "clear",
            clear_memory
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_message
        )
    )

    app.add_handler(
        MessageHandler(
            filters.VOICE,
            voice_message
        )
    )

    print("Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()