from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, computed_field



class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime


class LogInResponse(BaseModel):
    access_token: str

class HealthProfileResponse(BaseModel):
    id: int
    user_id: int
    age: int
    height_cm: float
    weight_kg: float
    smoking: bool
    exercise_per_week: int

class HealthRiskPredictionResponse(BaseModel):
    id: int
    user_id: int
    diabates_probability: float
    hypertension_probability: float
    # 모델 버전 -> 클라이언트에게 공개 하지 않을 수 있다.
    created_at: datetime
    #created_at_kst: datetime

    @computed_field
    @property
    def created_at_kst(self) -> datetime:
        KST = timezone(timedelta(hours=9))

        # UTC시간을 KST(+09:00)로 변환
        return self.created_at.astimezone(KST)

