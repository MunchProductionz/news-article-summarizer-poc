import requests

def get_articles():
    url = "https://news-article-summarizer-poc.vercel.app/articles"

    # Fetch the data from the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        return data
        
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

        return []
    

def send_email(ids, mail):
    url = "https://news-article-summarizer-poc.vercel.app/send_mail"
    payload = {"ids": ids, "mail": mail}
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        return response.json()  
    else:
        return {"error": response.text}  
