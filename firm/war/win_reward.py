"""战斗结算"""
from template import creat_enemy, creat_player
from attalk import Battle
from EventBus import event_emit

from commomd.mind import with_db
from Attribute import Enemy_item
from seed.firm import Back_bag


class Win_end:

    def __init__(self, player_id: int, enemy_id: int):
        self.player_id = player_id
        self.enemy_id = enemy_id

    @with_db
    def win_lost(self, db=None):
        item = db.query(Enemy_item).filter(Enemy_item.enemy_id == self.enemy_id).all()
        if item:
            for _item_id in item:
                if _item_id:
                    Back_bag().add_bag_item(item_id=_item_id.id, amount=_item_id.count)
        else:
            print("未知错误")

