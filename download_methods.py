import os

import requests
from tqdm import tqdm
from subprocess import call

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'
headers = {'User-Agent': user_agent}


# 判断是否下载完成
def download_check(download_url, file_path, file_name):
    try:
        response = requests.get(download_url, stream=True)
    except Exception:
        print("不知道出了什么问题")
    # 获取文件大小
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    # 获取以前下载的大小
    if os.path.exists(file_path + '/' + file_name):
        first_byte = os.path.getsize(file_path + '/' + file_name)
    else:
        first_byte = 0
    if first_byte >= total_size_in_bytes:
        return True
    return False


# 基于requests库的下载方法
def requests_tqdm_download(download_url, file_path, file_name):
    try:
        response = requests.get(download_url, stream=True)
    except Exception:
        print("不知道出了什么问题")
    # 获取文件大小
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    # 每次下载的字长
    block_size = 1024

    # 获取以前下载的大小，断点续传
    if os.path.exists(file_path + '/' + file_name):
        first_byte = os.path.getsize(file_path + '/' + file_name)
    else:
        first_byte = 0
    if first_byte >= total_size_in_bytes:
        print("已下载完成")
        return
    header = headers
    header['Range'] = f"bytes={first_byte}-{total_size_in_bytes}"
    response = requests.get(download_url, stream=True, headers=header)
    # 显示下载进度条
    progress_bar = tqdm(
        total=total_size_in_bytes,
        initial=first_byte,
        unit='B',
        unit_scale=True,
        desc=file_path + '/' + file_name
    )
    # 数据下载到文件
    with open(file_path + '/' + file_name, 'ab') as file:
        for data in response.iter_content(block_size):
            if data:
                progress_bar.update(len(data))
                file.write(data)
    return


# 基于idm的下载的下载方法，需要先去下载idm软件
def idm_download(idm_path, idm_exe, download_url, file_path, file_name):
    if download_check(download_url, file_path, file_name):
        print("已下载完成")
        return
    # os.chdir(idm_path)
    # command = ' '.join([idm_exe, '/d', download_url, '/p', file_path, '/f', file_name, '/n'])
    # os.system(command)
    # 下载文件链接（注意是这个列表）
    urlList = [download_url]
    # 将下载链接全部加入到下载列表，之后再进行下载。
    for ul in urlList:
        call([idm_path + '/' + idm_exe, '/d', ul, '/p', file_path, '/f', file_name, '/n', '/a'])
    print("添加到下载列表完成")
    call([idm_path + '/' + idm_exe, '/s'])
