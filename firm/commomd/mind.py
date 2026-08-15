"""数据"""
from functools import wraps
from typing import Optional, List

from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, DateTime, ForeignKey, Computed, \
    UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column, relationship

from datetime import datetime

# 1. 准备数据库连接 (格式: mysql+pymysql://用户名:密码@主机:端口/数据库名)
DATABASE_URL = "mysql+pymysql://root:@127.0.0.1:3306/planfirm"
engine = create_engine(DATABASE_URL, echo=False)  # echo=True 会在控制台打印 SQL 语句

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

# 2. 定义 ORM 基类
Base = declarative_base()


def with_db(func):
    """装饰器：自动管理数据库session，并注入到函数的 db 参数中"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'db' in kwargs and kwargs['db'] is not None:
            return func(*args, **kwargs)  # 复用外部 session
        db = SessionLocal()  # 创建新session
        try:
            result = func(*args, db=db, **kwargs)  # 注入db
            db.commit()  # 正常执行则提交
            return result
        except Exception:
            db.rollback()  # 异常则回滚
            raise  # 重新抛出异常
        finally:
            db.close()  # 确保关闭

    return wrapper


print("war/mind.py 中的 Base 地址:", id(Base))
