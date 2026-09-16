import json

import requests

from agent.message import Message_Control
from agent.chat import Chat
from agent.navel.var import var


class Send(Chat):

    def __init__(self, _Message: Message_Control):
        super().__init__()
        self._class = _Message

    def set_Message_class(self, _Message: Message_Control = None) -> object:
        """
        设置需要绑定的message对象
        :param _Message: message对象，默认值为None
        :return: 返回当前绑定的message对象
        """
        if isinstance(_Message, Message_Control):
            self._class = _Message
        return self._class

    @property
    def send_message(self) -> list:
        """
        message 信息
        :return: message 信息
        """
        return self._class()

    def add_ask(self, msg: str) -> None:
        """
        往message中添加用户消息
        :param msg: 用户消息
        :return: None
        """
        self._class.message_user_create(msg)

    def add_system(self, msg: str) -> None:
        """
        往message中添加系统消息
        :param msg: 系统消息
        :return: None
        """
        self._class.message_system_create(msg)

    def question_start(self, msg: str):
        # Todo 测试使用的临时组合方案
        self._class.message_remove_system()
        self.add_ask(msg=msg)
        text = self.send().text
        print(text)
        print(type(text))
        print(json.loads(text)["choices"][0]["message"])

    def send(self) -> object:
        """
        发送对话
        :return: request对象
        """
        self._class.message_remove_system()
        self.get_message(self.send_message)
        result = requests.request(
            method="POST",  # 或者 GET，你这里没写
            url=self.set_url(),
            headers=self.set_headers(),
            json=self.set_payload()  # 注意：payload 一般用 json 或 data 参数
        )
        return result

    def just_send_msg(self):
        # Todo 测试使用的临时组合方案
        self._class.message_remove_system()
        self.get_message(self.send_message)
        return {
            "method": "POST",  # 或者 GET，你这里没写
            "url": self.set_url(),
            "headers": self.set_headers(),
            "json": self.set_payload()
        }  # 注意：payload 一般用 json 或 data 参数


if __name__ == "__main__":
    from agent.tools.get_sql import tool
    from agent.tools.get_sql import Tool_data


    @tool()
    def books_tool(name: str):
        """
        检索未知名称的名称解释
        :param name: 未知名称
        :return:返回名称解释
        """

        return "布鲁斯是具有灵性且忠诚的狗"


    B = Message_Control()
    A = Send(B)
    A.set_tools_env(value=Tool_data().out_tool_json())
    A.add_system(var(r"D:\Seed\firm\agent\navel\template\one.txt", {"这个是个占位符啊，喵~": "‘布鲁斯’"}))
    replace_read2 = "你来开车，布鲁斯"
    print(A.send_message)
    print(A.just_send_msg())
    # A.question_start(replace_read2)
