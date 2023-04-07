import os
import numpy as np
import cv2
import time
import gradio as gr
import threading
import json
import launch
import subprocess
import requests

import modules.scripts as scripts
from modules import script_callbacks

from basicsr.utils.download_util import load_file_from_url

try:
    import aligo
except ImportError:
    if not launch.is_installed("aligo"):
        launch.run_pip("install aligo", "aligo")
        import aligo

import subprocess
import shutil

curl_command = ['curl', '-L', 'https://github.com/qjfoidnh/BaiduPCS-Go/releases/download/v3.9.1/BaiduPCS-Go-v3.9.1-linux-amd64.zip', '--output', 'BaiduPCS-Go-linux-amd64.zip']
unzip_command = ['unzip', '-o', 'BaiduPCS-Go-linux-amd64.zip']
copy_command = ['cp', './BaiduPCS-Go-v3.9.1-linux-amd64/BaiduPCS-Go', '/usr/bin']

subprocess.run(curl_command, check=True)
subprocess.run(unzip_command, check=True)
shutil.copy('./BaiduPCS-Go-v3.9.1-linux-amd64/BaiduPCS-Go', '/usr/bin')
        

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
        if self.k:    
            subprocess.run(f"BaiduPCS-Go login -bduss={self.k}", shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

udrive = udrive()


def udrive_save(c, baidu, k):
    setattr(udrive, "c", c)
    setattr(udrive, "baidu", baidu)
    setattr(udrive, "k", k)
    subprocess.run(f"BaiduPCS-Go login -bduss={k}", shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    udrive_dict = {}
    for attr, value in udrive.__dict__.items():
        udrive_dict[attr] = value

    with open("udrive.json", "w") as f:
        json.dump(udrive_dict, f)


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
            btn1.click(baiduupload, inputs=[locpath, dpath])

            code = gr.Textbox(label="Code")
            btn = gr.Button("执行代码")
            btn.click(sendcode, inputs=code)



    return [(drive, "Drive", "drive")]


def sendcode(code):
    result = subprocess.run(code, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    print(result.stdout.decode())

def baiduupload(loc,pan):
    process = subprocess.Popen(f"BaiduPCS-Go u {loc} {pan} ",shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,encoding='utf-8')

    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())

    process.communicate() 

    
    
def upload_file(params):

    if udrive.baidu:
        loc=f'/content/gdrive/MyDrive/sd/stable-diffusion-webui/{params.filename}'
        pandir=os.path.split(params.filename)[0]
        baiduupload(loc,pandir)
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
