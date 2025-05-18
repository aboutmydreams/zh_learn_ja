from zh_learn_ja.find_py import get_reading_csv_by_type
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import way3

current_dir = way3.get_current_dir(__file__)


def save_dict_to_csv_with_pandas(data_dict, csv_file_path):
    """
    使用 Pandas 将字典保存为 CSV 文件

    参数:
    data_dict (dict): 要保存的字典，键为读音，值为对应的汉字字符串
    csv_file_path (str): CSV 文件的保存路径
    """
    try:
        # 将字典转换为 DataFrame
        df = pd.DataFrame(list(data_dict.items()), columns=["读音", "对应的汉字"])

        # 保存为 CSV 文件，设置编码和索引选项
        df.to_csv(csv_file_path, index=False, encoding="utf-8-sig")

        print(f"成功保存 CSV 文件到: {csv_file_path}")

    except Exception as e:
        print(f"保存 CSV 文件时出错: {e}")


def count_characters(input_string):
    """
    统计字符串中每个字符的出现次数，并按出现次数由高到低排序

    参数:
    input_string (str): 要统计的字符串

    返回:
    list: 按出现次数排序的字符及其出现次数的列表
    """
    char_count = {}
    for char in input_string:
        if char in char_count:
            char_count[char] += 1
        else:
            char_count[char] = 1

    # 按出现次数排序
    sorted_char_count = sorted(
        char_count.items(), key=lambda item: item[1], reverse=True
    )
    return sorted_char_count


def plot_character_counts(char_counts):
    """
    绘制字符出现次数的条形图

    参数:
    char_counts (list): 字符及其出现次数的列表，例如 [('る', 1137), ('い', 422), ...]
    """
    # 分离字符和出现次数
    characters, counts = zip(*char_counts)

    # 设置字体，确保支持日语
    font_path = "/Library/Fonts/Arial Unicode.ttf"  # 替换为你系统中支持日语的字体路径
    font_prop = fm.FontProperties(fname=font_path)

    # 创建条形图
    plt.figure(figsize=(12, 6))
    plt.bar(characters, counts, color="skyblue")
    plt.xlabel("字符", fontproperties=font_prop)
    plt.ylabel("出现次数", fontproperties=font_prop)
    plt.title("字符出现次数统计", fontproperties=font_prop)
    plt.xticks(rotation=45, fontproperties=font_prop)
    plt.tight_layout()  # 自动调整布局
    plt.show()


# 使用示例
if __name__ == "__main__":
    # 假设这是你的字典数据
    # readings_dict = get_reading_csv_by_type()
    # readings_dict = get_reading_csv_by_type(
    #     identify_reading_fitter=["kun"], min_word_count=1
    # )

    # 保存为 CSV 文件
    # save_dict_to_csv_with_pandas(readings_dict, "japanese_readings_kun.csv")

    # 统计所有汉字词频
    all_n1_words = way3.read_file(
        f"{current_dir}/zh_learn_ja/data/all_n1_word.txt"
    ).content.split("\n")
    word_acounts = count_characters("".join(all_n1_words))
    # 绘制字符出现次数的条形图
    plot_character_counts(word_acounts[:70])
    plot_character_counts(word_acounts[70:140])
    plot_character_counts(word_acounts[140:210])
