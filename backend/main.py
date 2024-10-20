from models import ArticleSummary
from typing import List
from db import update_articles_db
from get_articles_tradewinds import get_articles_from_tradewinds
import time

def main():
    
    start = time.time()
    hours_ago = 24
    try:
        articles: List[ArticleSummary] = get_articles_from_tradewinds(hours_ago)
    except Exception as e:
        print(e)
        return None
    end_get_articles = time.time()
    try:
        update_articles_db(articles)
    except Exception as e:
        print(e)
        return None
    end = time.time()
    print(f"Time taken to get articles: {end_get_articles - start}")
    print(f"Time taken to update articles: {end - end_get_articles}")
    print(f"Total time taken: {end - start}")
    
if __name__ == "__main__":
    main()