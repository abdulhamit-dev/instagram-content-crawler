import requests
import cv2
import tempfile
import os
from datetime import datetime

from models.content_crawl_request import ContentCrawlRequest
from models.download_type_enum import DownloadType
from models.media_data import MediaData
from models.media_download_result import MediaDownloadResult
from models.content_type_enum import ContentType


class MediaService:
    def __init__(self):
        self.host = "rocketapi-for-instagram.p.rapidapi.com"
        self.key = "xyz" # replace with your own key rocketapi
        self.base_url = "https://rocketapi-for-instagram.p.rapidapi.com/instagram/media"

    def get_media_data(self, request:ContentCrawlRequest):

        json_data = self.get_ig_media(request)
        items = json_data['response']['body']['items']
        for item in items:
            media_download_url = None
            media_download_type = None
            video_versions = item.get('video_versions', [])
            if video_versions:
                for version in video_versions:
                    media_download_url = version.get('url')
                    media_download_type=DownloadType.VIDEO
                    break
            else:
                image_versions = item.get('image_versions2', {}).get('candidates', [])
                if image_versions:
                    media_download_url = image_versions[0].get('url')
                    media_download_type = DownloadType.IMAGE

            owner_item = item.get('owner', {})
            account_name = owner_item.get('username')
            created_at = item.get('taken_at')
            share_date = datetime.fromtimestamp(created_at)

            return MediaData(media_download_url, account_name, share_date,media_download_type)

    def get_ig_media(self, request:ContentCrawlRequest):
        headers = {
            'Content-Type': 'application/json',
            'x-rapidapi-host': self.host,
            'x-rapidapi-key': self.key
        }

        short_code_or_id = request.short_code

        content_type = ContentType(request.content_type)

        if content_type == ContentType.REEL:
            endpoint="/get_info_by_shortcode"
            payload = {
                'shortcode': short_code_or_id
            }
        else:
            endpoint="/get_info"
            payload = {
                'id': short_code_or_id
            }

        response = requests.post(url=f"{self.base_url}{endpoint}", headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code

    def download_media(self,content_url,media_type: ContentType,short_code,is_video=True):
        media_upload_date = datetime
        current_date = datetime.now().strftime("%d%m%Y")
        extension = "mp4" if is_video else "jpg"
        temp_content_path = os.path.join(tempfile.gettempdir(),
                                         f"{media_type.name.lower()}_{short_code}_{current_date}.{extension}")
        content_stream = requests.get(content_url, stream=True)

        with open(temp_content_path, 'wb') as temp_video:
            for chunk in content_stream.iter_content(chunk_size=1024):
                if chunk:
                    temp_video.write(chunk)

        return MediaDownloadResult(temp_content_path, media_upload_date)

    def extract_frames(self,video_path,short_code):
        cap = cv2.VideoCapture(video_path)
        frames_paths = []
        date = datetime.now().strftime("%d%m%Y")
        temp_dir = tempfile.gettempdir()
        try:
            if not cap.isOpened():
                raise ValueError("Failed to open video file.")

            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            frame_number = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
                if abs(current_time - round(current_time)) < 0.1:
                    frame_filename = f"frame_{short_code}_{date}_{frame_number}.jpg"
                    frame_path = os.path.join(temp_dir, frame_filename)
                    cv2.imwrite(frame_path, frame)
                    frames_paths.append(frame_path)
                frame_number += 1
        except Exception as e:
            print(f"An error occurred during frame extraction: {str(e)}")
        finally:
            cap.release()

        return frames_paths