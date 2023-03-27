import os
import numpy as np
import cv2
import time
import gradio as gr
import threading
import json
import launch
import subprocess

import modules.scripts as scripts
from modules import script_callbacks

from basicsr.utils.download_util import load_file_from_url

try:
    import aligo
except ImportError:
    if not launch.is_installed("aligo"):
        launch.run_pip("install aligo", "aligo")
        import aligo


# try:
#     from baidupcs_py.baidupcs import BaiduPCSApi
# except ImportError:
#     if not launch.is_installed("baidupcs_py"):
#         subprocess.run("pip install requests-toolbelt aget passlib", shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
#         launch.run_pip("install BaiduPCS-Py --no-deps", "baidupcs_py --no-deps")
#         #launch.run_pip("requests_toolbelt")
#         from baidupcs_py.baidupcs import BaiduPCSApi

# subprocess.run("curl -o /usr/local/lib/python3.9/dist-packages/uvicorn/loops/auto.py  https://raw.githubusercontent.com/encode/uvicorn/master/uvicorn/loops/auto.py", shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
# subprocess.run("curl -o /usr/local/lib/python3.9/dist-packages/uvicorn/loops/uvloop.py  https://raw.githubusercontent.com/encode/uvicorn/master/uvicorn/loops/uvloop.py", shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

class udrive:
    def __init__(self, ):
        # self.datas = {}
        # self.lock = []
        # self.locv = []
        # self.drive={}

        if os.path.isfile("udrive.json"):
            with open("udrive.json", "r") as f:
                datas = json.load(f)
            for a, b in datas.items():
                setattr(udrive, a, b)

        else:
            self.c = False
            self.k = ""
            self.baidu = False
            # self.code=[]
            # self.locpath=[]
            # self.dpath=[]


udrive = udrive()


def udrive_save(c, baidu, k):
    setattr(udrive, "c", c)
    setattr(udrive, "baidu", baidu)
    setattr(udrive, "k", k)

    udrive_dict = {}
    for attr, value in udrive.__dict__.items():
        udrive_dict[attr] = value

    with open("udrive.json", "w") as f:
        json.dump(udrive_dict, f)

    # for k,v in udrive.drive.blocks.items():
    #    if isinstance(v, gr.Checkbox) or isinstance(v, gr.Textbox):
    #         udrive.locv.append(v.value)
    # udrive_dict = dict(zip(udrive.lock, udrive.locv))
    # for k, v in udrive_dict.items():
    #     setattr(udrive, k, v)


class Script(scripts.Script):
    def __init__(self) -> None:
        super().__init__()

    def title(self):
        return "Drive"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        return ()


def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as drive:
        with gr.Column():
            with gr.Row():
                c = gr.Checkbox(label="是否输出控制台", value=udrive.c)
                baidu = gr.Checkbox(label="百度网盘", value=udrive.baidu)
            k = gr.Textbox(label="key", value=udrive.k)
            greet_btn = gr.Button("save")
            greet_btn.click(udrive_save, inputs=[c, baidu, k])

            with gr.Row():
                locpath = gr.Textbox(label="本地目录")
                dpath = gr.Textbox(label="网盘目录(加上文件名)")
            btn1 = gr.Button("上传")
            btn1.click(upload, inputs=[locpath, dpath])

            code = gr.Textbox(label="Code")
            btn = gr.Button("执行代码")
            btn.click(sendcode, inputs=code)

            # if os.path.isfile("udrive.json"):
            #     with open("udrive.json", "r") as f:
            #         datas = json.load(f)
            #     for k, v in datas.items():
            #         if v == "" or v == None:
            #             pass
            #         else:
            #             exec(f"{k}.value={v}")

            # for k,v in locals().items():
            #    if isinstance(v, gr.Checkbox) or isinstance(v, gr.Textbox):
            #       udrive.lock.append(k)

    return [(drive, "Drive", "drive")]


def upload(locpath, dpath):
    #api = BaiduPCSApi(bduss=udrive.k)
    url = f'https://pan.baidu.com/rest/2.0/xpan/file?method=upload&path={dpath}'
    params = {
        "async": 2,
        "onnest": "fail",
        "opera": "rename",
        "bdstoken": "2c404dab0010e59dbbd64aa7a6f9f9ad",
        "clienttype": 0,
        "app_id": 250528,
        "web": 1
    }

    files = {'file': open(locpath, 'rb')}
    response = requests.post(url, headers=headers, params=params, cookies={"BDUSS":udrive.k}, files=files)
    result = response.json()
    print(f"已上传{params.filename}")


    try:
        #print("已上传至" + api.upload_file(locpath, remotepath=dpath)[0])
        result = response.json()
        print(f"已上传{params.filename}")
    except:
        print("未成功,请检查输入")


def sendcode(code):
    result = subprocess.run(code, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    print(result.stdout.decode())


def upload_file(params):
    if udrive.baidu:
        #         api = BaiduPCSApi(bduss=udrive.k)
        #         print("已上传至" + api.upload_file(f"/content/gdrive/MyDrive/sd/stable-diffusion-webui/{params.filename}",remotepath=f"{params.filename}")[0])
        url = f'https://pan.baidu.com/rest/2.0/xpan/file?method=upload&path={params.filename}'
        params = {
        "async": 2,
        "onnest": "fail",
        "opera": "rename",
        "bdstoken": "2c404dab0010e59dbbd64aa7a6f9f9ad",
        "clienttype": 0,
        "app_id": 250528,
        "web": 1
    }

        files = {'file': open(f"/content/gdrive/MyDrive/sd/stable-diffusion-webui/{params.filename}", 'rb')}
        response = requests.post(url, headers=headers, params=params, cookies={"BDUSS":udrive.k}, files=files)
        result = response.json()
        print(f"已上传{params.filename}")

    else:
        if udrive.c:
            lev = 1
    else:
        lev = 0
    if udrive.k:
        ali = aligo.Aligo(level=lev, refresh_token=udrive.k)
        path = params.filename
        path = os.path.split(path)
        ali.create_folder(name=path[0], check_name_mode="refuse")
        pathid = ali.get_folder_by_path(path[0]).file_id
        ali.upload_file(f"/content/gdrive/MyDrive/sd/stable-diffusion-webui/{params.filename}",
                        parent_file_id=pathid)
        print(f"已上传{params.filename}")


def on_image_saved(params):
    threading.Thread(target=upload_file, args=(params,)).start()


script_callbacks.on_ui_tabs(on_ui_tabs)
script_callbacks.on_image_saved(on_image_saved)
