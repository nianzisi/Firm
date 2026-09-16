from typing import Dict, Any, List

from agent.check.clean_data import clean


def user_and_system_rule(_data: Dict[str, Any]) -> str | bool:
    # 3. 检查 content 类型
    if not isinstance(_data["content"], (str, list)):
        raise ValueError(f"Invalid content type: {type(_data['content']).__name__}, must be str or list")
    # 4. 检查可选字段 name（如果存在）
    if "name" in _data:
        if not isinstance(_data["name"], str):
            raise ValueError(f"Invalid name type: {type(_data['name']).__name__}, must be str")
    return True


def validate_assistant(data: Dict[str, Any]) -> str | bool:
    """校验 assistant 角色的消息"""

    # 3. 检查 content（可以是 str、list 或 None）
    #    在 prefix 模式下，content 通常必须有值；但在 tool_calls 场景下可能为 None
    if "content" not in data:
        # content 不是必须的（比如只有 tool_calls 时）
        pass
    elif data["content"] is not None and not isinstance(data["content"], (str, list)):
        raise ValueError(f"Invalid content type: {type(data['content']).__name__}, must be str, list, or None")

    # 4. 检查可选字段 name
    if "name" in data:
        if not isinstance(data["name"], str):
            raise ValueError(f"Invalid name type: {type(data['name']).__name__}, must be str")

    # 5. 检查 reasoning_content（思维链，仅 deepseek-reasoner 使用）
    if "reasoning_content" in data:
        if not isinstance(data["reasoning_content"], str):
            raise ValueError(f"Invalid reasoning_content type: {type(data['reasoning_content']).__name__}, must be str")

    # 6. 检查 tool_calls（工具调用）
    if "tool_calls" in data:
        if not isinstance(data["tool_calls"], list):
            raise ValueError(f"Invalid tool_calls type: {type(data['tool_calls']).__name__}, must be list")
        if not isinstance(data["reasoning_content"], str):
            raise ValueError(f"Invalid reasoning_content type: {type(data['reasoning_content']).__name__}, must be str")

        for tool_call in data["tool_calls"]:
            # 每个 tool_call 必须包含 id、type 和 function
            if not isinstance(tool_call, dict):
                raise ValueError(f"Each tool_call must be a dict, got {type(tool_call).__name__}")
            if "id" not in tool_call:
                raise ValueError("Each tool_call must have 'id'")
            if "type" not in tool_call or tool_call["type"] != "function":
                raise ValueError("Each tool_call must have 'type' = 'function'")
            if "function" not in tool_call or not isinstance(tool_call["function"], dict):
                raise ValueError("Each tool_call must have 'function' as dict")
            if "name" not in tool_call["function"] or "arguments" not in tool_call["function"]:
                raise ValueError("Each function must have 'name' and 'arguments'")

    # 7. 检查 prefix（Beta 功能）
    if "prefix" in data:
        if not isinstance(data["prefix"], bool):
            raise ValueError(f"Invalid prefix type: {type(data['prefix']).__name__}, must be bool")
        # prefix 为 True 时，content 必须有值且不能为空
        if data["prefix"] is True:
            if not data.get("content"):
                raise ValueError("prefix=True requires non-empty content")
    if len(data) == 1:
        raise ValueError("just role parameter")

    return True


def validate_tool(data: Dict[str, Any]) -> str | bool:
    """校验 tool 角色的消息（工具返回的结果）"""
    # 3. 检查 tool_call_id（必需）
    if "tool_call_id" not in data:
        raise ValueError("Missing required field: 'tool_call_id'")
    if not isinstance(data["tool_call_id"], str):
        raise ValueError(f"Invalid tool_call_id type: {type(data['tool_call_id']).__name__}, must be str")

    # 4. 检查 content（必需，工具返回的内容）
    if "content" not in data:
        raise ValueError("Missing required field: 'content'")
    if not isinstance(data["content"], str):
        # 工具返回内容通常是字符串，但也可以是 None 或空字符串
        if data["content"] is not None:
            raise ValueError(f"Invalid content type: {type(data['content']).__name__}, must be str or None")

    return True


_rule: dict = {
    "user": user_and_system_rule,
    "system": user_and_system_rule,
    "tool": validate_tool,
    "assistant": validate_assistant
}


def check(data: list[dict] | dict) -> str | bool:
    """
    仅检测类型是否正确和必要字段是否存在，是clean的下层接口，不应该单独使用
    :param data:
    :return:
    """
    result = True
    if isinstance(data, list):
        for _ in data:
            result = _rule.get(_.get("role"))(_) and result
    if isinstance(data, dict):
        result = _rule.get(data.get("role"))(data)
    return result


def clean_check(data: list[dict] | dict) -> dict | list[dict]:
    """
    先清洗数据在检查
    :param data: 数据(list[dict] | dict)
    :return: 清洗后的数据
    """
    clean_data = clean(data)
    if check(clean_data):
        return clean_data

    else:
        raise ValueError("clean的值错误的为False")


if __name__ == "__main__":
    test_data = {"r2e": "assistant", "content": "1", "asd": 123, "name": "ggg", "reasoning_content": "1",
                 "prefix": True}

    print(clean_check(test_data))
