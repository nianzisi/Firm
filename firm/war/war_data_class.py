from commomd.data_class import data_add, data_del, data_change, data_search

from war.Attribute import Player, Enemy, Enemy_item

from war.attalk import Battle

from war.template import creat_enemy, creat_player

from commomd.attribute_change import player_att_change


class data_base:
    def __init__(self, model):
        self.model = model

    def data_add(self, data_obj):
        return data_add(data_obj=data_obj, model_class=self.model)

    def data_del(self, the_id):
        return data_del(model_class=self.model, the_id=the_id)

    def data_change(self, dir_name, the_id, value):
        return data_change(
            model_class=self.model, dir_name=dir_name, the_id=the_id, change_value=value
        )

    def data_search(self, the_id=None, **kwargs):
        return data_search(model_class=self.model, the_id=the_id, **kwargs)


class Player_class(data_base):
    """这个才是战斗对象创建吧"""

    def __init__(self, the_id):
        super().__init__(Player)
        self.the_id = the_id
        self.attribute = None
        self.action = None

    def get_base_attribute(self):
        result = self.data_search(self.the_id).get("msg", None)
        if result:
            self.attribute = result
        return self

    def att_change(self):
        result = player_att_change(self.attribute)
        if result:
            result = result | {
                "name": self.attribute.name,
                "ID": self.attribute.id,
                "tab_name": "player",
            }
            self.action = creat_enemy(**result)
        return self

    def __call__(self, *args, **kwargs):
        self.get_base_attribute()
        self.att_change()
        return self.action


class Enemy_class(data_base):
    def __init__(self, the_id):
        super().__init__(Enemy)
        self.the_id = the_id
        self.attribute = None
        self.action = None

    def get_base_attribute(self):
        result = self.data_search(self.the_id).get("msg", None)
        if result:
            self.attribute = result
        return self

    def att_change(self):
        result = player_att_change(self.attribute)
        if result:
            result = result | {
                "name": self.attribute.name,
                "ID": self.attribute.id,
                "tab_name": "enemy",
            }
            self.action = creat_player(**result)
        return self

    def __call__(self, *args, **kwargs):
        self.get_base_attribute()
        self.att_change()
        return self.action
