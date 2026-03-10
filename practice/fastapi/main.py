from fastapi import FastAPI

app = FastAPI()

# def hello_world():
#     return {"msg": "hello_world"}

# 서버에 GET("루트경로") 요청이 들어오면, root_handler를 실행한다.
# @app.get("/hello")
# def root_handler():
#     return hello_world()

users = [
    {"id": 1, "name": "alex"},  # [0]
    {"id": 2, "name": "bob"},   # [1]
    {"id": 3, "name": "chris"}, # [2]
]

# 전체 사용자 조회 API -> users 사용
@app.get("/users")
def get_users_handler():
    return users

# 단일 사용자 조회 API 
# method/ 상위/하위(식별자)
# GET /users/1
# GET /users/2

@app.get("/users/1")
def get_first_hadler():
    return users[0]
# 근데 너무 하나에만 확정지어있어서 계속 수정해줘야함
# -> 공통속성 뽑아서 변수로 받아 자동으로 바뀌게 코드 짜기 (first->users/[index no.]-> [user_id -1])

# {users_id}번 사용자 조회
# Path(경로) + {}: 매개변수(parameter)

# Path Parameter에 type hint를 추가 (int/str...) 
# -> 명시한 타입에 맞는지 검사 & 보장(무조건 그 타입으로 받아야할 때 사용)

@app.get("/{users_id}")             # 이 경로에서 변수로 받아
def get_users_hadler(users_id: int):     # 이 함수에서 받아서
    return users[users_id - 1]      # 적용하여 결과 출력

