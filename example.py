import pandas as pd  
import time  
from selenium import webdriver  
from selenium.webdriver.edge.options import Options  
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC  

def find_baidu_news_selenium(url):  
    options = Options()  
    options.use_chromium = True  # 使用 Chromium 内核，EDGE浏览器使用的就是这个内核
    options.add_argument('--headless')  # 无头模式，并不会打开浏览器窗口
    options.add_argument('--disable-gpu')  
    options.add_argument('--no-sandbox')  
    options.add_argument('--window-size=1920,1080')  
    options.add_argument('--log-level=3')  

    
    driver = webdriver.Edge(options=options)  
    driver.get(url)  
    time.sleep(1)    #等待页面加载完成，防止页面信息不完全

    news_list = []  

    # 定位主页上的新闻链接  
    news_items = driver.find_elements(By.CSS_SELECTOR, 'div#pane-news ul li a')  

    if not news_items:    #遍历每一个新闻项目
        print("未找到新闻项")  
        driver.quit()  
        return None  

    for item in news_items:  
        title = item.text  
        href = item.get_attribute('href')  

        # 打开新闻链接的新标签页    
        #这里的基本原理其实就是：使用request库直接查看动态数据是看不到的，通过开发者工具查看页面
        #确实能看到信息，那么我就选择先打开链接再去爬取数据，模拟浏览器的行为
        driver.execute_script("window.open(arguments[0]);", href)  #这里就是打开新闻链接的标签页
        driver.switch_to.window(driver.window_handles[1])  
        time.sleep(3)    #等待页面加载完成

        # 使用显式等待  
        wait = WebDriverWait(driver, 1)  

        # 尝试获取发布时间  
        publish_time = "未找到发布时间"  
        possible_time_selectors = [  
            '.date',  
            '.pub-date',  
            '.publish-time',  
            '.time',  
            'span.date',  
            'div.date'  
        ]  

        for selector in possible_time_selectors:  #遍历每一个选择器来找到发布时间
            try:  
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))  
                publish_time_text = element.text.strip()  
                if publish_time_text:  
                    publish_time = publish_time_text  
                    break  
            except:  
                continue  

        # 尝试获取作者或来源  
        author = "未找到作者/来源"  
        possible_author_selectors = [  
            '.source',   
            '.author',   
            '.writer',   
            '.article-source',   
            'span.source',   
            'div.source',  
            'meta[name="author"]'  
        ]  

        for selector in possible_author_selectors:  
            try:  
                if selector.startswith('meta'):  
                    # 处理 meta 标签  
                    element = driver.find_element(By.CSS_SELECTOR, selector)  
                    author_text = element.get_attribute('content').strip()  
                else:  
                    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))  
                    author_text = element.text.strip()  
                if author_text:  
                    # 去除可能的前缀  
                    author = author_text.replace("来源：", "").replace("作者：", "").strip()  
                    break  
            except:  
                continue  

        news_info = {  
            'title': title,  
            'url': href,  
            'publish_time': publish_time,  
            'author': author  
        }  

        news_list.append(news_info)  
        print(f"标题：{title}")  
        print(f"链接：{href}")  
        print(f"发布时间：{publish_time}")  
        print(f"作者/来源：{author}")  

        # 关闭当前标签页，返回主页面  
        driver.close()  
        driver.switch_to.window(driver.window_handles[0])  
        time.sleep(1)  

    driver.quit()  
    news_df = pd.DataFrame(news_list)  
    return news_df  

def save_to_csv(news_df, filename='baidu_news.csv'):  
    news_df.to_csv(filename, index=False, encoding='utf-8-sig')  
    print(f"新闻数据已保存到 {filename}")  

url = 'https://news.baidu.com'  
news_df = find_baidu_news_selenium(url)  
if news_df is not None:  
    save_to_csv(news_df)  
else:  
    print("未能获取新闻数据")