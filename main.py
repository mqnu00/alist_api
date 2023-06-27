import json
import os
from urllib import parse
import requests
from tqdm import tqdm

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'
headers = {'User-Agent': user_agent}


# 获取链接下文件的名字
def get_list(host, path):
    url = host + "/api/fs/list"
    data = {"path": path, "password": "", "page": 1, "per_page": 0, "refresh": False}
    res = requests.post(url=url, data=data)
    with open("res.txt", "w") as f:
        json.dump(res.json(), f, indent=4, ensure_ascii=False)


# 获取这个路径的文件的下载地址
def get_download_url(host, path):
    url = host + "/api/fs/get"
    data = {
        "path": path,
        "password": ""
    }
    download_list = requests.post(url=url, data=data)
    return download_list.json()["data"]["raw_url"]


# 建立文件夹
def create_folder(path):
    if not os.path.exists(path):
        os.mkdir(path)


# 下载
def download(host, path):
    create_folder("f:/" + path.split('/')[-1])
    with open("res.txt", "r") as f:
        name_list = json.loads(f.read())
    for name in name_list["data"]["content"]:
        name = name['name']
        print(name)
        if os.path.exists('f:/' + path.split('/')[-1] + '/' + name):
            print("已存在")
            continue
        download_url = get_download_url(host, path + '/' + name)
        try :
            response = requests.get(download_url, stream=True)
        except Exception:
            print("不知道出了什么问题，也许这是一个目录")
            continue
        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024

        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)

        with open('f:/' + path.split('/')[-1] + '/' + name, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)

        progress_bar.close()


if __name__ == "__main__":
    url = ""
    parseresult = parse.urlparse(url)
    scheme = parseresult.scheme
    netloc = parseresult.netloc
    path = parse.unquote(parseresult.path)
    print(path)
    host = f"{scheme}://{netloc}"
    get_list(host, path)
    download(host, path)
