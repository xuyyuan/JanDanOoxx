import requests
from requests.exceptions import RequestException, Timeout
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pymongo
import os
from hashlib import md5
import re

from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')
prefs = {
    'profile.default._content_setting_values':{
        'images': 2
    }
}
chrome_options.add_experimental_option('prefs', prefs)
browser = webdriver.Chrome(chrome_options=chrome_options)
wait = WebDriverWait(browser, 10)

client = pymongo.MongoClient('localhost')
db = client['JanDanOoxx']

def get_first_page():
    try:
        browser.get('http://jandan.net/ooxx')
        get_picture()
        total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#comments > div:nth-child(4) > div > span')))
        total = int(re.compile(r'(\d+)').search(total.text).group(1)) # 别忘了total标签要家加上text
        return total
    except TimeoutError:
        get_first_page()

def get_picture():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#comments > ol')))
    html = browser.page_source
    soup = BeautifulSoup(html, 'lxml')
    items = soup.select('.commentlist li[id*="comment"]')
    # print(items)
    for item in items:
        # picture_url = {
        #     'image': item.select('.text p img')[0].attrs['src']
        # }
        #  上面字典这种形式用于存储到mongoDB中
        picture_url = item.select('.text p img')[0].attrs['src']
        if picture_url:
            # save_to_mongodb(picture_url)
            download_images(picture_url)

def get_next_page(page_num):
    try:
        previous_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#comments > div:nth-child(4) > div > a.previous-comment-page')))
        if previous_button:
            previous_button.click()  # 这里点击下一页
            get_picture()  # 递归调用！
    except TimeoutError:
        get_next_page()

def save_to_mongodb(content):
    try:
        if db['picture_link'].insert(content):
            print('存储到mongodb成功！', content)
    except Exception:
        print('存储到mongodb失败！')

def download_images(url):
    print('正在请求图片', url)
    try:
        res = requests.get(url)
        if res.status_code == 200:
            save_images(res.content)
        return None
    except RequestException as e:
        print('请求图片失败', e.args)
        return None

def save_images(content):
    file_path = '{0}\{1}.{2}'.format(os.path.join(os.getcwd(), 'images'), md5(content).hexdigest(), 'jpg')
    # 以上一句巧妙地指定了要存储地每个文件的文件名（使用md5的方法），并放在一个文件夹里面
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as file:
            file.write(content)

if __name__ == '__main__':
    try:
        total = get_first_page()
        for page_num in range(total-1):
            get_next_page(page_num)
    except Exception:
        print('出错啦！')
    finally:
        browser.close()