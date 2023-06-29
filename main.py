import json
import os
from urllib import parse
import requests
from download_methods import requests_tqdm_download, idm_download

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'
headers = {'User-Agent': user_agent}
# idm软件的路径
idm_path = 'D:/tools/IDM'
idm_exe = 'IDMan.exe'


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
def download(host, host_d, base_path, path, cnt):
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
        file_path = base_path + '/' + path.split('/')[-1]
        count = count + 1
        # 文件夹判断
        if name_type == 1:
            print("这是一个文件夹")
            get_list(host, path + '/' + name, cnt + 1)
            download(host, host_d, base_path + '/' + path.split('/')[-1], path + '/' + name, cnt + 1)
            continue
        # 获取文件的下载url
        # download_url = get_download_url(host, path + '/' + name)
        download_url = host_d + parse.quote(path + '/' + name + f'?sign={info["sign"]}')
        # with open("res.txt", 'a', encoding='utf-8') as f:
        #     f.write(download_url + '\n')
        # 下载方法
        # requests_tqdm_download(download_url, file_path, name)
        idm_download(idm_path, idm_exe, download_url, file_path, name)


if __name__ == "__main__":
    # 下载的网址
    url = ""
    parseresult = parse.urlparse(url)
    scheme = parseresult.scheme
    netloc = parseresult.netloc
    path = parse.unquote(parseresult.path)
    host = f"{scheme}://{netloc}"
    host_d = f"{scheme}://{netloc}/d"
    # 下载的文件保存的地址
    base_path = ""
    download(host, host_d, base_path, path, 0)
