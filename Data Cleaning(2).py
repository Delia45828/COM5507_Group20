import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from collections import Counter
from nltk import pos_tag  # 词性标注


# ----------- 读取csv文件，基础设定 -----------
# 设置文件路径
input_file_path = '/Users/delia/Documents/Pycharm/youtube/数据清洗/翻译后清洗分词/trans_merged_output（删除Lang）.csv'
cleaned_file_path = '/Users/delia/Documents/Pycharm/youtube/数据清洗/trans_cleaned(en_sentiment).csv'  # 为情感分析
final_file_path = '/Users/delia/Documents/Pycharm/youtube/数据清洗/trans_cleaned(en_segmentation).csv'  # 分词后的文件
word_freq_output_file = '/Users/delia/Documents/Pycharm/youtube/数据清洗/trans_word_frequency_analysis.csv'  # 词频分析

# 读取 CSV 文件
try:
    df = pd.read_csv(input_file_path, encoding='utf-8')
except UnicodeDecodeError as e:
    print(f"读取文件时出错: {e}")


# ----------- Data cleaning for sentiment analysis-----------
# 根据 “Likes” 值从大到小重新排序
df.sort_values(by='Likes', ascending=False, inplace=True)

# 消除重复评论（除Likes外每一项都重复才算重复）
df.drop_duplicates(subset=['Video Link', 'User ID', 'Comment'], inplace=True)

# 创建 'Basic_Cleaned' 列，进行基本的清洗
df['Basic_Cleaned'] = df['Comment'].str.strip()  # 去除首尾空格

# 移除包含空值的行
df.dropna(subset=['Basic_Cleaned'], inplace=True)

# 移除无效评论（空字符串或仅包含空格）
df = df[df['Basic_Cleaned'] != '']

# 调试：打印清洗后的评论示例
print("清洗后的部分评论:")
print(df['Basic_Cleaned'].head(10))

# 保存简单清洗后的数据
df.to_csv(cleaned_file_path, index=False, encoding='utf-8')
print(f"简单清洗后的数据已保存为 {cleaned_file_path}。清洗后剩余评论数量: {len(df)}")


# ----------- 进一步分词处理 -----------
# 转为小写
df['ReCleaned_Comment'] = df['Basic_Cleaned'].str.lower()
# 移除所有标点符号（在分词之前）
df['ReCleaned_Comment'] = df['ReCleaned_Comment'].apply(lambda x: re.sub(r'[^\w\s]', '', x))
# 移除数字（在分词之前）
df['ReCleaned_Comment'] = df['ReCleaned_Comment'].apply(lambda x: re.sub(r'[0-9]', '', x))

# 分词
nltk.download('punkt')
df['Tokens'] = df['ReCleaned_Comment'].apply(word_tokenize)

# 去除停用词
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
df['Tokens'] = df['Tokens'].apply(lambda x: [word for word in x if word.lower() not in stop_words])

# 移除无效评论（空列表）
df = df[df['Tokens'].map(len) > 0]  # 确保 Tokens 列中没有空列表

# 调试：打印清洗后的评论示例
print(df[['ReCleaned_Comment', 'Tokens']].head(10))

# 词形还原
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

# 初始化词形还原器
lemmatizer = WordNetLemmatizer()

# 自定义词形还原函数
def lemmatize_with_pos(tokens):
    pos_tags = pos_tag(tokens)  # 获取词性标注
    lemmatized_words = []

    for word, tag in pos_tags:
        if tag.startswith('J'):  # 形容词
            lemmatized_words.append(lemmatizer.lemmatize(word, pos='a'))
        elif tag.startswith('V'):  # 动词
            lemmatized_words.append(lemmatizer.lemmatize(word, pos='v'))
        elif tag.startswith('N'):  # 名词
            lemmatized_words.append(lemmatizer.lemmatize(word, pos='n'))
        elif tag.startswith('R'):  # 副词
            lemmatized_words.append(lemmatizer.lemmatize(word, pos='r'))
        else:
            lemmatized_words.append(lemmatizer.lemmatize(word))  # 默认为名词

    return lemmatized_words

# 应用词形还原
df['Lem_Tokens'] = df['Tokens'].apply(lemmatize_with_pos)

# 调试：查看结果
print("词形还原前后的Tokens对比:")
print(df[['Tokens', 'Lem_Tokens']].head(10))

# 输出为最终处理后的 CSV 文件
df.to_csv(final_file_path, index=False, encoding='utf-8')
print(f"最终处理后的数据已保存为 {final_file_path}。清洗后剩余评论数量: {len(df)}")


# ----------- 词频分析 -----------
# 词频统计
all_words = [word for tokens in df['Lem_Tokens'] for word in tokens]
word_freq = Counter(all_words)

# 将词频转换为 DataFrame
word_freq_df = pd.DataFrame(word_freq.items(), columns=['Word', 'Frequency'])
word_freq_df = word_freq_df.sort_values(by='Frequency', ascending=False)

# 保存词频分析结果到 CSV 文件
word_freq_df.to_csv(word_freq_output_file, index=False, encoding='utf-8')
print(f"词频分析结果已保存到 {word_freq_output_file}。")

# 查看前 15 个词频
print(word_freq_df.head(15))
