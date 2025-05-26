import pandas as pd
import way3
from zh_learn_ja.fitter_chinese import is_only_chinese

current_dir = way3.get_current_dir(__file__)
# 读取CSV文件
df = pd.read_csv(
    f"{current_dir}/zh_learn_ja/data/n1_word_9000.csv"
)  # 替换为你的输入文件名

# 过滤掉"汉字"列中只包含汉字的行
filtered_df = df[~df["汉字"].apply(is_only_chinese)]

# 保存到新的CSV文件
filtered_df.to_csv("output_filtered.csv", index=False, encoding="utf-8-sig")

print("处理完成，已保存到 output_filtered.csv")
