import datetime
from datetime import datetime, timedelta, timezone
from typing import Dict, Tuple

import jwt
from core.config import settings


def create_access_token(payload: Dict, time=None) -> Tuple[datetime, datetime, str]:
    now = datetime.now(timezone.utc)
    delta = time or timedelta(minutes=15)
    expire = now + delta
    expire = expire.timestamp()
    now = now.timestamp()
    payload['now'] = now
    payload['expire'] = expire
    access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return (now, expire, access_token,)


def create_refresh_token(payload: Dict, time=None) -> Tuple[datetime, datetime, str]:
    now = datetime.now(timezone.utc)
    delta = time or timedelta(days=7)
    expire = now + delta
    expire = expire.timestamp()
    now = now.timestamp()
    payload['now'] = now
    payload['expire'] = expire
    refresh_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return (now, expire, refresh_token,)


def decode_token(token: str) -> Dict:
    return jwt.decode(token, key=settings.SECRET_KEY, algorithms='HS256')


def check_expire(expire: str) -> bool:
    now = datetime.now(timezone.utc)
    now = now.timestamp()
    if now > float(expire):
        return False
    return True
