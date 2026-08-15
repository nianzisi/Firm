from seed.data import Backpack, Firm, Plan_Seed, SeedRewardAssociation, Item, User
from war.Attribute import Enemy_item, Enemy, Player
from commomd.mind import Base, engine

print(Enemy)  # 如果报错 NameError，说明类没定义成功
print(Enemy_item)
print(Player)

print("建表前，Base 注册的表:", Base.metadata.tables.keys())

print("war/datacreat.py 中的 Base 地址:", id(Base))

Base.metadata.create_all(engine)
