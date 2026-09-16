import copy
from typing import overload

clean_rule = {
    "user": ["role", "content", "name"],
    "system": ["role", "content", "name"],
    "assistant": ["role", "content", "name", "reasoning_content", "tool_calls", "prefix"],
    "tool": ["role", "content", "name", "tool_call_id"]
}


@overload
def clean(data: list[dict]) -> list[dict]: ...


@overload
def clean(data: dict) -> dict: ...


def clean(data):
    """
    清理只会清理多余字段，如果某字典缺少关键字段，不会删除该字典
    :param data:
    :return:
    """
    _data = copy.deepcopy(data)  # 防止原数据被修改

    def sub_rule(_one_data):
        if _one_data.get("role") in clean_rule.keys():
            more = _one_data.keys() - clean_rule.get(_one_data.get("role"))
            [_one_data.pop(_) for _ in more or ()]
        else:
            raise ValueError("缺少字段role 或是 不合法的角色")

    if isinstance(_data, list):
        for one_data in _data:
            if isinstance(one_data, dict):
                sub_rule(one_data)
            else:
                raise ValueError("不支持的类型，期待list[dict]/dict")
        return _data
    elif isinstance(_data, dict):
        sub_rule(_data)
        return _data
    else:
        raise ValueError("不支持的类型，期待list[dict]/dict")


if __name__ == "__main__":
    test_data = {"role": "assistant", "content": 1, "asd": 123, "name": "ggg", "reasoning_content": 1}
    print(clean(test_data))
