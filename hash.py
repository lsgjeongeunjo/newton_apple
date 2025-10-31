from passlib.context import CryptContext

# CryptContext를 사용하여 bcrypt 알고리즘으로 해싱을 설정합니다.
# 'bcrypt'는 비밀번호 해싱에 가장 널리 사용되고 안전한 알고리즘입니다.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    주어진 비밀번호를 해싱하여 반환합니다.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    평문 비밀번호와 해싱된 비밀번호를 비교하여 일치 여부를 반환합니다.
    """
    return pwd_context.verify(plain_password, hashed_password)


