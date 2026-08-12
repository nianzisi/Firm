def data_decision(evens: object | list, *args: str):
    """
    数据库专用的判断，只接受列表、或者单个对象
    :param evens: object | list
    :param args: 属性名称
    :return:
    """
    if isinstance(evens, list):
        for _even in evens:
            if base_decision(_even, *args):
                continue
            else:
                return False
        return True
    elif evens.__class__.__module__ == "__main__":
        return base_decision(evens, *args)

    else:
        return False


def base_decision(_even, *args):
    print(_even.__class__.__name__)
    print(_even.__class__.__module__)
    if args:
        for _args in args:
            print(type(_args))

            if hasattr(_even, _args):
                pass
            else:
                return False
        return True
    return False


class A:
    A=1

class B:
    A = 1

print(data_decision([A(),B()]))