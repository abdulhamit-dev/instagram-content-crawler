from crawl_service import CrawlService
from models.content_crawl_request import ContentCrawlRequest

def main():
    request = ContentCrawlRequest(
        content_url="https://www.instagram.com/stories/user/123455/", 
        short_code="123455", 
        content_type=1)
    crawl_service = CrawlService()
    data = CrawlService.crawl_instagram_content(crawl_service, request)
    print(data)

if __name__ == "__main__":
    main()