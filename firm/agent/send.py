import json

import requests

from agent.message import Message_Control
from agent.chat import Chat
from agent.navel.var import var
from agent.tools.get_sql import Tool_data


class Send(Chat):

    def __init__(self, _Message: Message_Control, category: str = None):
        super().__init__()
        self._class = _Message
        self._tools = Tool_data()
        self._tool_category = category
        self.only_tool_max_times = 10
        self.new_only_tool_times = 0
        self.all_tool_max_times = 20
        self.new_all_tool_times = 0

        self.out_tools_env()

    def out_tools_env(self):
        if tool_env := Tool_data().out_tool_json(self._tool_category):
            self.set_tools_env(value=tool_env)

    def set_tools_category(self, name: str):
        if isinstance(name, str):
            self._tool_category = name
        return self._tool_category

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

    def add_assistant_return(self, msg: dict):
        self._class.message_add_end(msg)

    def add_tool(self, msg: dict):
        self._class.message_add_end(msg)

    def emit_tool(self, msg: dict):
        if self.new_all_tool_times <= self.all_tool_max_times and self.new_only_tool_times <= self.only_tool_max_times:
            #  Todo 还没有想出如何记录单个工具的调用次数
            self.new_all_tool_times += 1
            self.add_tool(self._tools.emit_on(msg))
            return True
        raise ValueError("工具调用次数过多")

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

        text = result.text
        assistant_msg = json.loads(text)["choices"][0]["message"]
        self._class.message_add_end(assistant_msg)

        if 'tool_calls' in assistant_msg:
            for _ in assistant_msg["tool_calls"]:
                self.emit_tool(_)
            self.send()
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


    @tool()
    def books_tool(name: str):
        """
        检索未知名称的名称解释
        :param name: 未知名称
        :return:返回名称解释
        """

        return "喵娘就是喵娘啊"


    B = Message_Control()
    A = Send(B)
    A.add_system(var(r"D:\Seed\firm\agent\navel\template\one.txt", {"这个是个占位符啊，喵~": "喵娘"}))
    replace_read2 = "你好啊，喵喵"
    A.add_ask(replace_read2)
    # A.send()
    print(A.send_message)
    print(A.just_send_msg())
