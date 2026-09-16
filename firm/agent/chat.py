import os

from agent.creat_env import creat_env


class Env_get:
    api_key: str = None
    api_url: str = None
    model: str = None
    llm_env: dict = None

    def __init__(self):
        creat_env()
        self.creat_env()
        self.check_env()

    def creat_env(self):
        """
        创建当前env信息
        :return: None
        """
        self.api_key: str = os.environ["API_KEY"]  # 请替换为你的真实密钥
        self.api_url: str = os.environ["api_url"]
        self.model: str = os.environ["MODEL"]
        self.llm_env = {"stream": False if os.environ["stream"] == "False" else True,
                        "max_tokens": int(os.environ["max_tokens"]),
                        "temperature": float(os.environ["temperature"])}
        return None

    def check_env(self):
        """
        检查env是否缺少关键值
        :return: None
        """
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

    def __init__(self):
        self.owner = Env_get()
        self._message: list[dict] = []

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
                          "messages": self._message,
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

    def set_tools_env(self, value: list[dict]):
        """
        将tools消息写入env
        :param value: tools消息
        :return: None
        """
        #  value Todo clean规则
        if value:
            parameter = {"tools": value}
            self.set_llm_env(**parameter)

    def get_message(self, result: list = None) -> list:
        """
        不应该在调用时使用参数result
        :param result: 默认
        :return: dict
        """
        if result:
            self._message = result
        return self._message


if __name__ == "__main__":
    pass
