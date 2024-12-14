import pandas as pd
import glob
import re

# 读取原始 CSV 文件（根据实际编码格式调整 encoding 参数）
df = pd.read_csv('/Users/delia/Documents/Pycharm/youtube/csv_files/china travel.csv', encoding='utf-8')

# 将 DataFrame 写入新的 CSV 文件，使用 UTF-8 编码
df.to_csv('/Users/delia/Documents/Pycharm/youtube/csv_files/china_travel_utf8.csv', encoding='utf-8', index=False)

# 定义要合并的 CSV 文件路径
file_pattern = '/Users/delia/Documents/Pycharm/youtube/csv_files/*.csv'
all_files = glob.glob(file_pattern)

# 检查是否找到任何文件
if not all_files:
    print("未找到符合条件的 CSV 文件，请检查路径和文件名。")
else:
    dataframes = []

    for filename in all_files:
        try:
            df = pd.read_csv(filename)
            dataframes.append(df)
        except Exception as e:
            print(f"读取文件 {filename} 时出错: {e}")

    if dataframes:
        combined_df = pd.concat(dataframes, ignore_index=True)

        # 去重前的总数
        total_before_deduplication = len(combined_df)
        print(f"去重前的总数: {total_before_deduplication}")

        # 提取视频 ID
        combined_df['Video ID'] = combined_df['Video URL'].apply(
            lambda x: re.search(r'v=([a-zA-Z0-9_-]+)', x).group(1) if re.search(r'v=([a-zA-Z0-9_-]+)', x) else None
        )

        # 根据 Video ID 去重
        combined_df.drop_duplicates(subset='Video ID', keep='first', inplace=True)

        # 去重后的总数
        total_after_deduplication = len(combined_df)
        print(f"去重后的总数: {total_after_deduplication}")

        # 将合并后的数据写入新的 CSV 文件
        combined_df.to_csv('merged_videos.csv', index=False, encoding='utf-8')
        print("合并完成，已删除重复项。")

        # 读取 merged_videos.csv 文件
        df = pd.read_csv('merged_videos.csv')

        # 按照 'View Count' 列的值从大到小对数据进行排序
        sorted_df = df.sort_values(by='View Count', ascending=False)

        # 将排序后的数据保存为一个新的 CSV 文件
        sorted_df.to_csv('sorted_merged_videos.csv', index=False, encoding='utf-8')

        print("已按照 'View Count' 列从大到小排序并保存新文件成功。")
    else:
        print("没有可合并的数据框。")