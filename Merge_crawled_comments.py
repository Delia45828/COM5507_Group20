import pandas as pd
import glob

# 定义包含 CSV 文件的目录
csv_files = glob.glob("/Users/delia/Documents/Pycharm/youtube/1000版/*.csv")

# 创建一个空的 DataFrame
combined_df = pd.DataFrame()

print(f"找到 {len(csv_files)} 个 CSV 文件。")

# 遍历所有 CSV 文件并将其合并
for csv_file in csv_files:
    print(f"正在读取文件: {csv_file}")
    try:
        df = pd.read_csv(csv_file)
        print(f"文件 {csv_file} 读取成功，包含 {df.shape[0]} 行和 {df.shape[1]} 列。")
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    except Exception as e:
        print(f"读取文件 {csv_file} 时出错: {e}")

# 将合并后的 DataFrame 保存为新的 CSV 文件
output_file = "1000版(总)_combined_output.csv"
combined_df.to_csv(output_file, index=False)
print(f"合并完成，结果已保存为 {output_file}，总行数: {combined_df.shape[0]}。")