from supabase import create_client, Client
from dotenv import load_dotenv
import os
from typing import List
from models import ArticleSummary

dev = False

def insert_articles_db(articles: List[ArticleSummary]) -> None:
    if dev:
        load_dotenv()
    url: str = os.environ.get("SUPABASE_URL", "SUPABASE_URL environment variable is not set.")
    key: str = os.environ.get("SUPABASE_KEY", "SUPABASE_KEY environment variable is not set.")
    supabase: Client = create_client(url, key)
    list_of_articles = []
    for article in articles:
        article_object = {
            "published_at": article['date_time'].strftime("%Y-%m-%d %H:%M:%S"),
            "category": article['category'],
            "title": article['title'],
            "url": article['url'],
            "lead_text": article['lead_text'],
            "content": article['content'],
            "summary": article['summary'],
            "bullet_points": article['bullet_points'],
        }
        list_of_articles.append(article_object)

    try:
        response = supabase.table("articles").insert(list_of_articles).execute()
        return response
    except Exception as exception:
        return exception

def delete_all_articles_db() -> None:
    if dev:
        load_dotenv()
    url: str = os.environ.get("SUPABASE_URL", "SUPABASE_URL environment variable is not set.")
    key: str = os.environ.get("SUPABASE_KEY", "SUPABASE_KEY environment variable is not set.")
    supabase: Client = create_client(url, key)
    response = supabase.rpc("delete_all_articles").execute()
    return None

def update_articles_db(articles: List[ArticleSummary]) -> None:
    delete_all_articles_db()
    insert_articles_db(articles)
    return None


def get_articles_db() -> List[ArticleSummary]:

    if dev:
        load_dotenv()

    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")

    supabase: Client = create_client(url, key)

    data: List[ArticleSummary] = supabase.table("articles").select("*").execute()
    return data.data


def get_articles_by_id(ids) -> List[ArticleSummary]:
    if dev:
        load_dotenv()

    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")

    supabase: Client = create_client(url, key)

    response: List[ArticleSummary] = (
        supabase.table("articles")
        .select("*")
        .in_("id", ids)
        .execute()
    )

    return response.data
