# Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd
import subprocess
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

subprocess.Popen(r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chromeCookie"')

def scrape_page(driver, url):
    
    driver.get(url)
    time.sleep(5)
    driver.implicitly_wait(3.5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find the container 'area_list_search'
    area_list_search = soup.find('div', class_='area_list_search')
    if not area_list_search:
        return []  # Return an empty list if the container is not found

    # Find all posts within the container
    posts = area_list_search.find_all('div', class_='list_search_post')

    data = []

    for post in posts:
        post_data = {}

        try:
            post_data['title'] = post.find('span', {'class': 'title'}).get_text()
            post_data['blog_post'] = post.find('a', {'class': 'text'}).get_text()
            post_data['blogger'] = post.find('em', {'class': 'name_author'}).get_text()
            post_data['blog_name'] = post.find('span', {'class': 'name_blog'}).get_text()
            post_data['post_date'] = post.find('span', {'class': 'date'}).get_text()

            a_tag_bu = post.find('a', {'class': 'author'})
            post_data['blog_url'] = a_tag_bu.get('href') if a_tag_bu else "URL Not Found"

            a_tag_pu = post.find('a', {'class': 'desc_inner'})
            post_data['post_url'] = a_tag_pu.get('href') if a_tag_pu else "URL Not Found"

            data.append(post_data)
        
        except AttributeError:
            # Handle cases where a post might not have all details
            continue

    return data

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

all_data = []

for page in range(1, 3):
    url = f"https://section.blog.naver.com/Search/Post.naver?pageNo={page}&rangeType=PERIOD&orderBy=recentdate&startDate=2022-12-01&endDate=2023-02-28&keyword=%EB%AC%B4%EC%9D%B8%EA%B8%B0%EB%8F%84%EB%B0%9C"
    page_data = scrape_page(driver, url)
    all_data.extend(page_data)

driver.quit()

df = pd.DataFrame(all_data)
df.to_csv('test_blog.csv', index=False, encoding='utf-8-sig')

print(df.head())
