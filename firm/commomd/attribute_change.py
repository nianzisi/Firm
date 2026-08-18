"""属性转换规则"""


def player_att_change(user) -> dict:
    """
    属性转换
    :param user: 实例对象
    :return: 字典
    """
    attrs = {}
    ATK = 0
    DEF = 0
    HP = 0
    AGI = 0
    if hasattr(user, "GenGu"):
        guts = getattr(user, "GenGu")
        DEF += guts * 1.2
        HP += guts * 2

    if hasattr(user, "BiLi"):
        power = getattr(user, "BiLi")
        ATK += power * 1.5
        AGI += power * 0.1

    if hasattr(user, "MingJie"):
        seep = getattr(user, "MingJie")
        AGI += seep * 0.8

    if ATK and DEF and HP and AGI:
        attrs["ATK"] = ATK
        attrs["DEF"] = DEF
        attrs["HP"] = HP
        attrs["AGI"] = AGI
        return attrs

    else:
        return {}
