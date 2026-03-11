import re
from pydantic import BaseModel, EmailStr, Field, field_validator


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        ..., 
        json_schema_extra={"example": "Password123"}
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        if len(v) < 8:
            raise ValueError("패스워드는 8자리 이상이어야 합니다.")
        
        if not re.search(r"[A-Z]", v):
            raise ValueError("패스워드는 대문자를 포함해야 합니다.")
        
        if not re.search(r"[0-9]", v):
            raise ValueError("패스워드는 숫자를 포함해야 합니다.")

        return v
    
# 이메일(사용자 식별 도구, 값) / 비밀번호 받기
class LogInRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., json_schema_extra={"example": "Password123"})

# 전체 사용자 -> 재설정 안내 w.마감 기한
# {id: 1, password: string, email: ...}

class HealthProfileCreateRequest(BaseModel):
    age: int
    height_cm: float
    weight_kg: float
    smoking: bool
    exercise_per_week: int
