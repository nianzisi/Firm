"""战斗逻辑,尝试使用类装饰器. pass为待做或者待扩展标识"""

from error import Player_Creat_Error


def dataclass(cls):
    """自动赋值，自动启动__post__init__,类装饰的尝试"""
    # 1. 收集类中定义的类型注解字段
    fields = {}
    defaults = {}
    for base in cls.__mro__:
        if hasattr(base, "__annotations__"):
            for name, typ in base.__annotations__.items():
                if hasattr(base, name):
                    defaults[name] = getattr(base, name)
                else:
                    defaults[name] = None
                fields[name] = typ

    def __init__(self, **kwargs):
        for _name in fields:
            if _name in kwargs:
                value = kwargs[_name]
                kwargs.pop(_name, value)
            else:
                value = defaults[_name]
            setattr(self, _name, value)
        self._kwargs = kwargs

        if hasattr(self, "__post__init__"):
            self.__post__init__()

    cls.__init__ = __init__

    return cls


@dataclass
class Data_base:
    name: str
    ATK: int
    HP: int
    DEF: int
    AGI: float

    #  疑惑：把数据库中的数据转换成类，是否多此一举？

    def __post__init__(self):
        for name, number in self.__dict__.items():
            if number is None:
                raise Player_Creat_Error(f"{name}数值异常")

    def get___kwargs(self) -> dict | None:
        if hasattr(self, "_kwargs"):
            __kwargs = self._kwargs
            del self._kwargs
            return __kwargs
        else:
            return None

    def __call__(self, *args, **kwargs):
        pass


class Action:

    def __init__(self, owner):
        self.owner = owner

    pass


class Attack(Action):
    """攻击"""

    def __init__(self, owner):
        super().__init__(owner)
        self.times: float = 1.0

    def attack(self) -> float:
        """攻击力计算"""
        damage = self.owner.ATK * self.times
        self.times *= 1.1
        return damage
        pass


class Defense(Action):
    def __init__(self, owner):
        super().__init__(owner)
        self.times: float = 1.0

    def defense(self) -> float:
        """防御力计算"""
        Def = self.owner.DEF * self.times
        self.times *= 0.9
        return Def
        pass


class Action_top(Action):
    """简易的通用动作，后续可添加其他属性。
    等待action扩展到一定数量在移入到Action父类"""

    def __init__(self, owner):
        super().__init__(owner)
        self._AGI = 0.0
        self._AGI_All = 1.0

    def move(self, speed) -> bool:
        self._AGI += speed
        if self._AGI >= self._AGI_All:
            self._AGI -= self._AGI_All
            return True
        else:
            return False

    def hit(self, damage: int):
        """受击"""
        self.owner.HP -= damage
        return self.owner.HP

    def death(self, target: Data_base) -> bool:
        if not target.HP > 0:
            print(f"{target.name}死亡")
            return False
        else:
            return True

        #  单体死亡，


@dataclass
class Player(Data_base):
    slots = ["Attack", "Defense", "Action_top"]

    # 普通的slots, 允许注册的类, 手动过滤 ,如果性能差，后续考虑用rust，重写Enemy类

    def __post__init__(self):
        super().__post__init__()
        self.dict = self.get___kwargs()
        for _name, _value in self.dict.items():
            if _name in self.slots:
                setattr(self, _name, _value(owner=self))
            else:
                print(f"无效的传入{_name}")  # 后续打印在日志中


@dataclass
class Enemy(Data_base):
    # __slots__ = ["Attack", "Defense", "Action_top"]
    # 会阻止__dict__创建(有内存优化，但会限制属性，不太使用于拓展)
    slots = ["Attack", "Defense", "Action_top"]

    # 普通的slots, 允许注册的类, 手动过滤 ,如果性能差，后续考虑用rust，重写Enemy类

    def __post__init__(self):
        super().__post__init__()
        self.dict = self.get___kwargs()
        for _name, _value in self.dict.items():
            if _name in self.slots:
                setattr(self, _name, _value(owner=self))
            else:
                print(f"无效的传入{_name}")  # 后续打印在日志中


class Battle_base:
    pass  # 待做


class Battle(Battle_base):

    def __init__(self):
        self._player_action = []
        self._enemy_action = []

    def join_action(self, action: list[Data_base]):
        for _action in action:
            if isinstance(_action, Enemy):
                self._enemy_action.append(_action)
            elif isinstance(_action, Player):
                self._player_action.append(_action)
            else:
                print("")  # 日志

    def join_player_action(self, action: Data_base):
        pass

    def join_enemy_action(self, action: Data_base):
        pass

    def get_speed(self):
        _action = self._player_action + self._enemy_action
        speed_all = 0
        for action in _action:
            speed_all += action.AGI
        return speed_all

    def battle_move(self):
        _action = self._player_action + self._enemy_action
        speed_all = self.get_speed()
        move_action = []

        for _ in range(10):
            """防止无限递归，每次最多前进10步"""
            for action in _action:
                speed = action.AGI / speed_all
                if action.Action_top.move(speed):
                    move_action.append(action)
            if move_action:
                move_action.sort(key=lambda f: f.AGI, reverse=True)
                return move_action

        return []

    def death(self):
        self._player_action = [p for p in self._player_action if p.HP > 0]
        self._enemy_action = [e for e in self._enemy_action if e.HP > 0]
        return bool(self._player_action and self._enemy_action)


    def pick(self, action: Data_base):
        player = self._player_action
        enemy = self._enemy_action
        if action in self._player_action:
            enemy.sort(key=lambda f: f.HP)
            if enemy:
                return enemy[0]
        elif action in self._enemy_action:
            player.sort(key=lambda f: f.HP)
            if player:
                return player[0]

        return False

    def fight(self, action: Data_base, target: Data_base):
        if action and target:
            damage = action.Attack.attack()
            defense = target.Defense.defense()
            target.Action_top.hit(max(0, damage - defense))

    def battle_run(self, action: list[Data_base]):
        """战斗逻辑"""
        self.join_action(action)
        while self.death():
            mover = self.battle_move()
            for _mover in mover:
                self.fight(_mover, self.pick(_mover))
        pass
        #  结算逻辑
