from google.cloud import vision
import io
from google.cloud import vision
from typing import Literal

from difflib import get_close_matches

client = vision.ImageAnnotatorClient()

def detect_spoon_fork_from_image(image_path: str) -> Literal["O", "X"]:
    """
    이미지에서 '(수저, 포크 O)' 또는 '(수저, 포크 X)'가 포함돼 있는지 분석해 결과를 반환
    param image_path: 이미지 파일 경로
    return: 'O', 'X'
    """
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)

    if not response.text_annotations:
        return "X"  # 아무 텍스트도 인식 안됐을 때

    full_text = response.text_annotations[0].description  # 전체 텍스트 덩어리
    normalized = full_text.replace(" ", "").strip()  # 공백 제거 및 정리

    if "수저,포크O" in normalized or "수저포크O" in normalized:
        return "O"
    elif "수저,포크X" in normalized or "수저포크X" in normalized:
        return "X"

    return "Unknown"  # 기본 fallback


def detect_tumbler_in_image(image_path: str) -> Literal["O", "X"]:
    """이미지에 텀블러가 있는지 분석"""
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
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