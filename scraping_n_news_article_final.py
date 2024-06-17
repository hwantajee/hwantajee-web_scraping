# Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd
import subprocess

subprocess.Popen(r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chromeCookie"')

def clean_text(text):
    return text.replace('\n', '').replace('\t', '').strip()

def scrape_news_head(driver):

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # news article (excl.comments >> div.newsct)
    newsct = soup.find('div', class_='newsct')
    head_data = {}

    if newsct:
        head = newsct.find('div', class_='media_end_head go_trans')
        if head:
            head_data['post_date'] = clean_text(head.find('span', {'class': 'media_end_head_info_datestamp_time _ARTICLE_DATE_TIME'}).get_text())   # 게시일
            head_data['title'] = clean_text(head.find('h2', {'class': 'media_end_head_headline'}).get_text())                                       # 제목

            journalist_element = head.find('em', {'class': 'media_end_head_journalist_name'})
            head_data['journalist'] = clean_text(journalist_element.get_text()) if journalist_element else 'N/A'                                    # 기자명

            comment_count_element = head.find('a', {'class': 'media_end_head_cmtcount_button _COMMENT_COUNT_VIEW'})
            head_data['cnt_comment'] = clean_text(comment_count_element.get_text()) if comment_count_element else '0'                               # 총 댓글 수
    return head_data

def scrape_news_body(driver):

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # news article (excl.comments >> div.newsct)
    newsct = soup.find('div', class_='newsct')
    body_data = {}
    
    if newsct:
        body = newsct.find('div', class_='newsct_body')
        if body:
            try:
                body_data['article'] = clean_text(body.find('article', {'class': 'go_trans _article_content'}).get_text())
                body_data['rate_useful'] = clean_text(body.select_one('#likeItCountViewDiv > ul > li.u_likeit_list.useful > a > span.u_likeit_list_count._count').get_text())           # 쏠쏠정보
                body_data['rate_wow'] = clean_text(body.select_one('#likeItCountViewDiv > ul > li.u_likeit_list.wow > a > span.u_likeit_list_count._count').get_text())                 # 흥미진진
                body_data['rate_touched'] = clean_text(body.select_one('#likeItCountViewDiv > ul > li.u_likeit_list.touched > a > span.u_likeit_list_count._count').get_text())         # 공감백배
                body_data['rate_analytical'] = clean_text(body.select_one('#likeItCountViewDiv > ul > li.u_likeit_list.analytical > a > span.u_likeit_list_count._count').get_text())   # 분석탁월
                body_data['rate_recommend'] = clean_text(body.select_one('#likeItCountViewDiv > ul > li.u_likeit_list.recommend > a > span.u_likeit_list_count._count').get_text())     # 후속강추
            except AttributeError:
                pass
    return body_data

def scrape_page(driver, url):
    driver.get(url)
    time.sleep(5)

    articles_info = []

    article_anchors = driver.find_elements(By.CSS_SELECTOR, 'a.info')

    for anchor in article_anchors:
        href = anchor.get_attribute('href')
        if href.startswith('https://n.news.naver.com'):
            parent_element = anchor.find_element(By.XPATH, './..')
            try:
                press_badge = parent_element.find_element(By.CLASS_NAME, 'spnew.ico_pick')
                press_info = parent_element.find_element(By.CLASS_NAME, 'info.press').text.replace(press_badge.text, '').strip()
            except NoSuchElementException:
                press_info = parent_element.find_element(By.CLASS_NAME, 'info.press').text.strip()
            articles_info.append((href, press_info))
    return articles_info

def scrape_news_article(driver, article_url):
    driver.get(article_url)
    time.sleep(5)

    head_data = scrape_news_head(driver)
    body_data = scrape_news_body(driver)
    article_data = {**head_data, **body_data}
    article_data['url'] = article_url
    return article_data

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

all_articles_data = []

for page in range(0, 2): 
    search_url = f"https://search.naver.com/search.naver?where=news&query=무인기도발&sort=1&pd=3&ds=2022.12.01&de=2023.02.28&start={page}1"
    articles_info = scrape_page(driver, search_url)
    
    for article_url, press_info in articles_info:
        article_data = scrape_news_article(driver, article_url)
        article_data['press'] = press_info 
        all_articles_data.append(article_data)

driver.quit()

df_articles = pd.DataFrame(all_articles_data)
df_articles.to_csv('all_news_articles.csv', index=False, encoding='utf-8-sig')

print(df_articles.head())