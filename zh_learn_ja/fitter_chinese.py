import pandas as pd
import re


def is_only_chinese(text):
    """检查字符串是否只包含汉字"""
    # 正则表达式匹配：只包含汉字（包括日语汉字）、中文标点或空格的字符串
    pattern = re.compile(
        r"^[\u4e00-\u9fff\u3000-\u303f\u3400-\u4dbf\uf900-\ufaff\uff00-\uffef\s]+$"
    )
    return bool(pattern.fullmatch(text))
