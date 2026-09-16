class Message:
    """
    只对messages负责
    功能：校验单条message是否合法，校验全部message是否合法
        应当只允许messages只有一条system:需要收集system位置信息
        允许添加messages（user，system，assistant）
        对外暴露messages，允许外部访问messages但不允许修改
    """

    def __init__(self):
        self.message: list[dict] = []
        self._system_address: list[int] = []

    def __call__(self, *args, **kwargs) -> list:
        """
        打印当前message信息
        :param args: 占位
        :param kwargs: 占位
        :return: message信息
        """
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
        if length >= 1:
            for _ in address[1:]:
                self.message.pop(_)
            self.message_add_start(self.message[address[-1]])
            self.message.pop(address[-1] + 1)
        return self

    def message_fmark_check_dict(self, msg: list[dict] = None) -> list | dict | bool:
        """
        检查msg是否符合规则，默认检查self的message
        :param msg: 默认为self
        :return:
        """
        from agent.check.meassge import clean_check
        if isinstance(msg, list):
            return clean_check(msg)
        elif msg is None:
            return clean_check(self.message)
        else:
            raise ValueError(f"{msg}非法格式")

    def message_simple_check(self, msg: dict) -> list | dict | bool:
        """
        检查单个msg是否符合规则
        :param msg: dict
        :return: list | dict | bool
        """
        from agent.check.meassge import clean_check
        return clean_check(msg)

    def message_insert(self, msg: dict = None, address: int = None):
        """
        单msg信息添加在任意位置
        :param msg:dict
        :param address: int
        :return: self
        """
        msg = self.message_simple_check(msg)
        print()  # TODO 日志
        if msg and isinstance(msg, dict) and isinstance(address, int):
            if address == -1:
                self.message.append(msg)
            elif address >= 0:
                self.message.insert(address, msg)
            return self
        else:
            raise ValueError(f"msg校验错误 \n address: {address} 或类型错误")

    def message_add_start(self, msg: dict = None):
        """
        信息添加在开头
        :param msg: dict
        :return: self
        """
        self.message_insert(msg, 0)
        return self

    def message_add_end(self, msg: dict = None):
        """
          信息添加在末尾
          :param msg: dict
          :return: self
          """
        self.message_insert(msg=msg, address=-1)
        return self

    def message_create_many(self, msg: list[dict]):
        """
        一次性往末尾添加一个msg历史对话
        :param msg: list[dict]
        :return: self
        """
        msg = self.message_fmark_check_dict(msg)
        if msg and isinstance(msg, list):
            self.message += msg
            return self
        raise ValueError("msg校验错误")


class Message_Control(Message):

    def __init__(self):
        super().__init__()

    def message_create(self, role: str, content: str | list):
        """
        创建角色消息
        :param role: 角色
        :param content: 内容
        :return: self
        """
        msg = {"role": role, "content": content}
        self.message_add_end(msg)
        return self

    def message_user_create(self, content: str | list):
        """
        创建user消息
        :param content: 内容
        :return: self
        """
        return self.message_create(role="user", content=content)

    def message_system_create(self, content: str | list):
        """
        创建system消息
        :param content: 内容
        :return: self
        """
        return self.message_create(role="system", content=content)

    def message_check_length(self):
        # TODO 检测token数量 类,待做
        return len(str(self.message))

    def __call__(self, *args, **kwargs) -> list:
        """
        输出message
        :param args: 占位符
        :param kwargs: 占位符
        :return: message
        """
        return self.message
