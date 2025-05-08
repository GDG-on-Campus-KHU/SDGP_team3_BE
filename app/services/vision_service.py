from difflib import get_close_matches
from typing import Literal

from fastapi import UploadFile
from google.cloud import vision

# 기존 client = vision.ImageAnnotatorClient() 대신 다음과 같이 수정
client = vision.ImageAnnotatorClient()
print(f"client: {client.__dict__}")
"""Google Cloud Vision API 클라이언트 초기화"""


class VisionService:
    """VisionService는 Google Cloud Vision API를 사용하여 이미지 분석을 수행하는 서비스입니다."""

    @staticmethod
    def detect_spoon_fork_from_image(file: UploadFile) -> Literal["O", "X", "Unknown"]:
        """
        이미지에서 '(수저, 포크 O)' 또는 '(수저, 포크 X)'가 포함돼 있는지 분석해 결과를 반환
        param image_path: 이미지 파일 경로
        return: 'O', 'X'
        """
        image = vision.Image(content=file.file.read())
        response = client.text_detection(image=image)

        if not response.text_annotations:
            return "X"  # 아무 텍스트도 인식 안됐을 때

        full_text = response.text_annotations[0].description  # 전체 텍스트 덩어리
        normalized = full_text.replace(" ", "").strip()  # 공백 제거 및 정리
        print("정규화된 텍스트:", normalized)

        if "수저,포크O" in normalized or "수저포크O" in normalized:
            return "O"
        elif "수저,포크X" in normalized or "수저포크X" in normalized:
            return "X"

        return "Unknown"  # 기본 fallback

    @staticmethod
    def detect_tumbler_in_image(file: UploadFile) -> Literal["Tumbler", "Not Tumbler"]:
        """이미지에 텀블러가 있는지 분석"""
        image = vision.Image(content=file.file.read())
        response = client.label_detection(image=image)
        labels = [label.description.lower() for label in response.label_annotations]

        print("라벨 결과 목록:", labels)

        # 2차 수정
        tumbler_keywords = ["tumbler", " bottle", "water bottle", "drinkware"]

        if any(label in tumbler_keywords for label in labels):
            return "Tumbler"

        for label in labels:
            similar = get_close_matches(label, tumbler_keywords, n=1, cutoff=0.8)
            if similar:
                return "Tumbler"
        # 1차
        # for label in labels:
        #     if "tumbler" in label or "bottle" in label or "water bottle" in label:
        #         return "Tumbler"

        return "Not Tumbler"
