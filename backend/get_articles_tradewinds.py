import requests
import bs4
import selenium
from datetime import datetime
import calendar
from typing import List, Dict, Union, Optional
from pprint import pprint
import time
import os
from typing_extensions import TypedDict
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
from openai import OpenAI
from models import ArticleInfo, ArticleInfoLeadText, ArticleInfoContent, ArticleSummary, MessageDict, ChoiceDict, UsageDetailsDict, UsageDict, ChatCompletionResponse

### get_articles_with_info ###

# Get date
def get_date(time):
    date_format = time.attrs['publish-date-format']
    date = time.text.split('Published')[1].strip()
    month = date.split(' ')[1]
    month_number = list(calendar.month_name).index(month)
    if month_number < 10:
        month_number = '0' + str(month_number)
    date = date.replace(month, str(month_number)).replace(' ', '-')
    date_format = date_format.replace('D', '%d').replace('MMM', '%m').replace('YYYY', '%Y').replace('HH', '%H').replace('mm', '%M').replace(' ', '-')
    datetime_object = datetime.strptime(date[:-4], date_format)
    return datetime_object

# Get category
def get_category(card):
    category = card.find('a').text.strip()
    return category

# Get title and href
def get_title_link(div):
    title = div.find('a').text.strip()
    href = div.find('a').get('href')
    link = 'https://www.tradewindsnews.com/' + href
    return title, link

# Get Tradewinds articles
def get_articles_with_info(verbose=False, hours_ago=8) -> List[ArticleInfo]:
    response = requests.get('https://www.tradewindsnews.com/latest')
    HTML = response.text
    soup = bs4.BeautifulSoup(HTML, 'html.parser')

    divs = soup.findAll('div', {'class': 'mb-auto'})
    cards = soup.findAll('div', {'class': 'card-body'})
    times = soup.findAll('span', {'class': 'published-at'})
    
    articles = []

    for i, (div, card, time) in enumerate(zip(divs, cards, times)):
        title, link = get_title_link(div)
        category = get_category(card)
        date = get_date(time)
        
        # Only get articles from the last 2 hours       # 7200 / 60 / 60
        seconds_per_hour = 60*60
        hours = hours_ago
        if (datetime.now() - date).seconds > hours*seconds_per_hour:
            if verbose:
                print(f'No more articles from the front page to show from the last {hours} hours ({i+1}/{len(divs)})\n')
            break
        
        article = ArticleInfo(
            date_time=date,
            category=category,
            title=title,
            url=link
            )
        articles.append(article)
        
        if verbose:
            print(f'{date} - {category} - {title}')
    
    return articles


### get_articles_with_lead_text ###

# Get lead text
def get_articles_with_lead_text(articles: List[ArticleInfo]) -> List[ArticleInfoLeadText]:
    articles_with_lead_text = []
    for article in articles:
        time.sleep(0.5)
        response = requests.get(article['url'])
        HTML = response.text
        soup = bs4.BeautifulSoup(HTML, 'html.parser')

        divs = soup.findAll('p', {'class': 'fs-lg mb-4 article-lead-text'})
        article_with_lead_text = ArticleInfoLeadText(
            date_time=article['date_time'],
            category=article['category'],
            title=article['title'],
            url=article['url'],
            lead_text=divs[0].text  # Added this line
            )
        articles_with_lead_text.append(article_with_lead_text)
    return articles_with_lead_text


### get_articles_with_content_from_trade_winds ###

def login_to_trade_winds(driver: webdriver.Chrome, email: str, password: str) -> webdriver.Chrome:
    
    # Login Page
    driver.get("https://www.tradewindsnews.com/auth/user/login?target=%2F")

    # Login
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, "#app > div.auth > div > div.form-wrapper > div > div > form > div:nth-child(1) > span:nth-child(1) > div > div.input-field-wrapper.d-flex > input").click()
    time.sleep(1)
    for character in email:
        driver.find_element(By.CSS_SELECTOR, "#app > div.auth > div > div.form-wrapper > div > div > form > div:nth-child(1) > span:nth-child(1) > div > div.input-field-wrapper.d-flex > input").send_keys(character)
        time.sleep(0.1)
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, "#app > div.auth > div > div.form-wrapper > div > div > form > div:nth-child(1) > span:nth-child(2) > div > div.input-field-wrapper.d-flex > input[type=password]").click()
    time.sleep(1)
    for character in password:
        driver.find_element(By.CSS_SELECTOR, "#app > div.auth > div > div.form-wrapper > div > div > form > div:nth-child(1) > span:nth-child(2) > div > div.input-field-wrapper.d-flex > input[type=password]").send_keys(character)
        time.sleep(0.1)
    time.sleep(2)
    try: # Sometimes the "Accept TOS" checkbox needs to be checked
        driver.find_element(By.CSS_SELECTOR, "#app > div.auth > div > div.form-wrapper > div > div > form > div:nth-child(2) > div.mt-0 > div > div.mt-0.mb-0 > div > div:nth-child(1)").click()
        time.sleep(1)
    except:
        pass
    driver.find_element(By.CSS_SELECTOR, "#app > div.auth > div > div.form-wrapper > div > div > form > div:nth-child(2) > div.mt-0 > div > div.loading-button > button").click()
    time.sleep(6)

    # Close Cookie-disclaimer
    driver.find_element(By.CSS_SELECTOR, "#onetrust-pc-btn-handler").click()
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, "#onetrust-pc-sdk > div > div.ot-pc-footer.ot-pc-scrollbar > div.ot-btn-container > button.ot-pc-refuse-all-handler").click()
    time.sleep(1)

    return driver

def logout_trade_winds(driver: webdriver.Chrome) -> webdriver.Chrome:
    
    driver.find_element(By.CSS_SELECTOR, "#app > div > div.top-bar > nav > header > div > div.d-flex.justify-content-between.align-items-center > div > div > div:nth-child(2) > button").click()
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, "#app > div > div.top-bar > nav > header > div > div.d-flex.justify-content-between.align-items-center > div > div > div:nth-child(2) > div > div > div > div > div:nth-child(2) > a").click()
    time.sleep(4)
    
    return driver

def get_articles_with_content_from_trade_winds(articles: List[ArticleInfoLeadText]) -> List[ArticleInfoContent]:
    articles_with_content = []

    email = os.getenv('TRADEWINDS_EMAIL')
    password = os.getenv('TRADEWINDS_PASSWORD')
    
    driver = webdriver.Chrome()
    driver = login_to_trade_winds(driver, email, password)
    for article in articles:
        
        # Get article content
        print("Getting content for: ", article['url'])
        driver.get(article['url'])
        time.sleep(4)
        page_source = bs4.BeautifulSoup(driver.page_source, 'html.parser')
        paragraphs = page_source.select('#app > div > div.container-fluid.tradewinds.articlepage.page-articlepage > div.wrapper > div > div:nth-child(2) > div:nth-child(1) > div.article-center-column.col-12.col-md-9.col-lg-6 > div.article-body > div')[0].select('p')
        content = ""
        for paragraph in paragraphs:
            content += paragraph.text + "\n"
        
        article_with_content = ArticleInfoContent(
            date_time=article['date_time'],
            category=article['category'],
            title=article['title'],
            url=article['url'],
            lead_text=article['lead_text'],
            content=content
            )
        articles_with_content.append(article_with_content)
        time.sleep(1)
    
    print("Logging out")
    driver = logout_trade_winds(driver)
    driver.quit()
    
    return articles_with_content


### get_articles_with_summaries_and_bullet_points ###

def get_client():
    client = OpenAI()
    return client

def get_completion(client: OpenAI, model: str, messages: List[Dict[str, str]]) -> ChatCompletionResponse:
    try:
        completion: ChatCompletionResponse = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return completion
    except Exception as e:
        print(e)
        return None

def get_summary(client: OpenAI, article: ArticleInfoContent) -> str:
    model = "gpt-4o-mini"
    messages = [
        {"role": "system", "content": "You are a ship broker and an expert at providing concise and information dense summaries of news articles."},
        {"role": "system", "content": "I will provide you with the title, lead text, and content from a news article. I want you to summarize the content in a few sentences. Respond only with the summary and a potential analysis and opinion from the author."},
        {"role": "system", "content": "Only use information from the news article, and do not hallucinate."},
        {"role": "system", "content": "The summary should focus on key events, key entities, key numbers, and the authors analysis and opinion."},
        {"role": "system", "content": "Write the summary first. If the authors analysis and opinion exist, add a newline, the text 'Authors Analysis:', and summarize the analysis and opinion as well in 1-2 sentences. If it does not exist, do not add this part."},
        {"role": "user", "content": f"<title>{article['content']}</title>"},
        {"role": "user", "content": f"<lead text>{article['lead_text']}</lead text>"},
        {"role": "user", "content": f"< content>{article['content']}</content>"}
    ]
    completion = get_completion(client, model, messages)
    summary = completion.choices[0].message.content
    return summary

def get_bullet_points(client: OpenAI, article: ArticleInfoContent) -> str:
    model = "gpt-4o-mini"
    messages = [
        {"role": "system", "content": "You are a ship broker and an expert at providing concise and informative bullet points of news articles."},
        {"role": "system", "content": "I will provide you with the title, lead text, and content from a news article. I want you to summarize the lead text and content with two informative and concise bullet points. Respond only with the bullet points."},
        {"role": "system", "content": "The bullet points should be formatted in the following manner: 'Point 1|Point 2'. Do not include any prefix '- ', the bullet points should only contain the actual text with a '|' as separator between the points."},
        {"role": "system", "content": "Only use information from the news article, and do not hallucinate."},
        {"role": "system", "content": "The bullet points should focus on key events, key entities, key numbers, and the authors analysis and opinion."},
        {"role": "system", "content": "The bullet points should give a ship broker the information they need to understand what the article is about, and what insights they gain from reading it."},
        {"role": "user", "content": f"<title>{article['content']}</title>"},
        {"role": "user", "content": f"<lead text>{article['lead_text']}</lead text>"},
        {"role": "user", "content": f"< content>{article['content']}</content>"}
    ]
    completion = get_completion(client, model, messages)
    bullet_points = completion.choices[0].message.content
    return bullet_points

def get_articles_with_summaries_and_bullet_points(articles: List[ArticleInfoContent]) -> List[ArticleSummary]:
    articles_with_summaries_and_bullet_points = []
    client = get_client()
    for article in articles:
        summary = get_summary(client, article)
        bullet_points = get_bullet_points(client, article)
        articles_with_summary_and_bullet_points = ArticleSummary(
            date_time=article['date_time'],
            category=article['category'],
            title=article['title'],
            url=article['url'],
            lead_text=article['lead_text'],
            content=article['content'],
            summary=summary,
            bullet_points=bullet_points
        )
        articles_with_summaries_and_bullet_points.append(articles_with_summary_and_bullet_points)
    return articles_with_summaries_and_bullet_points


### MAIN FUNCTION ###
### get_articles_from_tradewinds ###

# Get articles from Tradewinds
def get_articles_from_tradewinds(hours_ago: int = 8) -> List[ArticleSummary]:
    
    load_dotenv()
    articles: List[ArticleInfo] = get_articles_with_info(hours_ago=hours_ago)
    articles: List[ArticleInfoLeadText] = get_articles_with_lead_text(articles)
    articles: List[ArticleInfoContent] = get_articles_with_content_from_trade_winds(articles)
    articles: List[ArticleSummary] = get_articles_with_summaries_and_bullet_points(articles)
    
    return articles


if __name__ == '__main__':
    articles = get_articles_from_tradewinds(hours_ago=23)
    pprint(articles)