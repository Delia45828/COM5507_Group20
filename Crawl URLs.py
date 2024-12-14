from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import random
import csv
import os

# 定义关键词
keyword = "China travel"  

# 定义CSV文件路径
videos_file_path = os.path.join(os.getcwd(), 'videos_to_crawl.csv')

# 定义表头
videos_headers = ['Video URL', 'Video Title', 'Youtuber', 'Publish Date', 'View Count']

# 检查并创建文件
if not os.path.exists(videos_file_path):
    with open(videos_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=videos_headers)
        writer.writeheader()  # 只写入表头一次

# 初始化浏览器
options = webdriver.ChromeOptions()
options.add_argument("--lang=en-US")  # 设置语言为英语
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# 存储已爬取的视频链接，防止重复爬取
seen_videos = set()

# 解析观看量:将不同的单位转换成对应的数字
def parse_view_count(view_count_text):
    try:
        view_count_text = view_count_text.replace("views", "").strip()
        if "M" in view_count_text:
            return int(float(view_count_text.replace("M", "").replace(",", "").strip()) * 1000000)
        elif "K" in view_count_text:
            return int(float(view_count_text.replace("K", "").replace(",", "").strip()) * 1000)
        return int(view_count_text.replace(",", "").strip())
    except ValueError:
        print(f"无法解析观看量文本: {view_count_text}")
        return None

# 滚动并收集视频链接
def scroll_and_collect_links(driver, total_links_required=50):
    seen_videos = set()#使用一个集合来存储已收集的视频链接。集合用于避免重复的视频链接，因为集合中的元素是唯一的。
    current_scroll_position = 0#记录当前页面的滚动位置，初始为 0。
    scroll_attempts = 0#记录滚动尝试次数。

    while len(seen_videos) < total_links_required and scroll_attempts < 50:#这行代码启动了一个 while 循环，继续滚动页面并收集视频链接，直到：收集到足够的链接；滚动尝试次数超过最大值
        driver.execute_script("window.scrollBy(0, window.innerHeight);")#通过执行 JavaScript 滚动页面，向下滚动一个屏幕的高度。
        time.sleep(random.uniform(3, 5))  # 添加一个随机的停留时间（3到5秒之间），模拟用户的滚动行为。通过这种方式，可以减缓页面加载过快的问题，避免被识别为机器行为

        # 通过 XPath 获取所有视频链接。
        videos = driver.find_elements(By.XPATH, "//*[@id='title-wrapper']//h3/a")

        for video in videos:
            link = video.get_attribute('href')
            # 检查链接是否是 YouTube 视频链接，并且未被收集
            if link and link.startswith("https://www.youtube.com/watch") and link not in seen_videos:
                seen_videos.add(link)
                # 在收集到视频链接时报告数量
                print(f"已收集到视频链接：{len(seen_videos)}/{total_links_required}")

        new_scroll_position = driver.execute_script("return document.documentElement.scrollHeight")#获取页面的总高度（document.documentElement.scrollHeight），它代表页面内容的总高度，包括当前不可见的部分
        if new_scroll_position <= current_scroll_position:
            scroll_attempts += 1
        else:
            scroll_attempts = 0
            current_scroll_position = new_scroll_position

    return list(seen_videos)


# 抓取视频数据
def fetch_video_data(driver, link):
    # 在开始抓取之前随机等待
    time.sleep(random.uniform(3, 5))#随机等待3到5秒，以模拟人类行为，避免被检测为爬虫。

    driver.get(link)
    time.sleep(random.uniform(3, 5))#再次进行随机等待，确保页面加载完成。

    retry_count = 0
    while retry_count < 3:  # 使用 while 循环来实现最多3次的重试机制，防止偶尔由于网络问题或页面加载失败导致抓取失败。
        try:
            # 等待视频标题加载
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="title"]/h1/yt-formatted-string')),
                       message="视频标题未加载")#使用显式等待，直到页面中视频标题加载完成。
            time.sleep(random.uniform(2, 5))  # 随机等待时间

            # 抓取视频标题
            title_element = driver.find_element(By.XPATH, '//*[@id="title"]/h1/yt-formatted-string')#定位视频标题元素。
            video_title = title_element.text.strip()

            # 抓取观看量
            view_count_element = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="info"]/span[1]'))
            )
            view_count_text = view_count_element.text.strip()#获取观看量文本并去掉两端的空格
            view_count = parse_view_count(view_count_text)
            # 筛选播放量超过1w的视频
            if view_count is None or view_count < 10000:
                print(f"观看量不足（{view_count}），跳过视频: {link}")
                return None

            # 抓取发布时间，筛选不是今年的视频
            publish_time_element = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="info"]/span[3]'))
            )
            publish_time_text = publish_time_element.text.strip()
            if "year" in publish_time_text or "years" in publish_time_text:  # 带year或者years的肯定就是一年前
                print(f"发布时间不符合条件，跳过视频: {publish_time_text}")
                return None

            # 抓取 Youtuber 名字
            youtuber_element = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="text"]/a'))
            )
            youtuber_name = youtuber_element.text.strip()

            return video_title, view_count, publish_time_text, youtuber_name

        except TimeoutException as e:
            print(f"加载超时，重试... 错误信息: {e}")
            retry_count += 1
            time.sleep(random.uniform(3, 5))  # 增加重试之间的等待时间

    print(f"视频 {link} 加载失败，跳过。")
    return None


# 主程序逻辑
try:
    search_url = f"https://www.youtube.com/results?search_query={keyword.replace(' ', '+')}&hl=en"
    driver.get(search_url)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

    time.sleep(random.uniform(3, 5)) 

    # 点击 "Videos" 按钮
    videos_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//yt-chip-cloud-chip-renderer[.//yt-formatted-string[contains(text(), 'Videos')]]")))
    videos_button.click()
    print("已点击 'Videos' 按钮")

    time.sleep(random.uniform(2, 4))  # 等待片刻以确保页面加载更新

    # 开始滚动页面并收集视频链接
    video_links = scroll_and_collect_links(driver)

    # 添加符合条件的视频计数器
    valid_video_count = 0

    for link in video_links:
        video_data = fetch_video_data(driver, link)
        if video_data:
            video_title, view_count, publish_time, youtuber_name = video_data
            seen_videos.add(link)
            valid_video_count += 1  # 增加计数器
            print(f"\t符合条件的视频链接: {link}，"
                  f"\n观看量: {view_count}，发布时间: {publish_time}, 当前已抓取到的符合条件的视频数量: {valid_video_count}")

            # 将符合条件的视频信息存储到文件
            with open(videos_file_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=videos_headers)
                writer.writerow({
                    'Video URL': link,
                    'Video Title': video_title,
                    'Youtuber': youtuber_name,
                    'Publish Date': publish_time,
                    'View Count': view_count
                })

        # 当符合条件的视频数量达到30时退出循环
        if valid_video_count >= 30:
            print("已找到30个符合条件的视频，停止收集。")
            break

    # 检查符合条件的视频数量
    if len(seen_videos) < 30:
        print(f"警告: 只找到 {len(seen_videos)} 个符合条件的视频，低于预期的 30 个。")

finally:
    driver.quit()
    print(f"数据已写入文件：{videos_file_path}")