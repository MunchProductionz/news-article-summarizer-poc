from openai import OpenAI
from dotenv import load_dotenv
import os
from datetime import datetime
from asyncio import Semaphore
import logging
import time

# Define a Semaphore to limit concurrent requests
rate_limit = Semaphore(5)  # Limit to 5 concurrent requests (adjust as needed)

# My code
async def text_to_speech(texts):
    dev = False
    if dev:
        load_dotenv()
    key = os.environ.get('OPENAI_KEY')
    client = OpenAI(api_key=key)
    responses = []
    for text in texts:
        async with rate_limit:  # Limit concurrent API calls
            retries = 3
            while retries > 0:
                try:
                    response = await client.audio.speech.create(
                        model="tts-1",
                        voice="alloy",
                        input=text,
                        response_format="opus",
                        speed=1.0,
                    )
                    responses.append(response)
                    break
                except Exception as e:
                    logging.error(f"Error with text-to-speech: {e}")
                    retries -= 1
                    if retries > 0:
                        time.sleep(2)  # Wait 2 seconds before retrying
                    else:
                        raise e  # Re-raise the exception if out of retries
                    
    return responses