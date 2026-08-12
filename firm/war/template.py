from attalk import Enemy
from attalk import Player
from attalk import Attack, Defense, Action_top


def creat_player(**kwargs):
    _player = Player(tab_name=kwargs.get("tab_name"),
                     ID=kwargs.get("ID"),
                     name=kwargs.get("name"),
                     HP=kwargs.get("HP"),
                     ATK=kwargs.get("ATK"),
                     DEF=kwargs.get("DEF"),
                     AGI=kwargs.get("AGI"),
                     Attack=Attack,
                     Defense=Defense,
                     Action_top=Action_top)
    return _player


def creat_enemy(**kwargs):
    _enemy = Enemy(tab_name=kwargs.get("tab_name"),
                   ID=kwargs.get("ID"),
                   name=kwargs.get("name"),
                   HP=kwargs.get("HP"),
                   ATK=kwargs.get("ATK"),
                   DEF=kwargs.get("DEF"),
                   AGI=kwargs.get("AGI"),
                   Attack=Attack,
                   Defense=Defense,
                   Action_top=Action_top)
    return _enemy


if __name__ == "__main__":
    from attalk import Battle

    player = creat_player(tab_name="玩家", ID=1, name="玩家", HP=100, ATK=15, DEF=5, AGI=1.2)
    enemy = creat_enemy(tab_name="精英怪物", ID=23, name="怪物", HP=80, ATK=10, DEF=3, AGI=0.8)
    enemy2 = creat_enemy(tab_name="普通怪物", ID=24, name="怪物", HP=130, ATK=1, DEF=3, AGI=0.8)

    print(isinstance(player, Player))  # False,__main__.Player 和 attalk.Player是不同的

    for i in Battle().battle_run([player, enemy, enemy2]):
        print(i)
    print(player.HP, enemy.HP, enemy2.HP)
