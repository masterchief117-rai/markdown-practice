import requests  
from bs4 import BeautifulSoup  
import pandas as pd  
from datetime import datetime  

def fetch_baidu_news():  
    url = ''  
    headers = {  
        'User-Agent': 'Mozilla/5.0'  
    }  

    response = requests.get(url, headers=headers)  
    response.encoding = 'utf-8'  # 设置响应编码  

    if response.status_code == 200:  
        soup = BeautifulSoup(response.text, 'html.parser')  

        news_list = []  

        # 假设新闻列表在 class 为 'l-left-col' 的 div 中  
        news_sections = soup.find_all('div', class_='l-left-col')  
        if not news_sections:  
            print("未找到新闻板块")  
            return None  

        for section in news_sections:  
            news_items = section.find_all('a')  
            for item in news_items:  
                title = item.get_text(strip=True)  
                href = item.get('href')  

                # 过滤无效链接和空标题  
                if not title or not href or href.startswith('javascript'):  
                    continue  

                news_data = {  
                    '标题': title,  
                    'URL': href,  
                    '分类': '百度新闻',  
                    '时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
                }  
                news_list.append(news_data)  

        # 将新闻列表转换为 DataFrame  
        news_df = pd.DataFrame(news_list)  
        return news_df  
    else:  
        print(f"请求失败，状态码：{response.status_code}")  
        return None  

def save_to_csv(news_df, filename='baidu_news.csv'):  
    news_df.to_csv(filename, index=False, encoding='utf-8-sig')  
    print(f"新闻数据已保存到 {filename}")  

if __name__ == "__main__":  
    news_df = fetch_baidu_news()  
    if news_df is not None:  
        save_to_csv(news_df)