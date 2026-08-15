"""增删查改的万用接口，在尝试使用更推荐的风格，取消使用类当命名空间，使用脚本当命名空间"""

from commomd.mind import with_db
from sqlalchemy import Integer, String


def data_common_id_assess(the_id) -> dict:
    """
    只检测了id是否为int，听ai说id能为0和负数，所以没有去做数值检测
    :param the_id: id
    :return: dict
    """
    _bool = type(the_id) is int
    if _bool:
        return {"success": True}
    else:
        return {"success": False,
                "because": f"{the_id}不是int类型"}


def data_common_table_assess(model_class) -> dict:
    """
    检测表类是否是sqlalchemy模块创建的
    :param model_class: 表类
    :return: dict
    """
    if hasattr(model_class, "__table__"):
        return {"success": True}
    else:
        return {"success": False,
                "because": f"{model_class.__name__}不是sqlalchemy模块建立的类"}


@with_db
def data_change_base(model_class, dir_name, the_id, change_value, db=None) -> dict:
    """
    改
    :param model_class: 表类
    :param dir_name: 待改属性名
    :param the_id: id
    :param change_value: 值
    :param db: 默认
    :return: dict
    """
    col = db.get(model_class, the_id)
    if col:
        setattr(col, dir_name, change_value)
        return {"success": True,
                "msg": f"已修改{model_class.__name__}的{dir_name}的值为{change_value}"}
    else:
        return {"success": False,
                "msg": f"{model_class.__name__}的主键，没有值为{the_id}的"}


def data_change_handle(model_class, dir_name, change_value) -> dict:
    """
    仿写的
    :param model_class: 表类
    :param dir_name: 待改属性名
    :param change_value: 值
    :return: dict
    """
    table_columns = {col.name: col for col in model_class.__table__.columns}
    for _name, _obj in table_columns.items():
        if _name == dir_name:
            if not _obj.nullable:
                if change_value is None:
                    return {"success": False,
                            "because": f"{model_class.__name__}的{dir_name}属性不能为None"}

            if isinstance(_obj.type, String):
                if not isinstance(change_value, str):
                    return {"success": False,
                            "because": f"{model_class.__name__}的{dir_name}属性为str, 待更改值为{type(change_value)}"}
                if change_value.strip() == "":
                    return {"success": False,
                            "because": f"{model_class.__name__}的{dir_name}属性为str, 待更改值不能为''"}
            if isinstance(_obj.type, Integer):
                if not isinstance(change_value, int):
                    return {"success": False,
                            "because": f"{model_class.__name__}的{dir_name}属性为int, 待更改值为{type(change_value)}"}
            if _obj.primary_key:
                if not isinstance(change_value, int):
                    return {"success": False,
                            "because": f"{model_class.__name__}的{dir_name}属性为主键, 待更改值为{type(change_value)}"}
    return {"success": True}


def data_change(*, model_class, dir_name, the_id, change_value, db=None) -> dict:
    """
    改
    :param model_class: 表类
    :param dir_name: 待改属性名
    :param the_id: id
    :param change_value: 值
    :param db: 默认
    :return: dict
    """
    result = data_common_table_assess(model_class)
    if result.get("success", False):
        result2 = data_change_handle(model_class, dir_name, change_value)
        if result2.get("success", False):
            return data_change_base(model_class, dir_name, the_id, change_value, db=db)
        return result2
    return result


@with_db
def data_del_base(model_class, the_id, db=None) -> dict:
    """
    删
    :param model_class: 表类
    :param the_id: id
    :param db: 默认
    :return: dict
    """
    col = db.get(model_class, the_id)
    if col:
        db.delete(col)

        return {"success": True,
                "del": f"已删除{model_class.__name__}中id为{the_id}的数据"}
    else:
        return {"success": False,
                "msg": f"{model_class.__name__}的主键，没有值为{the_id}的"}


def data_del(*, model_class, the_id: int, db=None) -> dict:
    """
    删
    :param model_class: 表类
    :param the_id: id
    :param db: 默认
    :return: dict
    """
    result = data_common_id_assess(the_id)
    if result.get("success"):
        return data_del_base(model_class, the_id, db=db)
    else:
        return result


@with_db
def data_add_base(data_obj, db=None) -> dict:
    """
    只接受符合要求的实例
    :param data_obj:要创建的实例 
    :param db: 默认
    :return: dict
    """""
    db.add(data_obj)
    return {"success": True,
            "self_dir": data_obj.__dict__
            }


def data_add_handle(data_obj, model_class) -> list:
    """
    ai写的边界条件，一字不改的复制了过来
    :param data_obj: 实例
    :param model_class: 表类
    :return: dict
    """
    errors = []

    # 1. 获取表结构（期望的字段）
    table_columns = {col.name: col for col in model_class.__table__.columns}

    # 2. 获取实际数据
    actual_data = {}
    for key, value in data_obj.__dict__.items():
        if not key.startswith('_'):
            actual_data[key] = value

    # 3. 检查必填字段
    for col_name, col in table_columns.items():
        if not col.nullable and not col.primary_key:
            if col_name not in actual_data or actual_data[col_name] is None:
                errors.append(f"必填字段 '{col_name}' 缺失")

    # 4. 检查字段类型和长度
    for col_name, col in table_columns.items():
        if col_name in actual_data and actual_data[col_name] is not None:
            value = actual_data[col_name]

            # 检查类型
            if isinstance(col.type, String) and not isinstance(value, str):
                errors.append(f"字段 '{col_name}' 应该是字符串类型")

            if isinstance(col.type, Integer) and not isinstance(value, int):
                errors.append(f"字段 '{col_name}' 应该是整数类型")

            # 检查长度
            if hasattr(col.type, 'length') and isinstance(value, str):
                if len(value) > col.type.length:
                    errors.append(f"字段 '{col_name}' 长度不能超过 {col.type.length}")

    # 5. 检查多余字段（可选）
    for field_name in actual_data:
        if field_name not in table_columns:
            errors.append(f"未知字段 '{field_name}'")

    return errors


def data_add(*, data_obj, model_class, db=None) -> dict:
    """
    增
    :param data_obj: 实例类
    :param model_class: 表类
    :param db: 默认
    :return: dict
    """
    msg = data_common_table_assess(model_class)
    if msg.get("success", False):
        error = data_add_handle(data_obj, model_class)
        if not error:
            return data_add_base(data_obj, db=db)
        else:
            return {"success": False,
                    "because": error}
    else:
        return msg


@with_db
def data_search(*, model_class, the_id=None, db=None, **kwargs, ) -> dict:
    """
    好像没有什么边界要求，全靠自觉
    :param model_class: 表类
    :param the_id: id
    :param db: 默认
    :param kwargs: 要查询的键名和值
    :return: dict
    """
    if the_id:
        result = data_common_id_assess(the_id)
        if result["success"]:
            _i = db.get(model_class, the_id)
            if _i:
                return {"success": True,
                        "msg": _i}
            return {"success": False,
                    "msg": f"{model_class.__name__}的主键，没有值为{the_id}的"}
    query = db.query(model_class)
    for _dir, _value in kwargs.items():
        query = query.filter(getattr(model_class, _dir) == _value)
    result = query.all()
    return {"success": True,
            "msg": result}
