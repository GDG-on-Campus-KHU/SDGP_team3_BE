import google.generativeai as genai
from app.config import settings

genai.configure(api_key=settings.GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-pro-vision")

class GeminiService:
    @staticmethod
    def detect_tumbler(image_path: str) -> str:
        with open(image_path, "rb") as img_file:
            prompt = "이 이미지에 텀블러가 포함되어 있습니까? 'Tumbler' 또는 'Not Tumbler'로만 대답하세요."
            response = model.generate_content([prompt, img_file])
            result = response.text.strip()

            if result not in ["Tumbler", "Not Tumbler"]:
                raise ValueError(f"예상하지 못한 응답: {result}")
            return result
