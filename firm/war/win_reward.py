# win_reward.py
from war.Attribute import Enemy_item
from commomd.mind import with_db
from seed.firm import Back_bag


class Win_end:
    @staticmethod
    @with_db
    def search_data(*, target_id, db=None):
        return db.query(Enemy_item).filter(Enemy_item.enemy_id == target_id).all()

    @staticmethod
    def win_lost(*, target_id, **kwargs):
        drops = Win_end.search_data(target_id=target_id)
        if not drops:
            print(f"怪物 {target_id} 无掉落")
            return
        back = Back_bag()
        for drop in drops:
            back.add_bag_item(item_id=drop.item_id, amount=drop.count)
