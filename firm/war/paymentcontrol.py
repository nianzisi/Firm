import ast
import re

from war.win_reward import Win_end
from war.attalk import Battle
from war.Attribute import Enemy

from commomd.mind import with_db


class Control:
    """
    控制战斗和结算逻辑
    """

    orm_dict = {"怪物": Enemy, "enemy": Enemy}

    #  后续可以新建 boos 表，也可以放入orm_dict

    @staticmethod
    def init_battle(action, target) -> list:
        """
        战斗
        :param action: 玩家
        :param target: 敌方
        :return: 战斗日志
        """
        return Battle([action, target]).battle_run()

    @staticmethod
    def data_handle(logger: list) -> list[dict]:
        """
        字典转化
        :param logger: 战斗日志
        :return: 转换好的日志
        """
        match = []
        regular = r"{(.*)$"
        for _logger in logger:
            msg = re.search(regular, _logger).group(0)
            match.append(ast.literal_eval(msg))
            # match.append(re.search(regular, _logger).group(0))
        return match

    @staticmethod
    def out_handle(logger: list[dict]) -> list[dict]:
        """
        数据处理
        :param logger: 日志字典
        :return: 处理好的数据
        """
        out_msg = []
        for _msg in logger:
            if float(_msg.get("受伤者剩余血量")) == 0:
                out_msg.append(
                    {
                        "攻击者tab_name": _msg["攻击者tab_name"],
                        "攻击者id": _msg["攻击者id"],
                        "受伤者tab_name": _msg["受伤者tab_name"],
                        "受伤者id": _msg["受伤者id"],
                    }
                )
        return out_msg

    @staticmethod
    @with_db
    def add_item(logger: list[dict], db=None):
        """
        添加物品
        :param db: 默认
        :param logger: 数据
        :return: 无
        """
        for _msg in logger:
            # target_tab_name = Control.orm_dict[_msg["受伤者tab_name"]]
            Win_end.win_lost(target_id=_msg["受伤者id"], db=db)

    @staticmethod
    @with_db
    def control(action, target, db=None):
        """
        整体的对战+掉落物到背包的流程
        :param db: 默认
        :param action: 玩家
        :param target: 地方
        :return: 无
        """
        raw_logs = Control.init_battle(action, target)
        parsed = Control.data_handle(raw_logs)
        records = Control.out_handle(parsed)
        Control.add_item(records, db=db)
