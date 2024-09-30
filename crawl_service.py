import os
from media_service import MediaService
from image_processing_service import ImageProcessingService
from models.content_crawl_request import ContentCrawlRequest
from models.content_type_enum import ContentType
from models.download_type_enum import DownloadType
from models.response_model import ResponseModel

class CrawlService:
    def __init__(self):
        self.image_processing_service = ImageProcessingService()
        self.media_service = MediaService()

    def crawl_instagram_content(self, request:ContentCrawlRequest):
        try:
            content_type = ContentType(request.content_type)

            media_data = self.media_service.get_media_data(request)
            if media_data.download_type == DownloadType.VIDEO:
                media_download_result = self.media_service.download_media(media_data.video_url, content_type, request.short_code)
            else:
                media_download_result = self.media_service.download_media(media_data.video_url, content_type,request.short_code, False)

            frames = []
            if media_data.download_type==DownloadType.VIDEO:
                frames = self.media_service.extract_frames(media_download_result.file_path,request.short_code)
            else:
                frames.append(media_download_result.file_path)

            matched_image_info = self.image_processing_service.search_logos_in_images(frames)

            os.remove(media_download_result.file_path)

            if matched_image_info:
                print("Matched image found")
                return ResponseModel(success=True, data={"message": "Matched image found"})
            else:
                return ResponseModel(success=False, data={"message": "No matched image found"})
            
        except Exception as e:
            return ResponseModel(success=False, data={"message": str(e)})

