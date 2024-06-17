# Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd
import subprocess

subprocess.Popen(r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chromeCookie"')

def scrape_page(driver, url):
    
    driver.get(url)
    time.sleep(5)
    driver.implicitly_wait(3.5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find the container 'area_list_search'
    area_list_search = soup.find('div', class_='item_list')
    if not area_list_search:
        return []  # Return an empty list if the container is not found

    # Find all posts within the container
    posts = area_list_search.find_all('div', class_='article_item_wrap')

    data = []

    for post in posts:
        post_data = {}

        try:
            post_data['title'] = post.find('strong', {'class': 'title'}).get_text()
            post_data['cafe_post'] = post.find('p', {'class': 'text'}).get_text()
            post_data['cafe_name'] = post.find('span', {'class': 'cafe_name'}).get_text()
            post_data['post_date'] = post.find('span', {'class': 'date'}).get_text()

            a_tag_cu = post.find('a', {'class': 'cafe_info'})
            post_data['cafe_url'] = a_tag_cu.get('href') if a_tag_cu else "URL Not Found"

            data.append(post_data)
        
        except AttributeError:
            continue

    return data

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

all_data = []

for page in range(1,192):
    url = f"https://section.cafe.naver.com/ca-fe/home/search/articles?q=%EB%AC%B4%EC%9D%B8%EA%B8%B0%EB%8F%84%EB%B0%9C&t=1698909668031&em=1&od=1&p={page}"
    page_data = scrape_page(driver, url)
    all_data.extend(page_data)

driver.quit()

df = pd.DataFrame(all_data)
df.to_csv('naver_cafe_drone_221227_231101.csv', index=False, encoding='utf-8-sig')

print(df.head())