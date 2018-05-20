import requests
import re
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import pymongo

client = pymongo.MongoClient('localhost')
db = client['JanDanOoxx']

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
}

def get_one_page(url):
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.text
        return None
    except RequestException:
        return None

def get_page_num(url):
    html = get_one_page(url)
    pattern = re.compile(r'div.*?cp-pagenavi">.*?current-comment-page">\[(.*?)\]</span>.*?<div>', re.S)
    result = re.search(pattern, html).group(1)
    return int(result)

def parse_one_page(url):
    html = get_one_page(url)
    soup = BeautifulSoup(html, 'lxml')
    results = soup.select('#comments .commentlist li[id*="comment"]')
    for result in results:
        picture_url = {
            'image': result.select('.row .text img')[0].attrs['src']
        }
        # picture_url = item.select('.text p img')[0].attrs['src']
        if picture_url:
            save_to_mongodb(picture_url)
            # download_images(picture_url)

def save_to_mongodb(content):
    try:
        if db['sexy'].insert(content):
            print('存储到mongodb成功！', content)
    except Exception:
        print('存储到mongodb失败！', content)

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
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as file:
            file.write(content)

def main():
    base_url = 'http://jandan.net/JanDanOoxx/'
    page_num = get_page_num(base_url)
    for i in range(page_num):
        page_url = base_url + 'page-' + str(page_num-i) + '#comments'
        parse_one_page(page_url)

if __name__ == '__main__':
    main()



