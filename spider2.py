import requests
from requests.exceptions import RequestException
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import pymongo
import os
from hashlib import md5

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 30)

client = pymongo.MongoClient('localhost')
db = client['JanDanOoxx']

def get_one_page():
    try:
        browser.get('http://jandan.net/ooxx')
        get_picture()
    except TimeoutError:
        get_one_page()

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
    previous_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#comments > div:nth-child(4) > div > a.previous-comment-page')))
    if previous_button:
        previous_button.click() # 这里点击下一页
        get_picture()    # 递归调用！

def save_to_mongodb(content):
    try:
        if db['picture_link'].insert(content):
            print('存储到mongodb成功！', content)
    except Exception:
        print('存储到mongodb失败！')

def download_images(url):
    print('正在请求图片', url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
    }
    try:
        res = requests.get(url, headers=headers)
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

def main():
    get_one_page()

if __name__ == '__main__':
    main()

# 也可以爬取整整个网页，虽然比较代码比较简洁，但是其中get_one_page()函数存在巨大缺陷