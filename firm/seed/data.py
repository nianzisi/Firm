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

SessionLocal = sessionmaker(bind=engine)

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


class User(Base):
    """用户表
    name:
    password: hash
    id: ++
    creat_time:
    token: hash
    token_exist_time:"""
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)  # 主键
    name: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    password: Mapped[bytes] = mapped_column(LargeBinary(255), nullable=False)
    creat_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    token: Mapped[bytes] = mapped_column(LargeBinary(255), nullable=True)
    token_exist_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class Item(Base):
    """物品基础信息表（静态属性）"""
    __tablename__ = "item"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    grade: Mapped[int] = mapped_column(nullable=False, default=1)
    shopping_price: Mapped[Optional[int]] = mapped_column(nullable=True, default=None)  # NULL 表示不可出售

    # 种子
    seed_items: Mapped["Plan_Seed"] = relationship(
        back_populates="item",
        cascade="all, delete-orphan"
    )

    # 关系（一对多）收获物
    reward_associations: Mapped[List["SeedRewardAssociation"]] = relationship(
        back_populates="item",
        cascade="all, delete-orphan"
    )
    # 背包
    backpack_items: Mapped[List["Backpack"]] = relationship(
        back_populates="item",
        cascade="all, delete-orphan"
    )


# ============================================
# 2. 种子奖励关联表（一对多中的"多"方）
# ============================================
class SeedRewardAssociation(Base):
    """种子的奖励配置（一个种子可以有多条奖励）"""
    __tablename__ = 'seed_reward_association'

    id: Mapped[int] = mapped_column(primary_key=True)  # ✅ 加个自增主键，方便管理

    rewards_amount: Mapped[int] = mapped_column(nullable=False)
    rewards_chance: Mapped[float] = mapped_column(nullable=False)

    # 外键
    seed_id: Mapped[int] = mapped_column(ForeignKey('plan_seed.id'), nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey('item.id'), nullable=False)

    # 关系
    seed: Mapped["Plan_Seed"] = relationship(back_populates="rewards")
    item: Mapped["Item"] = relationship(back_populates="reward_associations")

    __table_args__ = (
        UniqueConstraint('seed_id', 'item_id', name='uq_seed_reward'),  # 组合唯一约束
    )


# ============================================
# 3. 种子主表（一对多中的"一"方）
# ============================================
class Plan_Seed(Base):
    """植物种子"""
    __tablename__ = "plan_seed"

    id: Mapped[int] = mapped_column(primary_key=True)
    mature_time: Mapped[int] = mapped_column(nullable=False)
    mature_amount: Mapped[int] = mapped_column(nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    item_id: Mapped[int] = mapped_column(ForeignKey(
        "item.id",
        ondelete='CASCADE'),
        unique=True,
        nullable=False)

    # item
    item: Mapped["Item"] = relationship(back_populates="seed_items")

    # 关系（一对多）
    rewards: Mapped[List["SeedRewardAssociation"]] = relationship(
        back_populates="seed",
        cascade="all, delete-orphan"  # 删除种子时自动删除奖励配置
    )
    firms: Mapped[List["Firm"]] = relationship(
        back_populates="plan_owner",
        cascade="all, delete-orphan"  # 删除种子时自动删除关联的土地
    )


# ============================================
# 4. 土地表
# ============================================
class Firm(Base):
    """土地表"""
    __tablename__ = "firm"

    id: Mapped[int] = mapped_column(primary_key=True)
    level: Mapped[int] = mapped_column(nullable=False, default=0)
    plan_time: Mapped[int] = mapped_column(nullable=False, default=-1)
    extra_amount: Mapped[int] = mapped_column(nullable=False, default=0)

    plan_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("plan_seed.id", ondelete="SET NULL"),  # ✅ 删除种子时，土地保留但 plan_id 置 NULL
        nullable=True,
        default=None
    )

    # 关系
    plan_owner: Mapped[Optional["Plan_Seed"]] = relationship(
        back_populates="firms"
    )


# ============================================
# 5. 背包表
# ============================================
class Backpack(Base):
    """背包"""
    __tablename__ = "backpack"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[int] = mapped_column(nullable=False, default=0)

    item_id: Mapped[int] = mapped_column(ForeignKey("item.id"), nullable=False)

    # 关系
    item: Mapped["Item"] = relationship(back_populates="backpack_items")


if __name__ == "__main__":
    # 创建表

    Base.metadata.drop_all(engine)  # 删除所有表（危险！会清空数据）
    Base.metadata.create_all(engine)
    print("表创建成功！")
