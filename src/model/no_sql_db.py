# flask_app/no_sql_db.py
import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
redis_db = redis.Redis(host='localhost', port=6379, db=0)