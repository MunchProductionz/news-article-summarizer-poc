from typing import List, Optional
from typing_extensions import TypedDict
from datetime import datetime

# Article Objects
class ArticleInfo(TypedDict):
    date_time: datetime
    category: str
    title: str
    url: str
    
class ArticleInfoLeadText(TypedDict):
    date_time: datetime
    category: str
    title: str
    url: str
    lead_text: str

class ArticleInfoContent(TypedDict):
    date_time: datetime
    category: str
    title: str
    url: str
    lead_text: str
    content: str

class ArticleSummary(TypedDict):
    date_time: datetime
    category: str
    title: str
    url: str
    lead_text: str
    content: str
    summary: str
    bullet_points: str

# OpenAI Chat Completion API Response
class MessageDict(TypedDict):
    role: str
    content: str

class ChoiceDict(TypedDict):
    index: int
    message: MessageDict
    logprobs: Optional[None]
    finish_reason: str

class UsageDetailsDict(TypedDict):
    reasoning_tokens: int

class UsageDict(TypedDict):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    completion_tokens_details: UsageDetailsDict

class ChatCompletionResponse(TypedDict):
    id: str
    object: str
    created: int
    model: str
    system_fingerprint: str
    choices: List[ChoiceDict]
    usage: UsageDict