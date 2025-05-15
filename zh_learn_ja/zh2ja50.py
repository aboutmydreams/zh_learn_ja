import pykakasi

# 初始化 pykakasi
kakasi = pykakasi.kakasi()

# 输入汉字
text = "炒"

# 转换为平假名
result = kakasi.convert(text)
print(result)
# hiragana = result[0]["hira"]  # 获取平假名
# romaji = result[0]["roma"]  # 获取罗马音

# print(f"汉字: {text}")
# print(f"平假名: {hiragana}")
# print(f"罗马音: {romaji}")
