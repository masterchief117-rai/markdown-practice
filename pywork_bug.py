import requests 
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import re
import time

def find_baidu_news(url,headers):     #headers 用来模仿浏览器的请求，防止爬虫被拒
                                      #'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                                      # Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0'
    r = requests.get(url,headers=headers)
    r.raise_for_status()
    r.encoding = 'utf-8'  #将内容全部转换为utf-8的编码

    if r.status_code == 200:              #三位数状态码200表示的是请求被正常回应
        soup = BeautifulSoup(r.text,features='html.parser')

        list_news = []     #创建一个空列表方便存储与数据处理

        section_news = soup.find_all('div',class_='l-left-col')  #百度新闻的主要新闻内容都集中在左侧
        
        if not section_news:
            print("error")
        
        for section in section_news:            #这里就要去寻找其链接和标题，一般在‘a’中
            items_news = section.find_all('a')

            for item_news in items_news:
                title = item_news.get_text(strip=True)   #之所以strip=True是为了保证文本干净，没有多余空格和换行
                href = item_news.get('href')    #获取url链接(这里会存在一个相对还是绝对链接的问题)
         
                publish_time = get_publish_time(href,headers)  #获取新闻发布时间与作者

                info_news = {
                    'title':title,
                    'url':href,
                    'publish_time':publish_time,

                }

                list_news.append(info_news)
                print(f"标题：{title}")  
                print(f"链接：{href}")  
                #print(f"发布时间：{publish_time}")  

                time.sleep(1) #防止过快访问
        news_df = pd.DataFrame(list_news)         
        return news_df
    else:
        print(f"请求失败,其状态码为{r.status_code}")
        return None

def save_to_csv(news_df, filename='baidu_news1.csv'):  
    news_df.to_csv(filename, index=False, encoding='utf-8-sig')  
    print(f"新闻数据已保存到 {filename}")  






def get_publish_time(url,headers):
    try:
        r = requests.get(url,headers=headers,timeout=10)
        r.encoding = 'utf-8'

        if r.status_code == 200:
            soup = BeautifulSoup(r.text,features='html.parser')

            text = r.text
            match = re.search(r'(\d{4}年\d{1,2}月\d{1,2}日 \d{2}:\d{2})', text)  #根据百度新闻的时间，用正则表达式搜索
            if not match:
                match = re.search(r'(\d{4}-\d{1,2}-\d{1,2} \d{2}:\d{2})', text)
            if match:
                return match.group(1)
        else:
            return '请求失败'
    
    except Exception as e:
        print(f"请求异常",{e})
        return '请求异常'
    

url = 'http://news.baidu.com'
headers = {
    'User_Agent':'Mozilla/5.0'
}
news_df = find_baidu_news(url,headers).iloc[3:-1]
if news_df is not None:  
    save_to_csv(news_df)
        

