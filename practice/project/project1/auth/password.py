import bcrypt

# 회원가입할 때, 비밀번호 해시를 생성하는 함수
def hash_password(plain_password: str) -> str:
    password_hash_bytes: bytes = bcrypt.hashpw(
        plain_password.encode(),
        bcrypt.gensalt(),
    ) 
    return password_hash_bytes.decode()

# 로그인할 때, 비밀번호를 검증하는 함수
def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode(), password_hash.encode()
        )
    except Exception:
        return False