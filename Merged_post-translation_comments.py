import pandas as pd

# 读取包含评论的主 CSV 文件
main_file_path = '/Users/delia/Documents/Pycharm/youtube/translated_non_en.csv'
df_main = pd.read_csv(main_file_path)

# 打印合并前的行数
print(f"主文件行数（合并前）: {len(df_main)}")

# 用 Translated_Comment 列替代 Comment 列
df_main['Comment'] = df_main['Translated_Comment']

# 删除 Translated_Comment 列
df_main.drop(columns=['Translated_Comment'], inplace=True)

# 读取其他两个 CSV 文件
file2_path = '/Users/delia/Documents/Pycharm/youtube/数据清洗/剩余评论.csv'
file3_path = '/Users/delia/Documents/Pycharm/youtube/translated_comments.csv'

df_file2 = pd.read_csv(file2_path)
df_file3 = pd.read_csv(file3_path)

# 处理 file3：替换 Comment 列并删除 Translated_Comment 列
df_file3['Comment'] = df_file3['Translated_Comment']
df_file3.drop(columns=['Translated_Comment'], inplace=True)

# 打印其他文件的行数
print(f"第二个文件行数: {len(df_file2)}")
print(f"第三个文件行数: {len(df_file3)}")

# 合并所有数据
merged_df = pd.concat([df_main, df_file2, df_file3], ignore_index=True)

# 删除合并后的数据中的 Language 列（如果存在）
if 'Language' in merged_df.columns:
    merged_df.drop(columns=['Language'], inplace=True)

# 打印合并后的行数
print(f"合并后的行数: {len(merged_df)}")

# 保存合并后的结果到新的 CSV 文件
output_file_path = '/Users/delia/Documents/Pycharm/youtube/数据清洗/trans_merged_output（删除Lang）.csv'  # 输出文件路径
merged_df.to_csv(output_file_path, index=False, encoding='utf-8')
print(f"合并后的内容已保存到 {output_file_path}。")

