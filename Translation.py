import pandas as pd
from deep_translator import GoogleTranslator

# 读取 CSV 文件
input_file_path = '/Users/delia/Documents/Pycharm/youtube/数据清洗/非英语评论.csv'  # 替换为你的文件路径
df = pd.read_csv(input_file_path)

# 定义翻译函数
def translate_comment(comment):
    if not isinstance(comment, str) or not comment.strip():
        return comment  # 返回原文
    try:
        return GoogleTranslator(source='auto', target='en').translate(comment)
    except Exception as e:
        print(f"翻译出错: {e}")
        return comment  # 返回原文以防出错

# 翻译“Comment”列
df['Translated_Comment'] = df['Comment'].apply(translate_comment)

# 保存结果到新的 CSV 文件
output_file_path = 'translated_non_en.csv'  # 输出文件路径
df.to_csv(output_file_path, index=False, encoding='utf-8')
print(f"翻译后的内容已保存到 {output_file_path}。")