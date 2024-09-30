import os
import cv2
from urllib.parse import urlparse
from typing import List

from models.matched_image import MatchedImage


class ImageProcessingService:

    def __init__(self):
        pass

    def search_logos_in_images(self, crawl_image_paths : List[str], min_match_count=10):
        treshold_for_return = 90 # %90 match ratio is enough to return
        true_images_dir = os.path.join(os.path.dirname(__file__), 'true_images')
        true_image_paths = []
        for file_name in os.listdir(true_images_dir):
            if file_name.endswith('.jpeg'):
                true_image_paths.append(os.path.join(true_images_dir, file_name))

        CandidateMatchedImageInfos = []

        for crawl_image_path in crawl_image_paths:
            for index, true_image_path in enumerate(true_image_paths):
                large_image = cv2.imread(crawl_image_path, cv2.IMREAD_GRAYSCALE)
                small_image = cv2.imread(true_image_path, cv2.IMREAD_GRAYSCALE)
                sift = cv2.SIFT_create()
                kp1, des1 = sift.detectAndCompute(small_image, None)
                kp2, des2 = sift.detectAndCompute(large_image, None)
                FLANN_INDEX_KDTREE = 1
                index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
                search_params = dict(checks=50)
                flann = cv2.FlannBasedMatcher(index_params, search_params)

                matches=[]
                if des1 is not None and des2 is not None:
                    matches = flann.knnMatch(des1, des2, k=2)

                good_matches = []
                for m, n in matches:
                    if m.distance < 0.7 * n.distance:
                        good_matches.append(m)

                        total_matches = len(matches)
                        successful_match_ratio = len(good_matches) / total_matches

                        if len(good_matches) > min_match_count:
                            current = MatchedImage(crawl_image_path, successful_match_ratio * 100)
                            if(current.successful_match_ratio >= treshold_for_return):
                                return current

                            CandidateMatchedImageInfos.append(current)
        image_info_with_highest_match_score = self.find_max_successful_match_ratio(CandidateMatchedImageInfos)
        return image_info_with_highest_match_score

    def find_max_successful_match_ratio(self, CandidateMatchedImageInfos):
        max_ratio = None
        max_info = None

        for info in CandidateMatchedImageInfos:
            if max_ratio is None or info.successful_match_ratio > max_ratio:
                max_ratio = info.successful_match_ratio
                max_info = info

        return max_info
