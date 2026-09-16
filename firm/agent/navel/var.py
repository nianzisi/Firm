"""占位符渲染器
目前的思路是："""
import os
import re


def var(path: str, key: dict) -> str:
    """
    占位符渲染
    :param path: 地址
    :param key: 替换字典
    :return: str
    """
    if os.path.exists(path):
        with open(path, mode='r', encoding="utf-8", errors=None, newline=None) as f:
            read = f.read()

            del_note_read = re.sub(r"#.+?#", "", read)

            def replace(mach):
                msg = mach.group(1).strip()
                if msg not in key:
                    raise ValueError(f"var的key缺少{msg}的值，无该键对")  # TODO 写入日志

                return key.get(msg)

            replace_read = re.sub(r"\{\{([^}]+)}}", replace, del_note_read)

            # print(replace_read)  # TODO 写入日志

            return replace_read
    else:
        # 可扩写其他重试函数
        raise ValueError("var的path不存在")  # TODO 写入日志


if __name__ == "__main__":
    replace_read2 = var(r"D:\Seed\firm\agent\navel\template\one.txt", {"这个是个占位符啊，喵~": "喵喵~"})
    print(replace_read2)
