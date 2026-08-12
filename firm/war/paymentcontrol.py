import ast
import re


# from win_reward import Win_end
# from attalk import Battle


class Control:
    """
    控制战斗和结算逻辑
    """

    @staticmethod
    def control(action, target) -> list:
        return Battle([action, target]).battle_run()

    @staticmethod
    def data_handle(logger: list):
        match = []
        regular = r"{(.*)$"
        for _logger in logger:
            msg = re.search(regular, _logger).group(0)
            match.append(ast.literal_eval(msg))
            # match.append(re.search(regular, _logger).group(0))
        return match
