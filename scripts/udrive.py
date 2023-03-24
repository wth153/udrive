import os
import numpy as np
import cv2
import time
import gradio as gr
import threading
import json
import launch

import modules.scripts as scripts
from modules import script_callbacks

from basicsr.utils.download_util import load_file_from_url

try:
    import aligo
except ImportError:
  if not launch.is_installed("aligo"):
    launch.run_pip("install aligo","aligo")
    import aligo

try:
    from baidupcs_py.baidupcs import BaiduPCSApi
except ImportError:
  if not launch.is_installed("baidupcs_py"):
    launch.run_pip("install BaiduPCS-Py","baidupcs_py")
    from baidupcs_py.baidupcs import BaiduPCSApi
  
  
  
  

class udrive:
   def __init__(self,):
     if os.path.isfile("udrive.json"):
       with open ("udrive.json","r") as f:
        datas= json.load(f)
       for a,b in datas.items():
         setattr(udrive, a, b)
     else:
       udrive.c=False
       udrive.baidu=False
       udrive.k=""
     
       
udrive=udrive()

def udrive_save(c,baidu,k):
  setattr(udrive, "c", c)
  setattr(udrive, "baidu", baidu)
  setattr(udrive, "k", k)

  udrive_dict = {}
  for attr, value in udrive.__dict__.items():
    udrive_dict[attr] = value 
  with open ("udrive.json","w") as f:
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
  global udrive
  with gr.Blocks(analytics_enabled=False) as drive:
      with gr.Column():
        with gr.Row():
          c =gr.Checkbox(label="是否输出控制台",value=udrive.c)
          baidu =gr.Checkbox(label="百度网盘",value=udrive.baidu)
        k = gr.Textbox(label="key",value=udrive.k)
        greet_btn = gr.Button("save")
        greet_btn.click(fn=udrive_save, inputs=[c,baidu,k])  

  return [(drive, "Drive", "drive")]



def upload_file(params):
    if baidu:
      api = BaiduPCSApi(bduss=drive.k)
      print("已上传至"+api.upload_file(f"/content/gdrive/MyDrive/sd/stable-diffusion-webui/{params.filename}",remotepath=f"{params.filename}")[0])


      pass
    else:  
      if udrive.c:
        lev=1
      else:
        lev=0  
      if udrive.k:
        ali = aligo.Aligo(level=lev ,refresh_token=udrive.k)
        path=params.filename
        path=os.path.split(path)
        ali.create_folder(name=path[0],check_name_mode="refuse")
        pathid=ali.get_folder_by_path(path[0]).file_id
        ali.upload_file(f"/content/gdrive/MyDrive/sd/stable-diffusion-webui/{params.filename}",parent_file_id=pathid)
        print(f"已上传{params.filename}")  
      
    
      





def on_image_saved(params):
  
  threading.Thread(target=upload_file, args=(params,)).start()

script_callbacks.on_ui_tabs(on_ui_tabs)
script_callbacks.on_image_saved(on_image_saved)
