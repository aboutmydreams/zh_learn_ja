import xml.etree.ElementTree as ET
import jaconv
import json
import way3

from collections import defaultdict

current_dir = way3.get_current_dir(__file__)
# JLPT 汉字数量（基于网络资源）
jlpt_levels = {
    "N5": 100,  # 约 80-103 个
    "N4": 300,  # 约 250-300 个
    "N3": 650,  # 约 650 个
    "N2": 1000,  # 约 1000 个
    "N1": 2000,  # 约 2000 个
}


# 解析 kanjidic2.xml
def get_joyo_kanji(xml_file=f"{current_dir}/data/kanjidic2.xml"):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    joyo_kanji = []

    for character in root.findall("character"):
        grade = character.find("misc/grade")
        if grade is not None:  # Jōyō Kanji 有 grade 字段
            kanji = character.find("literal").text
            joyo_kanji.append(kanji)

    return joyo_kanji


joyo_kanji = get_joyo_kanji()


# 解析 kanjidic2.xml，按频率排序
def parse_kanjidic2(xml_file=f"{current_dir}/data/kanjidic2.xml"):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        kanji_data = []

        for character in root.findall("character"):
            kanji = character.find("literal").text
            freq = character.find("misc/freq")
            freq_value = int(freq.text) if freq is not None else 9999
            readings = []
            for reading in character.findall("reading_meaning/rmgroup/reading"):
                r_type = reading.get("r_type")
                if r_type in ["ja_on", "ja_kun"]:
                    reading_text = reading.text
                    reading_hira = (
                        jaconv.kata2hira(reading_text)
                        if r_type == "ja_on"
                        else reading_text.split(".")[0]
                    )
                    readings.append(reading_hira)
            kanji_data.append(
                {"kanji": kanji, "freq": freq_value, "readings": readings}
            )

        # 按频率排序
        kanji_data.sort(key=lambda x: x["freq"])
        return kanji_data
    except FileNotFoundError:
        print("kanjidic2.xml not found. Using fallback list.")
        return [
            {"kanji": k, "freq": i, "readings": []} for i, k in enumerate(joyo_kanji)
        ]


# 生成 JLPT 汉字列表
def generate_jlpt_kanji_lists():
    kanji_data = parse_kanjidic2()
    jlpt_kanji = {
        "N5": [k["kanji"] for k in kanji_data[: jlpt_levels["N5"]]],
        "N4": [k["kanji"] for k in kanji_data[: jlpt_levels["N4"]]],
        "N3": [k["kanji"] for k in kanji_data[: jlpt_levels["N3"]]],
        "N2": [k["kanji"] for k in kanji_data[: jlpt_levels["N2"]]],
        "N1": [k["kanji"] for k in kanji_data[: jlpt_levels["N1"]]],
    }
    return jlpt_kanji


# 获取并输出汉字列表
jlpt_kanji = generate_jlpt_kanji_lists()

# 打印完整 N5 列表和其他级别的示例（前 50 个）
for level in ["N5", "N4", "N3", "N2", "N1"]:
    print(f"{level} 汉字列表（共 {len(jlpt_kanji[level])} 个）：")
    # N5 打印全部，其他级别打印前 50 个
    if level == "N5":
        print(jlpt_kanji[level])
    else:
        print(jlpt_kanji[level][:50])
    print()

# 保存到 JSON 文件
with open("jlpt_kanji_lists.json", "w", encoding="utf-8") as f:
    json.dump(jlpt_kanji, f, ensure_ascii=False, indent=2)


# 函数：获取同音字列表
def get_homophone_kanji(
    kanji_list=None, xml_file=f"{current_dir}kanjidic2.xml", use_xml=False
):
    """
    生成同音字列表，格式为 [{ '读音': [汉字列表] }, ...]。
    参数：
        kanji_list: dict，包含 N1-N5 的汉字列表（默认使用 jlpt_kanji）。
        xml_file: str，kanjidic2.xml 的路径（如果 use_xml=True）。
        use_xml: bool，是否从 kanjidic2.xml 提取汉字（否则使用 kanji_list）。
    返回：
        list，格式为 [{ '读音': [汉字列表] }, ...]。
    """
    homophones = defaultdict(list)

    if use_xml:
        # 从 kanjidic2.xml 提取汉字和读音
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for character in root.findall("character"):
                kanji = character.find("literal").text
                # 只处理 N1 级别的汉字（假设 N1 包含所有 Jōyō Kanji）
                if kanji_list and "N1" in kanji_list and kanji not in kanji_list["N1"]:
                    continue
                readings = []
                for reading in character.findall("reading_meaning/rmgroup/reading"):
                    r_type = reading.get("r_type")
                    if r_type in ["ja_on", "ja_kun"]:
                        reading_text = reading.text
                        reading_hira = (
                            jaconv.kata2hira(reading_text)
                            if r_type == "ja_on"
                            else reading_text.split(".")[0]
                        )
                        if reading_hira:  # 忽略空读音
                            readings.append(reading_hira)
                for reading in readings:
                    homophones[reading].append(kanji)
        except FileNotFoundError:
            print("kanjidic2.xml not found. Falling back to kanji_list.")
            use_xml = False

    if not use_xml:
        # 使用提供的 kanji_list 和 pykakasi 获取读音
        import pykakasi

        kakasi = pykakasi.kakasi()

        # 使用 N1 级别汉字（包含 N5-N1 所有汉字）
        target_kanji = kanji_list.get("N1", []) if kanji_list else []
        for kanji in target_kanji:
            result = kakasi.convert(kanji)
            for item in result:
                reading = item["hira"]
                if reading:  # 忽略空读音
                    homophones[reading].append(kanji)

    # 转换为所需格式 [{ '读音': [汉字列表] }, ...]
    result = [
        {"readings": k, "kanji": sorted(v)} for k, v in sorted(homophones.items())
    ]
    return result


# 执行函数
# 使用 N1-N5 汉字列表（替换为你的实际数据）
homophone_list = get_homophone_kanji(kanji_list=jlpt_kanji, use_xml=False)
all_reading_list = [i["readings"] for i in homophone_list]
print(all_reading_list)

# 保存到 JSON 文件
with open("homophone_kanji.json", "w", encoding="utf-8") as f:
    json.dump(homophone_list, f, ensure_ascii=False, indent=2)

# 示例：查找特定读音（如“かん”）
target_reading = "かん"
for item in homophone_list:
    if item["readings"] == target_reading:
        print(f"\n读音 '{target_reading}' 的同音字：{item['kanji']}")
