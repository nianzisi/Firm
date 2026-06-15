# 可以定义一系列异常，形成体系
class GameError(Exception):
    """游戏基础异常"""
    pass


class LandError(GameError):
    """土地相关异常"""
    pass


class LandNotFoundError(LandError):
    """土地不存在"""
    pass


class LandOccupiedError(LandError):
    """土地被占用"""
    pass


class LandNotMatureError(LandError):
    """土地未成熟"""
    pass


class SeedError(GameError):
    """种子相关异常"""
    pass


class SeedNotFoundError(SeedError):
    """种子不存在"""
    pass
