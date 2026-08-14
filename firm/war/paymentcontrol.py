import ast
import re

from win_reward import Win_end
from attalk import Battle
from Attribute import Enemy


class Control:
    """
    控制战斗和结算逻辑
    """
    orm_dict = {"怪物": Enemy,
                "enemy": Enemy}
    #  后续可以新建 boos 表，也可以放入orm_dict

    @staticmethod
    def init_battle(action, target) -> list:
        return Battle([action, target]).battle_run()

    @staticmethod
    def data_handle(logger: list) -> list[dict]:
        match = []
        regular = r"{(.*)$"
        for _logger in logger:
            msg = re.search(regular, _logger).group(0)
            match.append(ast.literal_eval(msg))
            # match.append(re.search(regular, _logger).group(0))
        return match

    @staticmethod
    def out_handle(logger: list[dict]) -> list[dict]:
        out_msg = []
        for _msg in logger:
            if float(_msg.get("受伤者剩余血量")) == 0:
                out_msg.append({"攻击者tab_name": _msg["攻击者tab_name"],
                                "攻击者id": _msg["攻击者id"],
                                "受伤者tab_name": _msg["受伤者tab_name"],
                                "受伤者id": _msg["受伤者id"]})
        return out_msg

    @staticmethod
    def add_item(logger: list[dict]):
        for _msg in logger:
            # target_tab_name = Control.orm_dict[_msg["受伤者tab_name"]]
            Win_end.win_lost(target_id=_msg["受伤者id"])

    @staticmethod
    def control(action, target):
        raw_logs = Control.init_battle(action, target)
        parsed = Control.data_handle(raw_logs)
        records = Control.out_handle(parsed)
        Control.add_item(records)
