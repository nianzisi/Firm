"""监听器"""


class EventBus:
    """事件监听器类"""
    _instance = None  # 类变量，存唯一实例

    def __new__(cls):
        if cls._instance is None:  # 还没创建过
            cls._instance = super().__new__(cls)  # 创建
            cls._instance._listeners = {}  # 初始化
        return cls._instance  # 返回唯一实例

    def on(self, category: str, obj: object):
        if category not in self._listeners:
            self._listeners[category] = []

        if obj not in self._listeners[category]:
            self._listeners[category].append(obj)

    def emit(self, category: str, *args, **kwargs):
        if category in self._listeners:
            for obj in self._listeners[category]:
                obj(*args, **kwargs)


def event_on(category: str):
    """
    事件监听器注册装饰函数
    :param category: 注册名称
    :return: None
    """

    def event(func):
        def wrapper():
            EventBus().on(category=category, obj=func)

        return wrapper

    return event


def event_emit(*, category: str, result_name: str, **data):
    """
    事件监听器的执行函数，接受任意赋值
    :param result_name: 结果名称
    :param category: 类型名称
    :return: func(*arges, **kwargs)
    """

    def event(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            kwargs[result_name] = result
            kwargs = kwargs | data
            EventBus().emit(category=category, *args, **kwargs)
            return result

        return wrapper

    return event


class Logger:
    """日志"""
    _instance = None  # 类变量，存唯一实例

    _level = {"level": 2,  # 控制输出等级

              "print": 3,

              "waring": 3,

              "bug": 1,

              "debug": 3}

    def __new__(cls):
        if cls._instance is None:  # 还没创建过
            cls._instance = super().__new__(cls)  # 创建
            cls._instance._listeners = {}
        return cls._instance  # 返回唯一实例

    def __init__(self):
        self._instance._listeners = {
            "print": [self._prints],
            "waring": [self._waring_prints],
            "bug": [self._debug_prints],
            "debug": []
        }  # 初始化

    def set_level(self, who: str, level: int):
        self._level[who] = level

    @staticmethod
    def _prints(comment: str, *args, **kwargs):
        print(f"\033[97m{comment}\033[0m")

    @staticmethod
    def _waring_prints(comment: str, *args, **kwargs):
        print(f"\033[93m{comment}\033[0m")

    @staticmethod
    def _debug_prints(comment: str, *args, **kwargs):
        print(f"\033[31m{comment}\033[0m")
        import sys
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(f"当前异常: {exc_type, exc_value, exc_traceback}")  # ← 看看当前是什么异常
        import traceback

        print(traceback.format_exc())
        raise

    def on(self, category: str, obj: object):
        if category not in self._listeners:
            self._listeners[category] = []

        if obj not in self._listeners[category]:
            self._listeners[category].append(obj)

    def emit(self, category: str, comment: str, *args, **kwargs):
        if self._level[category] < self._level["level"]:
            if category in self._listeners:
                for obj in self._listeners[category]:
                    try:
                        obj(comment, *args, **kwargs)
                    except Exception as e:
                        print(f"\033[31m重大错误:{e}\033[0m")
        else:
            pass


def logger_emit(level: str, comment: str):
    """
    日志触发装饰函数，可以使用Logger().set_level设定等级
    :param level: 日志等级（print，waring，bug，debug）
    :param comment: 备注信息，会被打印出来
    :return: try：return func(*args, **kwargs) except：打印日志
    """

    def log(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                logger = Logger()
                logger.emit(level, comment, *args, **kwargs)

        return wrapper

    return log


if __name__ == "__main__":
    def test_base(level: str):
        @logger_emit(level, "日志emit测试失败")
        def test(box: list):
            box.append(1)
            print("日志emit测试")

        test(1)
        test([])


    test_base("print")
    test_base("waring")
    test_base("bug")
