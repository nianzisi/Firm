"""土地种植规则"""
import time

from data import Firm as Firm_Sheet, SeedRewardAssociation
from data import Plan_Seed_Rewards, Plan_Seed, with_db


class Firm():
    """土地实例化"""

    @with_db
    def create_land(self, db=None):
        land = Firm_Sheet()
        db.add(land)
        return True, "land创建成功", land.id

    @with_db
    def create_plan_seed(self, *, plan_name: str, plan_grade: int, mature_time: int, mature_amount: int,
                         comment: str | None = None, db=None):
        plan_seed = Plan_Seed(
            plan_name=plan_name,
            plan_grade=plan_grade,
            mature_time=mature_time,
            mature_amount=mature_amount,
            comment=comment
        )

        db.add(plan_seed)
        db.flush()
        return True, "seed创建成功", plan_seed.id

    @with_db
    def create_plan_rewards(self, *, rewards_name: str, rewards_grade: int, db=None):
        reward = Plan_Seed_Rewards(
            rewards_name=rewards_name,
            rewards_grade=rewards_grade,
        )
        db.add(reward)
        db.flush()
        return True, "rewards创建成功", reward.id

    @with_db
    def link_plan_rewards(self, *, plan_seed, rewards, db=None):
        association = SeedRewardAssociation(
            seed_id=plan_seed,
            reward_id=rewards,
            rewards_amount=1,  # 需要指定掉落数量
            rewards_chance=1.0  # 需要指定掉落概率
        )
        db.add(association)

        return True, "成功"

    @with_db
    def plan_plan_seed(self, *, plan_id, firm_id, db=None):
        seed = db.get(Plan_Seed, plan_id)
        land = db.get(Firm_Sheet, firm_id)
        if not seed:
            return False, "没有该种子"
        if not land:
            return False, "没有该土地"
        if land.plan_id is not None:
            return False, "该土地非空闲"

        land.plan_time = int(seed.mature_time / (1 + land.level * 0.1)) + int(time.time())
        land.plan_id = seed.id
        return True, f"{land.id}种植{seed.plan_name}成功"

    @with_db
    def get_reward(self, *, firm_id, db=None):
        reward = db.get(Firm_Sheet, firm_id)
        if reward.plan_id is None:
            return False, "该土地没有种植"
        if reward.plan_time <= int(time.time()):
            return True, "成熟", reward.id
        else:
            return False, "未成熟"

    @with_db
    def rewards(self, *, firm_id, db=None):
        if self.get_reward(firm_id)[0]:
            # 1. 获取土地
            land = db.get(Firm_Sheet, firm_id)

            # 2. 获取种子
            seed = land.plan_owner  # Plan_Seed 对象

            # 3. 获取种子的所有奖励配置（从关联表）
            associations = db.query(SeedRewardAssociation).filter(
                SeedRewardAssociation.seed_id == seed.id
            ).all()

            # 4. 遍历并收获
            import random
            obtained = []

            for assoc in associations:
                # 获取奖励详情
                reward = db.get(Plan_Seed_Rewards, assoc.reward_id)

                # 根据概率判断是否获得
                if random.random() <= assoc.rewards_chance:
                    # 应用土地的额外收获倍率
                    actual_amount = assoc.rewards_amount * (1 + land.extra_amount)

                    obtained.append({
                        'name': reward.rewards_name,
                        'grade': reward.rewards_grade,
                        'amount': actual_amount,
                        'base_amount': assoc.rewards_amount,
                        'chance': assoc.rewards_chance
                    })

                    print(f"收获 {reward.rewards_name} x{seed.mature_amount} (概率:{assoc.rewards_chance * 100}%)")
                else:
                    print(f"未获得 {reward.rewards_name} (概率:{assoc.rewards_chance * 100}%)")

            # 清空土地
            land.plan_id = None
            land.plan_time = -1

            return obtained
        else:
            print("未成熟或没有种植")
            return []


if __name__ == "__main__":
    firm = Firm()
    # 创建land
    # firm.create_land()
    # 创建种子及其关联
    # A = firm.create_plan_seed(plan_name="灵草种子", plan_grade=0,
    #                       mature_time=10, mature_amount=3,
    #                       comment="随处可见灵草的种子")
    # B = firm.create_plan_rewards(rewards_name="灵草", rewards_grade=0)
    #
    # print(type(A))
    # print(type(A[2]))
    # print(type(B[2]))
    #
    # firm.link_plan_rewards(A[2], B[2])
    print(firm.plan_plan_seed(plan_id=4, firm_id=1))
    print(firm.get_reward(firm_id=1))
    firm.rewards(firm_id=1)
