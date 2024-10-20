from openai import OpenAI
from dotenv import load_dotenv
import os
from datetime import datetime
from asyncio import Semaphore
import logging
import time

# My code
def text_to_speech(texts):
    dev = False
    if dev:
        load_dotenv()
    key = os.environ.get('OPENAI_KEY')
    client = OpenAI(api_key=key)
    responses = []
    for text in texts:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
            response_format="opus",
            speed=1.0,
        )
        responses.append(response)
                    
    return responses