from audio import text_to_speech
from mail import send_email_with_attachement
from db import get_articles_by_id
from models import ChatCompletionResponse
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()

async def run_in_thread(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)

def get_top_insights_from_summaries(body: str) -> str:

    summaries = body.split("|=======================|")[1:-1]   # Remove the first and last empty strings

    load_dotenv()
    client = OpenAI()
    model = "gpt-4o-mini"
    messages = [
        {"role": "system", "content": "You are a ship broker and an expert at extracting key insights from summaries of news articles."},
        {"role": "system", "content": "I will provide you with summaries of news articles, each containing key events, key entities, key numbers, and potentially the authors analysis and opinion."},
        {"role": "system", "content": "Your task is to extract the top key insight from each summary. Ensure that the insights are concise and relevant for a fellow ship broker."},
        {"role": "system", "content": "Extract only one key insight from each summary."},
        {"role": "system", "content": "Only use information from the summaries, and do not hallucinate."},
        {"role": "system", "content": "Respond only with a list of the top key insights."},
        {"role": "user", "content": f"<summaries>{summaries}</summaries>"}
    ]
    try:
        completion: ChatCompletionResponse = client.chat.completions.create(
            model=model,
            messages=messages
        )
    except Exception as e:
        print(e)
        return None
    top_three_insights = completion.choices[0].message.content
    return top_three_insights

def get_body_and_text_to_speech_text(ids):
    
    today_date = datetime.today().strftime("%Y-%m-%d")
    today_weekday = datetime.today().strftime("%A")
    
    # Create the body of the email
    body = f"Summaries {today_weekday} {today_date}\n"
    body += f"Here are the {len(ids)} articles you requested:\n\n"
    body += "|=======================|\n\n"
    
    articles = get_articles_by_id(ids)
    for article in articles:
        body += f"Title: {article['title']}\n"
        body += f"URL: {article['url']}\n"
        body += f"Category: {article['category']}\n"
        body += f"Summary: {article['summary']}\n"
        body += "\n"
        
    body += "|=======================|\n\n"
    body += "See the attachment for the summaries in audio format.\n"
    
    # Create the text to speech text
    top_insights = get_top_insights_from_summaries(body)
    today_day_and_month = datetime.today().strftime("%B %d")
    if today_day_and_month.split(" ")[-1][-1] == "1": today_day_and_month += "st"
    elif today_day_and_month.split(" ")[-1][-1] == "2": today_day_and_month += "nd"
    elif today_day_and_month.split(" ")[-1][-1] == "3": today_day_and_month += "rd"
    else: today_day_and_month += "th"
    summary_or_summaries = "summary" if len(ids) == 1 else "summaries"
    text_to_speech_text = f"Good morning! I hope you are having a great day."
    text_to_speech_text = f"Today is {today_weekday} {today_day_and_month}."
    text_to_speech_text += f"Here is a list of the top insights from the {len(ids)} {summary_or_summaries} you requested: {top_insights}."
    
    text_to_speech_text += f"I will now go through each of the {len(ids)} summary one by one."
    for i, article in enumerate(articles):
        text_to_speech_text += f"Number {i+1}."
        text_to_speech_text += f"{article['category']} news."
        text_to_speech_text += f"Title of the article: {article['title']}."
        text_to_speech_text += f"{article['summary']}."
        
    text_to_speech_text += f"That's all for today. Have a great day at work!"
    
    return body, text_to_speech_text

async def summmarizer(ids, mail):

    today_date = datetime.today().strftime("%Y-%m-%d")
    today_weekday = datetime.today().strftime("%A")
    article_or_articles = "article" if len(ids) == 1 else "articles"
    subject = f"{today_weekday} summaries {today_date}: {len(ids)} {article_or_articles}"
    body, text_to_speech_text = get_body_and_text_to_speech_text(ids)
    res = await run_in_thread(text_to_speech, text_to_speech_text)

    msg = await send_email_with_attachement(subject, body, mail, res)

    return msg


if __name__ == '__main__':
    load_dotenv()
    
    ids = ["abf450a7-05b6-4456-9991-8a1039988295", "662677e6-5775-4af6-8d9a-7737d5ce9264"]
    mail = "henrik.raaen.bo.nadderud@gmail.com"
    asyncio.run(summmarizer(ids, mail))