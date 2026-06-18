"""土地种植规则
    涉及到提交的，由调用端统一传入db
    仅查询可以直接忽略db传入"""
import time

from .data import Firm as Firm_Sheet, SeedRewardAssociation, Item as Item_Sheet
from .data import Plan_Seed, with_db, Backpack

from .error import *


class Item:
    """关于物品的操作 """

    @with_db
    def create_item(self, *, name, grade, shopping_price, db=None) -> int:
        item = Item_Sheet(
            name=name,
            grade=grade,
            shopping_price=shopping_price,
        )
        db.add(item)
        db.flush()
        return item.id

    @with_db
    def search_item(self,
                    *,
                    name=None | str,
                    grade=None | str,
                    shopping_price=None | str,
                    db=None) -> list[dict, dict]:
        """
        支持多段搜索(至少有一个)
        :param name: 名称
        :param grade: 等级
        :param shopping_price: 价格
        :param db: 默认
        :return: [{},{}] ,[] 表示错误
        """
        msg: list = []
        query = db.query(Item_Sheet)
        if name:
            query = query.filter(Item_Sheet.name.contains(name))
        if grade:
            query = query.filter(Item_Sheet.grade == grade)
        if shopping_price:
            query = query.filter(Item_Sheet.shopping_price == shopping_price)
        if not name and not grade and not shopping_price:
            return []
        result = query.all()
        for one in result:
            msg.append({
                "id": one.id,
                "name": one.name,
                "grade": one.grade,
                "shopping": one.shopping_price
            })
        return msg

    @with_db
    def delete_item(self, item_id, db=None) -> bool:
        """
        删除物品
        :param item_id: id
        :param db: 默认
        :return: bool
        """
        item = db.get(Item_Sheet, item_id)
        if item:
            db.delete(item)
            return True
        return False


class Firm:
    """土地组件，动作：创建，查询是否空地，种植"""

    # 土地创建
    @with_db
    def create_land(self, db=None) -> int:
        """
        创建新土地
        :param db: 默认接口
        :return: land.id
        """
        land = Firm_Sheet()
        db.add(land)

        return land.id

    @with_db
    def land(self, firm_id: int, db=None) -> dict | None:
        """
        查询土地
        :param firm_id: 土地id
        :param db: 默认接口
        :return: {id，等级，时间，种子，收获倍率}
        """
        land = db.get(Firm_Sheet, firm_id)
        if land is None:
            raise LandNotFoundError(f"土地{firm_id}不存在")
        msg = {"land.id": land.id,
               "land.level": land.level,
               "land.plan_time": land.plan_time,
               "land.plan_id": land.plan_id,
               "land.extra_amount": land.extra_amount}
        return msg

    def land_free(self, firm_id: int) -> bool:
        """
        查询土地是否为空
        :param firm_id: id
        :return: 空:Ture 非空:False
        """
        msg = self.land(firm_id)
        if msg is not None and msg.get("land.plan_id") is None:
            return True
        else:
            return False

    @with_db
    def plan_seed(self, *, firm_id: int, seed_id: int, db=None):
        """
        种植
        :param firm_id:id
        :param seed_id: id
        :param db: 默认
        :return:
        """
        seed = db.get(Plan_Seed, seed_id)
        land = db.get(Firm_Sheet, firm_id)
        land.plan_id = seed.id
        from founction import maturity_time
        land.plan_time = maturity_time(land_id=land.id, seed_id=seed.id)

    @with_db
    def clear_land(self, land_id: int, db=None) -> bool:
        """
        清空土地
        :param land_id: id
        :param db: 默认
        :return: Ture
        """
        land = db.get(Firm_Sheet, land_id)
        land.plan_id = None
        return True


class Seed:
    """关于种子的"""

    @with_db
    def create_plan_seed(self, *, item_id: int, mature_time: int, mature_amount: int,
                         db=None) -> int:
        """
        创建新种子

        :param item_id: id
        :param mature_time: 成熟时间
        :param mature_amount: 基础倍数
        :param db: 默认接口
        :return: plan_seed.id
        """
        plan_seed = Plan_Seed(
            item_id=item_id,
            mature_time=mature_time,
            mature_amount=mature_amount
        )

        db.add(plan_seed)
        db.flush()
        return plan_seed.id

    @with_db
    def seed(self, plan_id, db=None) -> dict | None:
        """
        查询种子
        :param plan_id: id
        :param db: 默认接口
        :return: {id，名称，等级，成熟时间，基础数量，备注}
        """
        plan = db.get(Plan_Seed, plan_id)
        if plan is None:
            return None

        msg = {"id": plan.id,
               "mature_time": plan.mature_time,
               "mature_amount": plan.mature_amount}
        return msg

    def seed_empty(self, plan_id) -> bool:
        """
        查询种子是否存在
        :param plan_id:id
        :return: 空False，非空Ture
        """
        return self.seed(plan_id) is not None


class Rewards:
    """关于收获物的"""

    @with_db
    def link_plan_rewards(self, *, plan_seed: int, item_id: int, db=None) -> bool:
        """
        关联种子和收获物
        :param plan_seed: plan_seed.id
        :param item_id: rewards.id
        :param db: 默认接口
        :return: Ture
        """
        association = SeedRewardAssociation(
            seed_id=plan_seed,
            item_id=item_id,
            rewards_amount=1,  # 需要指定掉落数量
            rewards_chance=1.0  # 需要指定掉落概率
        )
        db.add(association)

        return True

    @with_db
    def addtobackpack(self, seed_id, db=None) -> bool:
        """
        收获
        :param seed_id: id
        :param db: 默认
        :return: Ture
        """
        # 查询种子关联的所有收获物
        results = db.get(Plan_Seed, seed_id)

        for reward in results.rewards:
            # 1. 查找或创建Item记录
            item = db.query(Item_Sheet).filter(Item_Sheet.name == reward.item.name).first()
            if not item:
                # 如果Item不存在，报错
                return False

            # 2. 检查背包是否已有该物品
            backpack_item = db.query(Backpack).filter(
                Backpack.item_id == item.id
            ).first()

            if backpack_item:
                # 已有则增加数量
                backpack_item.amount += reward.rewards_amount
            else:
                # 没有则新增
                backpack_item = Backpack(
                    name=item.name,  # 冗余字段，方便查询
                    amount=reward.rewards_amount,
                    item_id=item.id
                )
                db.add(backpack_item)
        return True


class Action(Firm, Seed, Rewards, Item):
    """逻辑动作：
    种植，收获，添加收获物"""

    @with_db
    def plan_plan(self, *, plan_id: int, firm_id: int, db=None) -> tuple[bool, str]:
        """
        完整的种植动作
        :param db: 默认
        :param plan_id:seed_id
        :param firm_id: land_id
        :return:
        """
        if not self.land_free(firm_id):
            return False, "土地不存在|土地已种植"
        if not self.seed_empty(plan_id):
            return False, "种子不存在"
        self.plan_seed(firm_id=firm_id, seed_id=plan_id, db=db)
        return True, f"{firm_id}种植{plan_id}成功"

    def reward(self, land_id: int, *, db) -> tuple[bool, str]:
        """
        完整的收获动作
        :param db: 默认
        :param land_id:id
        :return:[bool,详细信息]
        """

        if self.land_free(land_id) is True:
            return False, "土地空闲"
        if self.land(land_id).get("land.plan_time") is None:
            return False, "时间错误"
        if self.land(land_id).get("land.plan_time") < time.time():
            self.clear_land(land_id, db=db)
            return True, f"{land_id}已收获"
        return False, "未知错误"

    @with_db
    def get_rewards(self, land_id: int, db=None):
        """
        收获物品并添加到背包
        :param land_id:
        :param db:
        :return:
        """
        seed_id = self.land(land_id).get("land.plan_id")
        status = self.reward(land_id, db=db)
        if status[0]:
            self.addtobackpack(seed_id, db=db)
            return True, f"收获{land_id}成功"
        else:
            return False, status[1]


if __name__ == "__main__":
    pass
