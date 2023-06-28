import json
import os
from urllib import parse
import requests
from tqdm import tqdm

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'
headers = {'User-Agent': user_agent}


# 获取链接下文件的名字
def get_list(host, path, cnt):
    url = host + "/api/fs/list"
    data = {"path": path, "password": "", "page": 1, "per_page": 0, "refresh": False}
    res = requests.post(url=url, data=data)
    with open("res" + str(cnt) + ".txt", "w", encoding='utf-8') as f:
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
def download(host, base_path, path, cnt):
    # 获取文件夹内文件列表
    get_list(host, path, cnt)
    create_folder(base_path + '/' + path.split('/')[-1])
    print(base_path + '/' + path.split('/')[-1])
    with open("res" + str(cnt) + ".txt", encoding='utf-8') as f:
        name_list = json.loads(f.read())

    # 获取下载文件的信息
    count = 1
    for info in name_list["data"]["content"]:
        name = info['name']
        name_type = info["type"]
        print(name)
        print(str(count) + '/' + str(len(name_list["data"]["content"])))
        # 下载的文件存放的路径
        filepath = base_path + '/' + path.split('/')[-1] + '/' + name
        count = count + 1
        # 文件夹判断
        if name_type == 1:
            print("这是一个文件夹")
            get_list(host, path + '/' + name, cnt + 1)
            download(host, base_path + '/' + path.split('/')[-1], path + '/' + name, cnt + 1)
            continue
        # 获取文件的下载url
        download_url = get_download_url(host, path + '/' + name)
        try:
            response = requests.get(download_url, stream=True)
        except Exception:
            print("不知道出了什么问题")
            continue
        # 获取文件大小
        total_size_in_bytes = int(response.headers.get('content-length', 0))
        # 每次下载的字长
        block_size = 1024

        # 获取以前下载的大小，断点续传
        if os.path.exists(filepath):
            first_byte = os.path.getsize(filepath)
        else:
            first_byte = 0
        if first_byte >= total_size_in_bytes:
            print("已下载完成")
            continue
        header = headers
        header['Range'] = f"bytes={first_byte}-{total_size_in_bytes}"
        response = requests.get(download_url, stream=True, headers=header)
        # 显示下载进度条
        progress_bar = tqdm(
            total=total_size_in_bytes,
            initial=first_byte,
            unit='iB',
            unit_scale=True,
            desc=filepath
        )
        # 数据下载到文件
        with open(filepath, 'wb') as file:
            for data in response.iter_content(block_size):
                if data:
                    progress_bar.update(len(data))
                    file.write(data)

        progress_bar.close()


if __name__ == "__main__":
    url = "网址"
    parseresult = parse.urlparse(url)
    scheme = parseresult.scheme
    netloc = parseresult.netloc
    path = parse.unquote(parseresult.path)
    host = f"{scheme}://{netloc}"
    base_path = "下载的文件存放的地址"
    download(host, base_path, path, 0)
