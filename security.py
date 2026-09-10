from datetime import timezone, timedelta, datetime
from jose import jwt
import bcrypt
from database import settings
from jose import jwt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())



def create_access_token(username:str) -> str:
    payload= {
        "sub": username,
        "exp": datetime.now(timezone.utc)+ timedelta(minutes = 30)
    }

    return jwt.encode(payload, settings.secret_key,algorithm="HS256" )

