from pydantic import BaseModel
class ContentCrawlRequest(BaseModel):
    content_url: str
    short_code: str
    content_type: int