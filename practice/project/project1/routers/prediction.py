from enum import StrEnum

from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy import select

from auth.jwt import verify_user
from database.connection import get_session
from database.orm import HealthProfile, HealthRiskPrediction
from llm import predict_health_risk
from response import HealthRiskPredictionResponse


router = APIRouter(tags=["Prediction"])

@router.post(
    "/predictions",
    summary="당뇨병/고혈압 위험도 예측 API",
    status_code=status.HTTP_201_CREATED,
    response_model=HealthRiskPredictionResponse,
)
async def risk_predict_handler(
    user_id: int = Depends(verify_user),
    session = Depends(get_session),
):
    
    # [1] HealthProfile 조회
    stmt = select(HealthProfile).where(HealthProfile.user_id ==user_id)
    profile = await session.scalar(stmt)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="health profile not found",
        )

    # [2] profile로 위험도 예측 -> OpenAI API
    model_version="gpt-5-mini"
    risk_prediction = await predict_health_risk(profile=profile, model_version=model_version)

    # [3] 결과(prediction) 저장
    new_prediction = HealthRiskPrediction(
        user_id=user_id,
        diabates_probability=risk_prediction.diabates_probability,
        hypertension_probability = risk_prediction.hypertention_probability,
        model_version=model_version,
    )
    session.add(new_prediction)
    await session.commit()
    await session.refresh(new_prediction)

    return new_prediction

# 문서에 표기하고 싶을 때
class QuerySort(StrEnum):
    OLDEST = "oldest"
    LATEST = "latest"


@router.get(
    "/prediction",
    summary="내 건강 위험 예측 결과 조회 API",
    status_code=status.HTTP_200_OK,
    response_model=list[HealthRiskPredictionResponse],
)

async def get_my_risk_predictions_handler(
    sort: QuerySort = Query(QuerySort.OLDEST),
    user_id: int = Depends(verify_user), # 내가 맞는지 검증 후(사용자식별) 내 정보 접근 
    session = Depends(get_session)       # DB 접근
):
    # [1] DB에서 HealthRiskPrediction조회
    # 가능하지만 좋지 않은 방법 -> 모든 Query를 고쳐야함
    # stmt = (
    #     select(HealthRiskPrediction)
    #     .join(User)
    #     .where(
    #         User.deleted_at.is_(None),
    #         HealthRiskPrediction.user_id == user_id
    #     )
    # )
    stmt = (
        select(HealthRiskPrediction)
        .where(HealthRiskPrediction.user_id == user_id)
    )

    # 최신순 정렬(N->1)
    if sort == QuerySort.LATEST:
        stmt = stmt.order_by(HealthRiskPrediction.id.desc())
    
    # 순차 정렬(1->N)
    else:
        stmt = stmt.order_by(HealthRiskPrediction.id)

    result = await session.scalars(stmt)
    predictions = result.all()


    # [2] 응답
    return predictions