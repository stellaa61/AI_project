from fastapi import Depends, Body, HTTPException, status, APIRouter
from sqlalchemy import select

from auth.password import hash_password, verify_password
from auth.jwt import create_access_token, verify_user
from fastapi.security import HTTPBearer
from database.connection import get_session
from database.orm import User, HealthProfile
from request import SignUpRequest, LogInRequest, HealthProfileCreateRequest
from response import UserResponse, LogInResponse, HealthProfileResponse


router = APIRouter(tags=["User"])

@router.post(
    "/users",
    summary="회원가입 API",
    #status_code=201,
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,

)
async def signup_handler(
 
    body: SignUpRequest = Body(...),
    session = Depends(get_session),
):
    
        # [1] email 중복 검사
        stmt = select(User).where(User.email == body.email)
        user = await session.scalar(stmt)

        if user:
            raise HTTPException(status_code=409, detail="email already exists")

        # [2] 비밀번호 해싱 (hashing)
        new_user = User(
            email=body.email,
            password_hash=hash_password(plain_password=body.password),
        )

        # [3] 데이터 저장 새로운 유저 데이터 추가
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user) # 데이터베이스에서 id/created_at 을 읽어온다.

        # new_user에 이미 id/password 다 지정되어있다.
        return new_user

@router.delete(
    "/users",
    summary="회원탈퇴 API",
    status_code=status.HTTP_204_NO_CONTENT,
)

async def delete_user_handler(
    user_id: int = Depends(verify_user),
    session = Depends(get_session),
):
    # [1] user 조회
    stmt = select(User).where(User.id == user_id)
    user = await session.scalar(stmt)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    
    
    # [2] DB에서 삭제
    # HealthProfile 삭제

    # Hard Delete: FK 제약 ondelete="CASCADE" 속성을 이용해서 연관 객체 자동 삭제
    # await session.delete(user)
    # await session.commit()
    
    # [3] Soft Delete: email/password hash만 삭제 나머지 기록은 유지.(수정)/ 실제 데이터를 삭제하지 않고 개인정보 마스킹
    user.soft_delete()
    await session.commit()



@router.post(
    "/user/login",
    summary="로그인 API",
    status_code=status.HTTP_200_OK,
    response_model=LogInResponse,
)
async def login_handler(
    body: LogInRequest = Body(...),
    session = Depends(get_session), # 데이터베이스 필요
):
    # [1] email로 사용자 조회
    stmt = select(User).where(User.email == body.email)
    user: User | None = await session.scalar(stmt)

    if not user: 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user not found"
        )
    # [2] body.password & user.passhash 비교 -> 맞는지 확인
    verified = verify_password(plain_password=body.password, password_hash=user.password_hash)
    if not verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorised")
    
    # [3] 로그인 처리 
    access_token = create_access_token(user_id=user.id)
    return {"access_token": access_token}

# 1. Path ->
# 2. Query Parameter ->
# 3. RequestBody ->
# 4. Header -> meta data

http_bearer = HTTPBearer()


# 토큰   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiZXhwIjoxNzczMjgyODYyfQ.t1aOpyFHEkJhx8A6xU5S90yer80gaDZv9ybIbz57cKU


# 프로필 변경
# 1) 프로필 처음 생성 -> 생성
# 2) 프로필 변경 -> 수정
#@app.patch("/health-profiles")

# 프로필 생성
@router.post(
    "/health-profiles",
    summary="건강 프로필 생성 API",
    status_code=status.HTTP_201_CREATED,
    response_model=HealthProfileResponse
)
async def create_health_profile_handler(
    user_id: int = Depends(verify_user), # 인증요구 api로 만들기
    body: HealthProfileCreateRequest = Body(...),
    session = Depends(get_session),
):
    # [1] 생성 전 프로필 중복 검사 유무 검사
    stmt = select(HealthProfile).where(HealthProfile.user_id == user_id)
    exsiting = await session.scalar(stmt)
    if exsiting:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="health profile already exists",
        )
    
    # [2] HealthProfile 객체 생성
    profile_data = body.model_dump()    # 데이터들을 딕셔너리로 변경 -> 그 딕셔너리로 정보를 받기 위해서 사용/아님 매번 모든 정보를 다 넣어줘야함
    new_profile = HealthProfile(user_id=user_id, **profile_data)

    # [3] DB 저장
    session.add(new_profile)
    await session.commit()
    await session.refresh(new_profile)
    return new_profile

