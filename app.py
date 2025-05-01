###############################################################################
#  Copyright (C) 2024 LiveTalking@lipku https://github.com/lipku/LiveTalking
#  email: lipku@foxmail.com
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  
#       http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################

# server.py
from flask import Flask, render_template,send_from_directory,request, jsonify
from flask_sockets import Sockets
import base64
import time
import json
#import gevent
#from gevent import pywsgi
#from geventwebsocket.handler import WebSocketHandler
import os
import re
import numpy as np
from threading import Thread,Event
#import multiprocessing
import torch.multiprocessing as mp

from aiohttp import web
import aiohttp
import aiohttp_cors
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.rtcrtpsender import RTCRtpSender
from webrtc import HumanPlayer

import argparse
import random

import shutil
import asyncio
import torch


app = Flask(__name__)
#sockets = Sockets(app)
nerfreals = {}
opt = None
model = None
avatar = None


# def llm_response(message):
#    from llm.LLM import LLM
#     # llm = LLM().init_model('Gemini', model_path= 'gemini-pro',api_key='Your API Key', proxy_url=None)
#     # llm = LLM().init_model('ChatGPT', model_path= 'gpt-3.5-turbo',api_key='Your API Key')
#    llm = LLM().init_model('VllmGPT', model_path= 'THUDM/chatglm3-6b')
#     response = llm.chat(message)
#     print(response)
#     return response

# def llm_response(message, nerfreal):
#     # 记录开始时间
#     start = time.perf_counter()
    
#     # 使用LLM类初始化VllmGPT模型
#     from llm.LLM import LLM
#     llm = LLM().init_model('VllmGPT', model_path='THUDM/chatglm3-6b')
    
#     end = time.perf_counter()
#     print(f"llm Time init: {end-start}s")
    
#     # 设置系统提示
#     system_prompt = '你的名字叫春儿,英文名Chuner,你的爸爸叫张静,今年2025年。你18岁，你来自南宋奉贤，你是从2024年穿越到奉贤张静家。你擅长弹古筝和琵琶，擅长舞剑。喜欢古典文学。每次回答问题你都要喊一声爸爸。'
    
#     # 使用流式生成进行聊天
#     result = ""
#     first = True
    
#     # 假设LLM类支持流式输出，如果不支持需要修改此部分
#     for chunk in llm.stream_chat(message, system_prompt=system_prompt):
#         if first:
#             end = time.perf_counter()
#             print(f"llm Time to first chunk: {end-start}s")
#             first = False
        
#         # 处理当前生成的文本片段
#         msg = chunk
#         lastpos = 0
        
#         for i, char in enumerate(msg):
#             if char in ",.!;:，。！？：；":
#                 result = result + msg[lastpos:i+1]
#                 lastpos = i+1
#                 if len(result) > 10:
#                     print(result)
#                     nerfreal.put_msg_txt(result)
#                     result = ""
        
#         result = result + msg[lastpos:]
    
#     # 记录结束时间
#     end = time.perf_counter()
#     print(f"llm Time to last chunk: {end-start}s")
#     nerfreal.put_msg_txt(result)



#==========================================


def llm_response(message,nerfreal):
    # 记录开始时间
    start = time.perf_counter()
    from openai import OpenAI
    client = OpenAI(
        # 如果您没有配置环境变量，请在此处用您的API Key进行替换
        # api_key=os.getenv("DASHSCOPE_API_KEY"),
        api_key="sk-8888888888888888834552353453452888888",
        # 填写DashScope SDK的base_url
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    end = time.perf_counter()
    print(f"llm Time init: {end-start}s")

    # 创建聊天完成请求
    completion = client.chat.completions.create(
        model="qwen3-235b-a22b",
        messages=[{'role': 'system', 'content': '你的名字叫春儿,英文名Chuner,你的爸爸叫张静,今年2025年。你18岁，你来自南宋奉贤，你是从2024年穿越到奉贤张静家。你擅长弹古筝和琵琶，擅长舞剑。喜欢古典文学。每次回答问题你都要喊一声爸爸。'},
                  {'role': 'user', 'content': message}],
        extra_body={"enable_search": True,"enable_thinking": False},        
        stream=True,
        # 通过以下设置，在流式输出的最后一行展示token使用信息
        stream_options={"include_usage": True}
    )

    # # 创建聊天完成请求
    # completion = client.chat.completions.create(
    #     model="qwen-plus",
    #     messages=[{'role': 'system', 'content': '你的名字叫春儿,英文名Chuner,你的爸爸叫张静,今年2025年。你18岁，你来自南宋奉贤，你是从2024年穿越到奉贤张静家。你擅长弹古筝和琵琶，擅长舞剑。喜欢古典文学。每次回答问题你都要喊一声爸爸。'},
    #               {'role': 'user', 'content': message}],
    #     extra_body={"enable_search": True},          
    #     stream=True,
    #     # 通过以下设置，在流式输出的最后一行展示token使用信息
    #     stream_options={"include_usage": True}
    # )


    # 处理流式响应
    result=""
    first = True
    for chunk in completion:
        if len(chunk.choices)>0:
            #print(chunk.choices[0].delta.content)
            if first:
                end = time.perf_counter()
                print(f"llm Time to first chunk: {end-start}s")
                first = False
            msg = chunk.choices[0].delta.content
            lastpos=0
            #msglist = re.split('[,.!;:，。！?]',msg)
            for i, char in enumerate(msg):
                if char in ",.!;:，。！？：；" :
                    result = result+msg[lastpos:i+1]
                    lastpos = i+1
                    if len(result)>10:
                        print(result)
                        nerfreal.put_msg_txt(result)
                        result=""
            result = result+msg[lastpos:]
    
    # 记录结束时间
    end = time.perf_counter()
    print(f"llm Time to last chunk: {end-start}s")
    nerfreal.put_msg_txt(result)
#####webrtc###############################
pcs = set()

def randN(N):
    '''生成长度为 N的随机数 '''
    min = pow(10, N - 1)
    max = pow(10, N)
    return random.randint(min, max - 1)

def build_nerfreal(sessionid):
    opt.sessionid=sessionid

    from lipreal import LipReal
    nerfreal = LipReal(opt,model,avatar)
    
    if opt.enable_static_video and opt.static_video:
        nerfreal.load_static_video(opt.static_video)

    return nerfreal

#@app.route('/offer', methods=['POST'])
async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    if len(nerfreals) >= opt.max_session:
        print('reach max session')
        return -1
    sessionid = randN(6) #len(nerfreals)
    print('sessionid=',sessionid)
    nerfreals[sessionid] = None
    nerfreal = await asyncio.get_event_loop().run_in_executor(None, build_nerfreal,sessionid)
    nerfreals[sessionid] = nerfreal
    
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)
            del nerfreals[sessionid]
        if pc.connectionState == "closed":
            pcs.discard(pc)
            del nerfreals[sessionid]

    player = HumanPlayer(nerfreals[sessionid])
    audio_sender = pc.addTrack(player.audio)
    video_sender = pc.addTrack(player.video)
    capabilities = RTCRtpSender.getCapabilities("video")
    preferences = list(filter(lambda x: x.name == "H264", capabilities.codecs))
    preferences += list(filter(lambda x: x.name == "VP8", capabilities.codecs))
    preferences += list(filter(lambda x: x.name == "rtx", capabilities.codecs))
    transceiver = pc.getTransceivers()[1]
    transceiver.setCodecPreferences(preferences)

    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    #return jsonify({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type, "sessionid":sessionid}
        ),
    )

async def human(request):
    params = await request.json()

    sessionid = params.get('sessionid',0)
    if params.get('interrupt'):
        nerfreals[sessionid].flush_talk()

    if params['type']=='echo':
        nerfreals[sessionid].put_msg_txt(params['text'])
    elif params['type']=='chat':
        res=await asyncio.get_event_loop().run_in_executor(None, llm_response, params['text'],nerfreals[sessionid])                         
        #nerfreals[sessionid].put_msg_txt(res)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"code": 0, "data":"ok"}
        ),
    )

async def humanaudio(request):
    try:
        form= await request.post()
        sessionid = int(form.get('sessionid',0))
        fileobj = form["file"]
        filename=fileobj.filename
        filebytes=fileobj.file.read()
        nerfreals[sessionid].put_audio_file(filebytes)

        return web.Response(
            content_type="application/json",
            text=json.dumps(
                {"code": 0, "msg":"ok"}
            ),
        )
    except Exception as e:
        return web.Response(
            content_type="application/json",
            text=json.dumps(
                {"code": -1, "msg":"err","data": ""+e.args[0]+""}
            ),
        )

async def set_audiotype(request):
    params = await request.json()

    sessionid = params.get('sessionid',0)    
    nerfreals[sessionid].set_curr_state(params['audiotype'],params['reinit'])

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"code": 0, "data":"ok"}
        ),
    )

async def record(request):
    params = await request.json()

    sessionid = params.get('sessionid',0)
    if params['type']=='start_record':
        # nerfreals[sessionid].put_msg_txt(params['text'])
        nerfreals[sessionid].start_recording()
    elif params['type']=='end_record':
        nerfreals[sessionid].stop_recording()
    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"code": 0, "data":"ok"}
        ),
    )

async def is_speaking(request):
    params = await request.json()

    sessionid = params.get('sessionid',0)
    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"code": 0, "data": nerfreals[sessionid].is_speaking()}
        ),
    )

async def set_static_video(request):
    params = await request.json()
    
    sessionid = params.get('sessionid',0)
    if params.get('enable', False):
        if params.get('video_path', ''):
            nerfreals[sessionid].load_static_video(params['video_path'])
            return web.Response(
                content_type="application/json",
                text=json.dumps(
                    {"code": 0, "data": "静态视频已加载"}
                ),
            )
        else:
            return web.Response(
                content_type="application/json",
                text=json.dumps(
                    {"code": -1, "data": "未提供视频路径"}
                ),
            )
    else:
        nerfreals[sessionid].static_video_enabled = False
        return web.Response(
            content_type="application/json",
            text=json.dumps(
                {"code": 0, "data": "静态视频已禁用"}
            ),
        )


async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

async def post(url,data):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url,data=data) as response:
                return await response.text()
    except aiohttp.ClientError as e:
        print(f'Error: {e}')

async def run(push_url,sessionid):
    nerfreal = await asyncio.get_event_loop().run_in_executor(None, build_nerfreal,sessionid)
    nerfreals[sessionid] = nerfreal

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    player = HumanPlayer(nerfreals[sessionid])
    audio_sender = pc.addTrack(player.audio)
    video_sender = pc.addTrack(player.video)

    await pc.setLocalDescription(await pc.createOffer())
    answer = await post(push_url,pc.localDescription.sdp)
    await pc.setRemoteDescription(RTCSessionDescription(sdp=answer,type='answer'))
##########################################
# os.environ['MKL_SERVICE_FORCE_INTEL'] = '1'
# os.environ['MULTIPROCESSING_METHOD'] = 'forkserver'                                                    
if __name__ == '__main__':
    mp.set_start_method('spawn')
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=0)


    ### GUI options
    parser.add_argument('--gui', action='store_true', help="start a GUI")
    parser.add_argument('--W', type=int, default=450, help="GUI width")
    parser.add_argument('--H', type=int, default=450, help="GUI height")
    parser.add_argument('--radius', type=float, default=3.35, help="default GUI camera radius from center")
    parser.add_argument('--fovy', type=float, default=21.24, help="default GUI camera fovy")
    parser.add_argument('--max_spp', type=int, default=1, help="GUI rendering max sample per pixel")


    # asr
    parser.add_argument('--asr', action='store_true', help="load asr for real-time app")
    parser.add_argument('--asr_wav', type=str, default='', help="load the wav and use as input")
    parser.add_argument('--asr_play', action='store_true', help="play out the audio")

    #parser.add_argument('--asr_model', type=str, default='deepspeech')
    parser.add_argument('--asr_model', type=str, default='cpierse/wav2vec2-large-xlsr-53-esperanto') #
    # parser.add_argument('--asr_model', type=str, default='facebook/wav2vec2-large-960h-lv60-self')
    # parser.add_argument('--asr_model', type=str, default='facebook/hubert-large-ls960-ft')

    parser.add_argument('--asr_save_feats', action='store_true')
    # audio FPS
    parser.add_argument('--fps', type=int, default=50)
    # sliding window left-middle-right length (unit: 20ms)
    parser.add_argument('-l', type=int, default=10)
    parser.add_argument('-m', type=int, default=8)
    parser.add_argument('-r', type=int, default=10)

    #musetalk opt
    parser.add_argument('--avatar_id', type=str, default='avator_1')
    parser.add_argument('--bbox_shift', type=int, default=5)
    parser.add_argument('--batch_size', type=int, default=16)

    # parser.add_argument('--customvideo', action='store_true', help="custom video")
    # parser.add_argument('--customvideo_img', type=str, default='data/customvideo/img')
    # parser.add_argument('--customvideo_imgnum', type=int, default=1)

    parser.add_argument('--customvideo_config', type=str, default='')
    
    parser.add_argument('--static_video', type=str, default='', help="静态视频路径，可以是视频文件或图片序列文件夹")
    parser.add_argument('--enable_static_video', action='store_true', help="启用静态视频播放")

    parser.add_argument('--tts', type=str, default='edgetts') #xtts gpt-sovits cosyvoice
    parser.add_argument('--REF_FILE', type=str, default=None)
    parser.add_argument('--REF_TEXT', type=str, default=None)
    parser.add_argument('--TTS_SERVER', type=str, default='http://127.0.0.1:9880') # http://localhost:9000
    # parser.add_argument('--CHARACTER', type=str, default='test')
    # parser.add_argument('--EMOTION', type=str, default='default')

    parser.add_argument('--model', type=str, default='wav2lip') #musetalk wav2lip

    parser.add_argument('--transport', type=str, default='webrtc') #rtmp webrtc rtcpush
    parser.add_argument('--push_url', type=str, default='http://localhost:1985/rtc/v1/whip/?app=live&stream=livestream') #rtmp://localhost/live/livestream

    parser.add_argument('--max_session', type=int, default=1)  #multi session count
    parser.add_argument('--listenport', type=int, default=8010)

    opt = parser.parse_args()
    #app.config.from_object(opt)
    #print(app.config)
    opt.customopt = []
    if opt.customvideo_config!='':
        with open(opt.customvideo_config,'r') as file:
            opt.customopt = json.load(file)



    from lipreal import LipReal,load_model,load_avatar,warm_up
    print(opt)
    model = load_model("./models/wav2lip.pth")
    avatar = load_avatar(opt.avatar_id)
    warm_up(opt.batch_size,model,384)
    # for k in range(opt.max_session):
    #     opt.sessionid=k
    #     nerfreal = LipReal(opt,model)
    #     nerfreals.append(nerfreal)


    if opt.transport=='rtmp':
        thread_quit = Event()
        nerfreals[0] = build_nerfreal(0)
        rendthrd = Thread(target=nerfreals[0].render,args=(thread_quit,))
        rendthrd.start()

    #############################################################################
    appasync = web.Application()
    appasync.on_shutdown.append(on_shutdown)
    appasync.router.add_post("/offer", offer)
    appasync.router.add_post("/human", human)
    appasync.router.add_post("/humanaudio", humanaudio)
    appasync.router.add_post("/set_audiotype", set_audiotype)
    appasync.router.add_post("/record", record)
    appasync.router.add_post("/is_speaking", is_speaking)
    appasync.router.add_post("/set_static_video", set_static_video)
    appasync.router.add_static('/',path='web')

    # Configure default CORS settings.
    cors = aiohttp_cors.setup(appasync, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        })
    # Configure CORS on all routes.
    for route in list(appasync.router.routes()):
        cors.add(route)

    pagename='page-asr-new.html'
    if opt.transport=='rtmp':
        pagename='echoapi.html'
    elif opt.transport=='rtcpush':
        pagename='rtcpushapi.html'
    print('start http server; http://<serverip>:'+str(opt.listenport)+'/'+pagename)
    def run_server(runner):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner, '0.0.0.0', opt.listenport)
        loop.run_until_complete(site.start())
        if opt.transport=='rtcpush':
            for k in range(opt.max_session):
                push_url = opt.push_url
                if k!=0:
                    push_url = opt.push_url+str(k)
                loop.run_until_complete(run(push_url,k))
        loop.run_forever()    
    #Thread(target=run_server, args=(web.AppRunner(appasync),)).start()
    run_server(web.AppRunner(appasync))

    #app.on_shutdown.append(on_shutdown)
    #app.router.add_post("/offer", offer)

    # print('start websocket server')
    # server = pywsgi.WSGIServer(('0.0.0.0', 8000), app, handler_class=WebSocketHandler)
    # server.serve_forever()
    
    
