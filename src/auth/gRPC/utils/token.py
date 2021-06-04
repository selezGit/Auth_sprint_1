from typing import Dict, Tuple
import datetime
import os
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.no_sql_db import add_refresh_token, add_to_blacklist, del_refresh_token
from core.config import settings


def create_access_token(payload: Dict) -> Tuple[datetime, datetime, bytes]:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=15)
    expire = expire.timestamp()
    now = now.timestamp()
    payload['now'] = now
    payload['expire'] = expire
    access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return (now, expire, access_token,)


def create_refresh_token(payload: Dict) -> Tuple[datetime, datetime, bytes]:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=7)
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
