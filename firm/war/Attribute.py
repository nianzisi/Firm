from functools import wraps
from typing import Optional, List

from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, DateTime, ForeignKey, Computed, \
    UniqueConstraint, event
from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column, relationship, validates

from datetime import datetime

from commomd.mind import Base, DATABASE_URL


class Player(Base):
    """

    """
    __tablename__ = "player"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)  # 主键
    name: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)

    # 四维
    GenGu: Mapped[int] = mapped_column(LargeBinary(255), nullable=False)
    BiLi: Mapped[int] = mapped_column(LargeBinary(255), nullable=False)
    MingJie: Mapped[int] = mapped_column(LargeBinary(255), nullable=False)
    WuXing: Mapped[int] = mapped_column(LargeBinary(255), nullable=False)

    level: Mapped[int] = mapped_column(LargeBinary(255), nullable=False)
    CurrentEXP: Mapped[int] = mapped_column(LargeBinary(255), nullable=False)

    @validates("GenGu", "BiLi", "MingJie", "WuXing", "level")
    def test(self, key, value) -> int:
        if key == "level":
            return min(100, value)
        return max(0, min(255, value))

    @event.listens_for(Player,"after_insert")
    # 实例级别事件
    # @event.listens_for(Player, 'before_insert')  # 插入前
    # @event.listens_for(Player, 'after_insert')  # 插入后
    # @event.listens_for(Player, 'before_update')  # 更新前
    # @event.listens_for(Player, 'after_update')  # 更新后
    # @event.listens_for(Player, 'before_delete')  # 删除前
    # @event.listens_for(Player, 'after_delete')  # 删除后
    # @event.listens_for(Player, 'load')  # 从数据库加载后
    #
    # # 会话级别事件
    # @event.listens_for(Session, 'before_commit')  # 提交前
    # @event.listens_for(Session, 'after_commit')  # 提交后
    # @event.listens_for(Session, 'before_flush')  # 刷新前
    # @event.listens_for(Session, 'after_flush')  # 刷新后
