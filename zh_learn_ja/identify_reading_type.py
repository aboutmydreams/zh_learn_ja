import xml.etree.ElementTree as ET
import jaconv
from typing import Optional
import way3

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
    判断一个汉字的特定读音是音读（on'yomi）、训读（kun'yomi）、人名读音（nanori）还是其他。

    参数：
        kanji (str): 单个汉字（如“換”）。
        reading (str): 读音（平假名，如“かん”或“かえ”）。
        xml_file (str): kanjidic2.xml 的路径（默认 "./kanjidic2.xml"）。
        use_xml (bool): 是否使用 kanjidic2.xml（否则使用 pykakasi）。

    返回：
        str: "on"（音读）、"kun"（训读）、"nanori"（人名读音）、"unknown"（其他）或 None（未找到）。
    """
    if not kanji or not reading:
        return None

    if use_xml:
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            for character in root.findall("character"):
                if character.find("literal").text == kanji:
                    # 检查音读（ja_on）
                    for r in character.findall(
                        "reading_meaning/rmgroup/reading[@r_type='ja_on']"
                    ):
                        if jaconv.kata2hira(r.text) == reading:
                            return "on"
                    # 检查训读（ja_kun）
                    for r in character.findall(
                        "reading_meaning/rmgroup/reading[@r_type='ja_kun']"
                    ):
                        # 匹配完整读音或主要部分
                        r_text = r.text
                        if r_text == reading or r_text.split(".")[0] == reading:
                            return "kun"
                    # 检查人名读音（nanori）
                    for r in character.findall("reading_meaning/nanori"):
                        if r.text == reading:
                            return "nanori"
                    return "unknown"  # 汉字存在，但读音未匹配
            return None  # 汉字未找到
        except FileNotFoundError:
            print(f"kanjidic2.xml not found at {xml_file}. Falling back to pykakasi.")
            use_xml = False

    if not use_xml:
        import pykakasi

        kakasi = pykakasi.kakasi()
        result = kakasi.convert(kanji)

        for item in result:
            if item["hira"] == reading:
                # 启发式推断：短读音（1-2 音节）为音读，复杂读音为训读
                if len(reading) <= 2 and all(c in jaconv.hiragana for c in reading):
                    return "on"
                return "kun"
        return None

    return None


if __name__ == "__main__":
    # 扩展测试用例
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
        ("換", "かえ"),  # 训读（かえ.る）
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
        ("非", "ひ"),  # 音读
        ("海", "かい"),  # 音读
        ("海", "うみ"),  # 训读
        ("学", "がく"),  # 音读
        ("学", "まな"),  # 训读（まな.ぶ）
        ("名", "めい"),  # 音读
        ("名", "な"),  # 训读
        ("名", "みょう"),  # 人名读音（nanori）
    ]

    # 运行测试
    print("测试结果：")
    for kanji, reading in test_cases:
        result = identify_reading_type(kanji, reading, use_xml=True)
        print(f"汉字: {kanji}, 读音: {reading}, 类型: {result}")
