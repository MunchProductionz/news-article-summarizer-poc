from summarizer import summmarizer
from fastapi import Request, FastAPI
from loguru import logger
from typing import Dict
import uvicorn
from db import get_articles_db
from pydantic import BaseModel
from typing import List

app = FastAPI()

@app.get('/')
def hello_world():
    return "Hello,World"


@app.get('/articles')
def get_articles():
    return get_articles_db()


class SendEmailInput(BaseModel):
    ids: List[str]
    mail: str

@app.post('/send_mail')
async def send_mail(send_email_input: SendEmailInput):

    ids = send_email_input.ids
    mail = send_email_input.mail

    msg = await summmarizer(ids, mail)

    res = {
        "ids": ids,
        "msg": msg
    }

    return res


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)