# win_reward.py
from war.Attribute import Enemy_item
from commomd.mind import with_db
from seed.firm import Back_bag


class Win_end:
    """
    查找对象对应的掉落物，添加到物品到背包
    """

    @staticmethod
    @with_db
    def search_data(*, target_id, db=None):
        """
        搜索id对应的凋落物
        :param target_id: enemy_id
        :param db: 默认
        :return: 数据库对象列表
        """
        return db.query(Enemy_item).filter(Enemy_item.enemy_id == target_id).all()

    @staticmethod
    @with_db
    def win_lost(*, target_id, db=None):
        """
        添加对应的掉落物到背包
        :param target_id: enemy_id
        :param db: 默认
        :return: 无
        """
        drops = Win_end.search_data(target_id=target_id, db=db)
        if not drops:
            print(f"怪物 {target_id} 无掉落")
            return
        back = Back_bag()
        for drop in drops:
            back.add_bag_item(item_id=drop.item_id, amount=drop.count)
