"""关于植物的各类计算"""
import time

from seed.data_space import Data


def maturity_time(*, land_id: int, seed_id: int) -> int:
    """计算种植时间，后续可能添加其他效果
    :param land_id:id
    :param seed_id:id
    :return :int"""
    with Data(land_id=land_id, seed_id=seed_id) as cxl:
        plan_time = int(cxl.seed_mature_time / (1 + cxl.land_level * 0.1)) + int(time.time())
    return plan_time

