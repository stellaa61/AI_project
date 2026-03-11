from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Integer, Float, Boolean, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"

    # 저장할 데이터 목록: 아이디, 이름, 비번, 닉네임 등등
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    # 사용자가 회원가입한 시간
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False,
    )

class HealthProfile(Base):
    __tablename__ = "health_profile"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True, nullable=False) # null을 허용하지 않는다.= 반드시 유저아이디가 있어야한다.

    age: Mapped[int] = mapped_column(Integer)
    height_cm: Mapped[float] = mapped_column(Float)
    weight_kg: Mapped[float] = mapped_column(Float)
    smoking: Mapped[bool] = mapped_column(Boolean)
    exercise_per_week: Mapped[int] = mapped_column(Integer)


class HealthRiskPrediction(Base):
    __tablename__ = "health_risk_prediction"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False) # prediction은 여러번 해도 되니까 unique 사용 x
    # 당뇨병 위험도
    diabates_probability: Mapped[float] = mapped_column(Float)
    # 고혈압 위험도
    hypertension_probability: Mapped[float] = mapped_column(Float)

    model_version: Mapped[str] = mapped_column(String(50)) # string: 최대 길이 50자
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
