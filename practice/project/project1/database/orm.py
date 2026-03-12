from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, Integer, Float, Boolean, func, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, with_loader_criteria

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"

    # 저장할 데이터 목록: 아이디, 이름, 비번, 닉네임 등등
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    # 사용자가 회원가입한 시간
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False,
    )
    # Soft Delete일 경우
    # 사용자가 삭제한 시간
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def soft_delete(self):
        self.email = f"deleted_user:{self.id}"
        self.deleted_at = datetime.now(tz=timezone.utc)

# User를 불러올 때, deleted_at !=NULL인 데이터는 제외
# @event.listens_for(Session, "do_orm_execute")
# def _add_filtering_criteria(execute_state):

#     execute_state.statment = execute_state.statement.options(
#         with_loader_criteria(
#             User,
#             lambda cls: cls.deleted_at.is_(None),
#             include_aliases=True,
#         )
#     )

@event.listens_for(Session, "do_orm_execute")
def _add_filtering_criteria(execute_state):

    if execute_state.is_select:

        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                User,
                lambda cls: cls.deleted_at.is_(None),
                include_aliases=True,
            )
        )

class HealthProfile(Base):
    __tablename__ = "health_profile"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), # user(부모)가 삭제되면 profile(자식)도 함께 자동 삭제
        unique=True, 
        nullable=False
    ) # null을 허용하지 않는다. = 반드시 유저아이디가 있어야한다.

    age: Mapped[int] = mapped_column(Integer)
    height_cm: Mapped[float] = mapped_column(Float)
    weight_kg: Mapped[float] = mapped_column(Float)
    smoking: Mapped[bool] = mapped_column(Boolean)
    exercise_per_week: Mapped[int] = mapped_column(Integer)

# 결과 저장 클래스
class HealthRiskPrediction(Base): 
    __tablename__ = "health_risk_prediction"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False) # prediction은 여러번 해도 되니까 unique 사용 x
    # 당뇨병 위험도
    diabates_probability: Mapped[float] = mapped_column(Float)
    # 고혈압 위험도
    hypertension_probability: Mapped[float] = mapped_column(Float)

    model_version: Mapped[str] = mapped_column(String(50)) # string: 최대 길이 50자
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiZXhwIjoxNzczMzY4MTkyfQ.zzMs1Z4Epcr3iuF9O8xXYRqeeTXfFQ59DWJc1g1l0Rs