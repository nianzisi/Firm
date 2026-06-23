"""数据的上下文窗口"""

from .firm import Firm, Seed


class Data(Firm, Seed):
    def __init__(self, *, seed_id: int, land_id: int):
        self.seed_id = seed_id
        self.land_id = land_id
        self.seed_msg: dict | None = None
        self.land_msg: dict | None = None

    def __enter__(self):
        if self.seed_msg is None:
            self.seed_msg = self.seed(self.seed_id)
        if self.land_msg is None:
            self.land_msg = self.land(self.land_id)
        return self

    @property
    def land_level(self) -> int:
        return self.land_msg.get("land.level")

    @property
    def seed_mature_time(self) -> int:
        return self.seed_msg.get("mature_time")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.seed_msg = None
        self.land_msg = None

        return False
