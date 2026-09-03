import os
import requests
import json

from dataclasses import dataclass

from agent.creat_env import creat_env

from agent.Even_bus import EventBus, event_on, event_emit


class Env_get:
    api_key: str = None
    api_url: str = None
    model: str = None
    llm_env: dict = None

    def __init__(self):
        creat_env()
        self.creat_env()

    def creat_env(self):
        self.api_key: str = os.environ["API_KEY"]  # 请替换为你的真实密钥
        self.api_url: str = os.environ["api_url"]
        self.model: str = os.environ["MODEL"]
        self.llm_env = {"stream": False if os.environ["stream"] == "False" else True,
                        "max_tokens": int(os.environ["max_tokens"]),
                        "temperature": float(os.environ["temperature"])}
        return None

    def check_env(self):
        if not self.api_url or not self.api_key or not self.model:
            raise ValueError("环境缺少关键值")
        return None


class Chat:
    """
    只对url、headers、payload负责
    功能：加载url，设置url
        加载headers，设置headers
        加载payload， 设置payload
        不允许修改messages
    """

    def __init__(self, category):
        self.owner = Env_get()
        EventBus().on(category=category, obj=self.get_message)
        self.message: list[dict] = []

    def set_url(self, url: str = None) -> str:
        """
        允许设置url，若没有则返回默认值。默认值会被新值覆盖
        :param url: path
        :return: url：str
        """
        if url:
            self.owner.api_url = url
        return self.owner.api_url

    def set_headers(self, api_key: str = None) -> dict:
        """
        允许设置密钥，若没有则返回默认值。默认值会被新值覆盖
        :param api_key: 密钥
        :return: dict
        """
        if api_key:
            self.owner.api_key = api_key
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.owner.api_key}"  # Bearer Token 认证方式
        }

    def set_payload(self) -> dict:
        """
        应设置前置3步：
            第一步：获取model
            第二步：获取messages
            第三步：获取其他llm配置
        最后：组装payload
        :return:
        """
        _payload: dict = {"model": self.set_model(),
                          "messages": self.message,
                          **self.set_llm_env()}
        return _payload

    def set_model(self, model: str = None, ) -> str:
        """
        允许设置model，若没有则返回默认值。默认值会被新值覆盖
        :param model: str
        :return: str
        """
        if model:
            self.owner.model = model
        return self.owner.model

    def set_llm_env(self, **kwargs) -> dict:
        """
        允许设置llm其他配置，若没有则返回默认值。默认值会被新值覆盖
        :param kwargs: 配置字典
        :return: dict
        """
        if kwargs:
            for _key, _value in kwargs.items():
                self.owner.llm_env[_key] = _value
        return self.owner.llm_env

    def get_message(self, result: dict = None) -> dict:
        """
        不应该在调用时使用参数result
        :param result: 默认
        :return: dict
        """
        if result:
            self.message = result
        return self.message


class Message_Control:
    """
    只对messages负责
    功能：校验单条message是否合法，校验全部message是否合法
        应当只允许messages只有一条system:需要收集system位置信息
        允许添加messages（user，system，assistant）
        对外暴露messages，允许外部访问messages但不允许修改
    """

    def __init__(self, _category):
        self._category = _category
        self._message: list[dict] = []
        self._system_address: list[int] = []

    def __call__(self, *args, **kwargs):
        print(self.message)
        #  TODO 写入日志
        return self.message

    def get_system_address(self) -> list:
        """
        获取system的位置
        :return: list
        """
        address = []
        if self.message:
            for number, _ in enumerate(self.message):
                _key = _.get("role", None)
                if _key == "system":
                    address.append(number)
        return address

    def message_remove_system(self):
        """
        清除非最新的system内容
        :return:
        """
        address = self.get_system_address()
        address.reverse()
        length = len(address)
        if length > 1:
            for _ in address[:-1]:
                self.message.pop(_)
        if length == 1:
            self.message_add_start(self.message[address[0]])
            self.message.pop(address[0] + 1)
        return self

    def message_fmark_check_dict(self, msg: list[dict]):
        """
        进阶判断
        """
        order = True
        error = []
        ok = True
        if msg:
            _message = msg
        else:
            _message = self.message

        def handle_content(dix, content):
            if content is None:
                return f"Error: {dix}缺少content", False
            elif isinstance(content, (str, list)):
                return None, True  # 无错误
            else:
                return f"Error: {dix}期待str|list，但当前是{type(content)}", False

        def handle_system(dix, _order):
            if dix > 0:
                return f"Warning: system信息应放置在序列0，但当前是{dix}", True
            return True, True

        def handle_user(dix, _order):
            if not _order:
                return f"Warning: {dix}消息应该是assistant", True
            return None, True  # 无警告

        def handle_assistant(dix, _order):
            if _order:
                return f"Warning: {dix}消息应该是user", True
            return None, True

        def handle_any(dix, _order):
            return f"Error: {dix}出现非法role", False

        check_dict = {
            "user": handle_user,
            "system": handle_system,
            "assistant": handle_assistant,
        }

        def decision(result: tuple):
            nonlocal ok, order
            msg, success = result

            # 顺序切换逻辑：只有 role 是 user 或 assistant 且无错误时才切换
            if msg is None and success:
                order = not order
                return

            if not success:
                ok = False
            if isinstance(msg, str):
                error.append(msg)

        for _number, _value in enumerate(_message):
            _role = _value.get("role", None)
            _content = _value.get("content", None)

            # 检查 content
            content_result = handle_content(_number, _content)
            decision(content_result)

            # 检查 role
            handler = check_dict.get(_role, handle_any)
            role_result = handler(_number, order)
            decision(role_result)

        if not ok:
            raise ValueError("\n".join(error))
        return error

    def message_simple_check(self, msg: dict = None):
        if msg:
            if not (msg.get("role", None) in ("system", "user", "assistant")):
                return False
            if not (isinstance(msg.get("content", None), (str, list))):
                return False
            return True
        return False

    def message_insert(self, msg: dict = None, address: int = None):
        print()  # TODO 日志
        if msg and isinstance(msg, dict) and isinstance(address, int):
            self.message.insert(address, msg)
            return self
        else:
            raise ValueError(f"msg: {msg} \n address: {address} 或类型错误")

    def message_add_start(self, msg: dict = None):
        self.message_insert(msg, 0)
        return self

    def message_add_end(self, msg: dict = None):
        _message = self.message.copy()
        _message.append(msg)
        self.message = _message
        return self

    def message_create(self, role: str, content: str | list):
        msg = {"role": role, "content": content}
        if self.message_simple_check(msg):
            self.message_add_end(msg)
            return self
        else:
            raise ValueError("错误的值")

    def message_create_many(self, msg: list[dict]):
        if isinstance(msg, list):
            _msg = self.message + msg
            try:
                error = self.message_fmark_check_dict(_msg)
                print(error)  # TODO 日志
                self.message = _msg  # 有需要可以增加严格等级，最严格是error为空
            except ValueError as e:
                print(e)  # TODO 日志
            return self
        raise ValueError("msg不为list")

    def message_user_create(self, content: str | list):
        return self.message_create(role="user", content=content)

    def message_check_length(self):
        # TODO 检测token数量 类,待做
        return len(str(self.message))

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        if self._message != value:
            self._message = value
            EventBus().emit(category=self.category, result=self.message)
        else:
            pass

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        if self._category != value:
            self._category = value
        else:
            pass


if __name__ == "__main__":
    pass
