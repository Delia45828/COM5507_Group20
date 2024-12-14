import pandas as pd
import re
import emoji
import langid

# ----------- 读取csv文件，基础设定 -----------
# 设置文件路径
input_file_path = '/Users/delia/Documents/Pycharm/youtube/数据清洗/1000版(总)_防改copy.csv'
japanese_comments_file_path = '/Users/delia/Documents/Pycharm/youtube/数据清洗/日语评论.csv'
chinese_comments_file_path = '/Users/delia/Documents/Pycharm/youtube/数据清洗/中国评论.csv'
non_english_comments_file_path = '/Users/delia/Documents/Pycharm/youtube/数据清洗/非英语评论.csv'

# 读取 CSV 文件
try:
    df = pd.read_csv(input_file_path, encoding='utf-8')
except UnicodeDecodeError as e:
    print(f"读取文件时出错: {e}")

# 自定义函数：删除评论中的 @ 和后面的内容（包括后面的空格）
def remove_at_mentions(text):
    if isinstance(text, str):
        return re.sub(r'@\S*\s*', '', text)  # 删除 @ 后的内容和空格
    return text

# 自定义函数：删除文本中的 Emoji
def remove_emojis(text):
    if isinstance(text, str):
        return emoji.demojize(text)  # 将 Emoji 转换为文本描述
    return text

# 移除多余的字符：特殊字符、URLs 和电子邮件地址
def clean_text(text):
    if isinstance(text, str):
        # 移除URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        # 移除电子邮件
        text = re.sub(r'\S+@\S+', '', text)
        return text.strip()
    return ""

# 自定义函数：过滤掉三个字符以下的评论
def filter_short_comments(text):
    if isinstance(text, str):
        return len(text) > 3  # 仅保留三个字符以上的评论
    return False

# 应用清理函数到评论列
df['Comment'] = df['Comment'].apply(remove_at_mentions)
df['Comment'] = df['Comment'].apply(remove_emojis)
df['Comment'] = df['Comment'].apply(clean_text)
# 过滤掉三个词以下的评论
df = df[df['Comment'].apply(filter_short_comments)]

# 自定义函数判断评论是否包含日语
def is_japanese_dominant(text):
    if isinstance(text, str):
        total_chars = len(text)
        if total_chars == 0:
            return False
        japanese_chars = sum(1 for char in text if '\u3040' <= char <= '\u30ff')
        return (japanese_chars / total_chars) > 0.3  # 日语字符占比超过30%
    return False

# 提取日语评论并保存到新文件
japanese_comments = df[df['Comment'].apply(is_japanese_dominant)]
japanese_comments.to_csv(japanese_comments_file_path, index=False, encoding='utf-8')
print(f"日语评论已保存到 {japanese_comments_file_path}。数量: {len(japanese_comments)}")

# 从原数据中删除日语评论
df = df[~df['Comment'].apply(is_japanese_dominant)]

# 自定义函数判断评论或 User ID 是否包含中文
def contains_chinese(text):
    if isinstance(text, str):
        return any('\u4e00' <= char <= '\u9fff' for char in text)  # 检查汉字
    return False

# 提取中文评论
chinese_comments_from_comments = df[df['Comment'].apply(contains_chinese)]
# 提取 User ID 中包含中文的评论
chinese_comments_from_user_id = df[df['User ID'].apply(contains_chinese)]

# 合并中文评论和包含中文的 User ID 的评论
chinese_comments = pd.concat([chinese_comments_from_comments, chinese_comments_from_user_id]).drop_duplicates()

# 保存到新文件
chinese_comments.to_csv(chinese_comments_file_path, index=False, encoding='utf-8')
print(f"中文评论已保存到 {chinese_comments_file_path}。数量: {len(chinese_comments)}")

# 从原数据中删除中文评论和 User ID 中包含中文的评论
df = df[~(df['Comment'].apply(contains_chinese) | df['User ID'].apply(contains_chinese))]

# 自定义函数：清理文本
def clean_text_en(text):
    if isinstance(text, str):
        # 删除特殊字符和多余空格，保留撇号
        text = re.sub(r"[^\w\s,.?!':]", '', text)  # 只保留字母、数字、空格和部分标点（包括撇号）
        text = re.sub(r'\s+', ' ', text)  # 替换多个空格为一个空格
        return text.strip()  # 去除首尾空格
    return text

df['Comment'] = df['Comment'].apply(clean_text_en)

# 自定义函数判断评论语言并返回语言代码
def detect_language(text):
    try:
        lang, _ = langid.classify(text)  # 检测语言
        return lang  # 返回语言代码
    except:
        return 'unknown'  # 如果无法检测，返回 unknown

# 在 DataFrame 中添加语言列
df['Language'] = df['Comment'].apply(detect_language)

# 提取非英语评论并保存到新文件
non_english_comments = df[df['Language'] != 'en']
non_english_comments.to_csv(non_english_comments_file_path, index=False, encoding='utf-8')
print(f"非英语评论已保存到 {non_english_comments_file_path}。数量: {len(non_english_comments)}")

# 从原数据中删除非英语评论
df = df[df['Language'] == 'en']

# 最终保存剩余的 DataFrame
remaining_file_path = '/Users/delia/Documents/Pycharm/youtube/数据清洗/剩余评论.csv'
df.to_csv(remaining_file_path, index=False, encoding='utf-8')
print(f"剩余评论已保存到 {remaining_file_path}。数量: {len(df)}")
