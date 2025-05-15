import xml.etree.ElementTree as ET
import jaconv
from typing import Optional
import json
import way3
from collections import defaultdict

current_dir = way3.get_current_dir(__file__)


def is_hiragana(char: str) -> bool:
    """判断一个字符是否为平假名"""
    return "\u3040" <= char <= "\u309f"


def identify_reading_type(
    kanji: str,
    reading: str,
    xml_file: str = f"{current_dir}/data/kanjidic2.xml",
    use_xml: bool = True,
) -> Optional[str]:
    """
    判断一个汉字的特定读音是音读（on'yomi）还是训读（kun'yomi）。

    参数：
        kanji (str): 单个汉字（如"換"）。
        reading (str): 读音（平假名，如"かん"或"かえ"）。
        xml_file (str): kanjidic2.xml 的路径（默认 "./kanjidic2.xml"）。
        use_xml (bool): 是否使用 kanjidic2.xml（否则使用 pykakasi）。

    返回：
        str: "on"（音读）、"kun"（训读）、"unknown"（未知）或 None（未找到）。
    """
    if not kanji or not reading:
        return None

    if use_xml:
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # 查找指定汉字
            for character in root.findall("character"):
                if character.find("literal").text == kanji:
                    for r in character.findall("reading_meaning/rmgroup/reading"):
                        r_type = r.get("r_type")
                        r_text = r.text
                        if r_type == "ja_on":
                            # 音读：片假名，转为平假名
                            if jaconv.kata2hira(r_text) == reading:
                                return "on"
                        elif r_type == "ja_kun":
                            # 训读：平假名，去除送假名（如"い.う"）
                            if r_text.split(".")[0] == reading:
                                return "kun"
                    return "unknown"  # 读音存在但未标记为音读或训读
            return None  # 汉字未找到
        except FileNotFoundError:
            print(f"kanjidic2.xml not found at {xml_file}. Falling back to pykakasi.")
            use_xml = False

    if not use_xml:
        # 使用 pykakasi 推断读音类型
        import pykakasi

        kakasi = pykakasi.kakasi()
        result = kakasi.convert(kanji)

        for item in result:
            if item["hira"] == reading:
                # 推断逻辑：音读通常短（1-2 音节），训读可能更长或有送假名
                # 这是不精确的推断，仅作 fallback
                if len(reading) <= 2 and all(is_hiragana(c) for c in reading):
                    return "on"  # 假设短读音为音读
                return "kun"  # 假设长读音或复杂读音为训读
        return None  # 读音未找到

    return None


# 示例：测试函数
# 测试用例
test_cases = [
    # N5 级别
    ("一", "いち"),  # 音读
    ("日", "にち"),  # 音读
    ("日", "ひ"),  # 训读
    ("人", "じん"),  # 音读
    ("人", "ひと"),  # 训读
    ("山", "さん"),  # 音读
    ("山", "やま"),  # 训读
    ("見", "けん"),  # 音读
    ("見", "み"),  # 训读
    # N4 级别
    ("店", "てん"),  # 音读
    ("店", "みせ"),  # 训读
    ("道", "どう"),  # 音读
    ("道", "みち"),  # 训读
    # N3-N2 级别
    ("換", "かん"),  # 音读
    ("換", "かえ"),  # 训读
    ("生", "せい"),  # 音读
    ("生", "い"),  # 训读
    ("漢", "かん"),  # 音读
    ("漢", "はん"),  # 音读
    # N1 级别
    ("行", "こう"),  # 音读
    ("行", "い"),  # 训读
    ("行", "おこな"),  # 训读（おこな.う）
    ("議", "ぎ"),  # 音读
    ("議", "はか"),  # 训读（罕见）
    # 特殊情况
    ("国", "こく"),  # 音读
    ("国", "くに"),  # 训读
    ("水", "すい"),  # 音读
    ("水", "みず"),  # 训读
    ("読", "どく"),  # 音读
    ("読", "よ"),  # 训读
    ("長", "ちょう"),  # 音读
    ("長", "なが"),  # 训读
    ("重", "じゅう"),  # 音读
    ("重", "おも"),  # 训读
    # 边缘情况
    ("漢", "xyz"),  # 不存在的读音
    ("非", "ひ"),  # 音读（测试未知情况）
]

for kanji, reading in test_cases:
    result = identify_reading_type(kanji, reading, use_xml=True)
    print(f"汉字: {kanji}, 读音: {reading}, 类型: {result}")


# 可选：生成所有同音字的读音类型
def get_homophone_reading_types(
    kanji_list: list, xml_file: str = f"{current_dir}/data/kanjidic2.xml"
) -> list:
    """
    生成所有汉字的同音字列表，并标注每个读音的类型（音读/训读）。
    返回格式：[{ 'readings': '读音', 'kanji': [{'kanji': '汉字', 'type': 'on/kun'}]}]
    """
    homophones = defaultdict(list)

    tree = ET.parse(xml_file)
    root = tree.getroot()

    for character in root.findall("character"):
        kanji = character.find("literal").text
        if kanji not in kanji_list:  # 仅处理提供的汉字列表（如 N1）
            continue
        for r in character.findall("reading_meaning/rmgroup/reading"):
            r_type = r.get("r_type")
            r_text = r.text
            if r_type == "ja_on":
                reading = jaconv.kata2hira(r_text)
                homophones[reading].append({"kanji": kanji, "type": "on"})
            elif r_type == "ja_kun":
                reading = r_text.split(".")[0]
                if reading:
                    homophones[reading].append({"kanji": kanji, "type": "kun"})

    # 转换为输出格式
    result = [{"readings": k, "kanji": v} for k, v in sorted(homophones.items())]
    return result


# 运行测试
print("测试结果：")
for kanji, reading in test_cases:
    result = identify_reading_type(kanji, reading, use_xml=True)
    print(f"汉字: {kanji}, 读音: {reading}, 类型: {result}")
