from openai import AsyncOpenAI
from pydantic import BaseModel

from config import settings
from database.orm import HealthProfile

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

class RiskPredictionResult(BaseModel):
    diabates_probability: float
    hypertention_probability: float


async def predict_health_risk(profile: HealthProfile, model_version: str) -> RiskPredictionResult:
    prompt = f"""
    다음 건강 정보를 기반으로 당뇨와 고혈압의 위험도를 0과 1사이로 계산하세요.

    age: {profile.age}
    height_cm: {profile.height_cm}
    weight_kg: {profile.weight_kg}
    smoking: {profile.smoking}
    exercise_per_week: {profile.exercise_per_week}
    """

    response = await client.responses.parse( #parse: AI 응답을 지정한 형식(클래스)으로 자동 변환해주는 기능
        model=model_version,
        input=prompt,
        text_format=RiskPredictionResult
    )

    return response.output_parsed