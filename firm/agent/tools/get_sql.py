import inspect
import re


class Tool_data:
    _instance = None
    """
    储存tool的单类，允许分类
    实现:自动转换，tool工具的字段信息
    实现:存储tool工具列表
    待实现:执行LLM调用函数
    """

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._listeners = {}  # 初始化储存字典
        return cls._instance

    def sign_up(self, category: str, func: object) -> None:
        """
        {"category": {"name": "func",
              "name2": "func",
              },
        "category2":{"name": "func",
              "name2": "func",
              }
        }
        :param category:类名
        :param func:函数
        :return:None
        """
        func_name = func.__name__

        if category not in self._listeners:
            self._listeners[category] = {}
        if func_name not in self._listeners[category]:
            self._listeners[category][func_name] = func
        else:
            times = 1
            while times <= 10:
                if f"{func_name}_{times}" not in self._listeners[category]:
                    self._listeners[category][f"{func_name}_{times}"] = func
                    break
                else:
                    times += 1
            if times > 10:
                raise ValueError(f"过多的同名文件{func_name}")

    def out_tool_json(self, category: str = None)  -> list:
        """
        输出tool的json格式
        :param category:要输出的类名
        :return: tools的value：list
        """
        out_json = []
        if category is None:
            _next = bool(self._listeners.keys())
            if _next:
                category = list(self._listeners.keys())[0]
            else:
                return []
        elif category not in list(self._listeners.keys()):
            raise ValueError(f"不存在{category} 工具箱")
        for name, func in self._listeners[category].items():
            out_json.append(
                func_org(func=func, name=f"{category}__{name}")
            )
        return out_json

    def emit_on(self, ):
        pass
        # Todo


def tool(category: str = "tool"):
    """
    tool工具注册装饰器
    :param category: 类名
    :return: 原函数
    """

    def muld(func):
        Tool_data().sign_up(category=category, func=func)

        return func

    return muld

# python类型转换jsonn类型的映射字典
json_translation = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    None: "null",
    list: "array",
    tuple: "array",
    dict: "object"
}


# def type_translation(input_):
#     _input = str(input_)


def func_org(func: object, name: str) -> dict:
    """
    主要组合tool的json信息
    :param func: 函数（不能缺少，参数类型，注释）
    :param name: 函数的名称
    :return: dict
    """
    msg = func.__doc__
    if msg is None:
        raise ValueError(f"{func}缺少注释")

    func_description_bool = re.search(r"(.+?)\n:param", msg)
    parameters_list = re.findall(r":param(.+?):", msg)
    func_return_bool = re.search(r":return:(.+)", msg)
    if not func_description_bool or not parameters_list or not func_return_bool:
        raise ValueError(f"{name}描述/参数描述/返回值描述不全或者格式不正确")
    else:
        func_return = func_return_bool.group(1)
        func_description = func_description_bool.group(1)

    properties = {}
    for parameter in parameters_list:
        parameter_strip = parameter.strip()
        description = re.search(rf":param {re.escape(parameter_strip)}:(.+)", msg).group(1).strip()
        # print(str)
        todo_json_translation = func.__annotations__.get(parameter_strip, "！@/空标志符/占位符￥%")
        if todo_json_translation == "！@/空标志符/占位符￥%":
            raise ValueError(f"{func}参数类型注释有空缺")
        properties[parameter_strip] = {
            "type": json_translation[todo_json_translation],
            "description": description}

    if "args" in properties.keys():
        properties["args"]["type"] = 'array'
    if "kwargs" in properties.keys():
        properties["kwargs"]["type"] = "object"

    func_inspect = inspect.signature(func).parameters.items()
    result = []

    for _key, _value in func_inspect:
        if (str(_value.kind) == "POSITIONAL_ONLY" or str(
                _value.kind) == "POSITIONAL_OR_KEYWORD") and _value.default is inspect.Parameter.empty:
            result.append(_key)

    return {
        "type": "function",
        "function": {
            "name": name or func.__name__,
            "description": f"{func_description} \n 返回:{func_return}",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": result,
            },
        },
    }


if __name__ == "__main__":
    @tool()
    def test_tool(Aad: str, B: int = 1, *args, **kwargs):
        """
        当前是测试用例函数，当前为描述
        :param Aad: 占位参数
        :param B:占位参数2
        :param args:其余占位参数
        :param kwargs:其余占位参数2
        :return:返回值
        """

        return str(Aad + str(B))


    print(Tool_data().out_tool_json())
