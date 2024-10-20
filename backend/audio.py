from openai import OpenAI
from dotenv import load_dotenv
import os

def text_to_speech(text):
    dev = False
    if dev:
        load_dotenv()
    key = os.environ.get('OPENAI_KEY')
    client = OpenAI(api_key=key)
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
        response_format="opus"
    )
    return response