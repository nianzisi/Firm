"""数据"""
from functools import wraps

from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, DateTime, ForeignKey, Computed
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
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    password: Mapped[bytes] = mapped_column(LargeBinary(255), nullable=False)
    creat_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    token: Mapped[bytes] = mapped_column(LargeBinary(255), nullable=True)
    token_exist_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class Plan_Seed(Base):
    """植物种子
    id:
    plan_name:名称
    plan_grade:1->2->3->4->5…………品质等级
    mature_time:成长时间
    mature_amount:数量
    comment:备注"""

    __tablename__ = "plan_seed"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)  # 主键
    plan_name: Mapped[str] = mapped_column(String(20), nullable=False)
    plan_grade: Mapped[int] = mapped_column(nullable=False, default=1)
    mature_time: Mapped[int] = mapped_column(nullable=False)
    mature_amount: Mapped[int] = mapped_column(nullable=False)
    comment: Mapped[str] = mapped_column(String(255), nullable=True)

    seed_owner: Mapped[list["Plan_Seed_Rewards"]] = relationship("Plan_Seed_Rewards",
                                                                 secondary='seed_reward_association',
                                                                 back_populates="rewards_owner")
    firm_owner: Mapped[list["Firm"]] = relationship("Firm", back_populates="plan_owner")


class SeedRewardAssociation(Base):
    """ Plan_Seed与Plan_Seed_Rewards的关联表
    rewards_amount:数量
    rewards_chance:概率
    """
    __tablename__ = 'seed_reward_association'

    seed_id: Mapped[int] = mapped_column(ForeignKey('plan_seed.id'), primary_key=True)
    reward_id: Mapped[int] = mapped_column(ForeignKey('plan_seed_rewards.id'), primary_key=True)
    rewards_amount: Mapped[int] = mapped_column(nullable=False)
    rewards_chance: Mapped[float] = mapped_column(nullable=False)


class Plan_Seed_Rewards(Base):
    """植物收获物品
    id:
    rewards_name:名称
    rewards_grade:品阶"""

    __tablename__ = "plan_seed_rewards"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)  # 主键
    rewards_name: Mapped[str] = mapped_column(String(20), nullable=False)
    rewards_grade: Mapped[int] = mapped_column(nullable=False, default=1)


    rewards_owner: Mapped[list["Plan_Seed"]] = relationship("Plan_Seed",
                                                            secondary='seed_reward_association',
                                                            back_populates="seed_owner")


class Firm(Base):
    """土地表
    id:
    level:
    plan_id:
    plan_time:
    extra_amount: 额外收获倍率
    extra_mature: 额外生长速率"""

    __tablename__ = "firm"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)  # 主键
    level: Mapped[int] = mapped_column(nullable=False, default=0)
    plan_time: Mapped[int] = mapped_column(nullable=False, default=-1)
    extra_amount: Mapped[int] = mapped_column(nullable=False, default=0)

    plan_id: Mapped[int | None] = mapped_column(ForeignKey("plan_seed.id", ), nullable=True, default=None)
    plan_owner = relationship("Plan_Seed", back_populates="firm_owner")


class Backpack(Base):
    """背包
    id：
    name：
    amount：
    """
    __tablename__ = "backpack"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)  # 主键
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[int] = mapped_column(nullable=False, default=0)


    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)
    # 关联物品基础信息
    item: Mapped["Item"] = relationship(back_populates="backpack_items")


class Item(Base):
    """物品基础信息表（静态属性）
        shopping：None 未不可出售，数字为价格"""
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    grade: Mapped[int] = mapped_column(nullable=False, default=1)
    shopping_price: Mapped[int] = mapped_column(nullable=True)  # NULL表示不可出售

    # 关联背包记录
    backpack_items: Mapped[list["Backpack"]] = relationship(back_populates="item", cascade="all, delete-orphan")



if __name__ == "__main__":
    # 创建表
    Base.metadata.create_all(engine)
    # Base.metadata.drop_all(engine)  # 删除所有表（危险！会清空数据）
    print("表创建成功！")
