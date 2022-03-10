# coding=utf-8

import sys
import json
import base64
import time
import re
import os
from nltk.translate.bleu_score import sentence_bleu

import Levenshtein
IS_PY3 = sys.version_info.major == 3

if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode
    timer = time.perf_counter
else:
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import URLError
    from urllib import urlencode
    if sys.platform == "win32":
        timer = time.clock
    else:
        # On most other platforms the best timer is time.time()
        timer = time.time

API_KEY = 'L0h7r7y8GRhOyXMKAC0wXT24'
SECRET_KEY = 'k5DU2cslzVryQgLr4zuxgEqh1N4nQGLO'



CUID = '123456PYTHON'
# 采样率
RATE = 16000  # 固定值

# 普通版

DEV_PID = 1537  # 1537 表示识别普通话，使用输入法模型。根据文档填写PID，选择语言及识别模型
ASR_URL = 'http://vop.baidu.com/server_api'
SCOPE = 'audio_voice_assistant_get'  # 有此scope表示有asr能力，没有请在网页里勾选，非常旧的应用可能没有

#测试自训练平台需要打开以下信息， 自训练平台模型上线后，您会看见 第二步：“”获取专属模型参数pid:8001，modelid:1234”，按照这个信息获取 dev_pid=8001，lm_id=1234
# DEV_PID = 8001 ;   
# LM_ID = 1234 ;

# 极速版 打开注释的话请填写自己申请的appkey appSecret ，并在网页中开通极速版（开通后可能会收费）

# DEV_PID = 80001
# ASR_URL = 'http://vop.baidu.com/pro_api'
# SCOPE = 'brain_enhanced_asr'  # 有此scope表示有极速版能力，没有请在网页里开通极速版

# 忽略scope检查，非常旧的应用可能没有
# SCOPE = False

class DemoError(Exception):
    pass


"""  TOKEN start """

TOKEN_URL = 'http://aip.baidubce.com/oauth/2.0/token'


def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    if (IS_PY3):
        post_data = post_data.encode( 'utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req)
        result_str = f.read()
    except URLError as err:
        print('token http response http code : ' + str(err.code))
        result_str = err.read()
    if (IS_PY3):
        result_str =  result_str.decode()

    print(result_str)
    result = json.loads(result_str)
    print(result)
    if ('access_token' in result.keys() and 'scope' in result.keys()):
        print(SCOPE)
        if SCOPE and (not SCOPE in result['scope'].split(' ')):  # SCOPE = False 忽略检查
            raise DemoError('scope is not correct')
        print('SUCCESS WITH TOKEN: %s  EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
        return result['access_token']
    else:
        raise DemoError('MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')

"""  TOKEN end """

if __name__ == '__main__':
    n_10 = 0
    n_5 = 0
    bleu1_10 = []
    bleu2_10 = []
    bleu3_10 = []
    bleu4_10 = []
    corr_10 = []
    bleu1_5 = []
    bleu2_5 = []
    bleu3_5 = []
    bleu4_5 = []
    corr_5 = []
    sum1_10=sum2_10=sum3_10=sum4_10=sumcorr_10=0
    sum1_5=sum2_5=sum3_5=sum4_5=sumcorr_5=0
    for cleanwav in os.listdir("G:/语音测试程序/voice_data/chinese/THCHS-30/sam_clean"):
        # 需要识别的文件
          # 只支持 pcm/wav/amr 格式，极速版额外支持m4a 格式
        #print(AUDIO_FILE)
        AUDIO_FILE = "G:/语音测试程序/voice_data/chinese/THCHS-30/sam_clean/" + cleanwav
        FORMAT = AUDIO_FILE[-3:]  # 文件后缀只支持 pcm/wav/amr 格式，极速版额外支持m4a 格式
    
    
        token = fetch_token()

        speech_data = []
        with open(AUDIO_FILE, 'rb') as speech_file:
            speech_data = speech_file.read()

        length = len(speech_data)
        if length == 0:
            raise DemoError('file %s length read 0 bytes' % AUDIO_FILE)
        speech = base64.b64encode(speech_data)
        if (IS_PY3):
            speech = str(speech, 'utf-8')#
        params = {'dev_pid': DEV_PID,
             #"lm_id" : LM_ID,    #测试自训练平台开启此项
              'format': FORMAT,
              'rate': RATE,
              'token': token,
              'cuid': CUID,
              'channel': 1,
              'speech': speech,
              'len': length
              }
        post_data = json.dumps(params, sort_keys=False)
    # print post_data
        req = Request(ASR_URL, post_data.encode('utf-8'))
        req.add_header('Content-Type', 'application/json')
        try:
            begin = timer()
            f = urlopen(req)
            result_str = f.read()
            print ("Request time cost %f" % (timer() - begin))
        except URLError as err:
            print('asr http response http code : ' + str(err.code))
            result_str = err.read()

        if (IS_PY3):
            result_str = str(result_str, 'utf-8')
        print(result_str)
        a = re.findall(r'[\u4e00-\u9fa5]', result_str)
        
        
        AUDIO_FILE = "G:/语音测试程序/voice_data/chinese/THCHS-30/noisy100_0/add_machinegun/" + cleanwav[:-4] + "_machinegun_snr0.wav"
        FORMAT = AUDIO_FILE[-3:]  # 文件后缀只支持 pcm/wav/amr 格式，极速版额外支持m4a 格式
    
    
        token = fetch_token()

        speech_data = []
        with open(AUDIO_FILE, 'rb') as speech_file:
            speech_data = speech_file.read()

        length = len(speech_data)
        if length == 0:
            raise DemoError('file %s length read 0 bytes' % AUDIO_FILE)
        speech = base64.b64encode(speech_data) 
        if (IS_PY3):
            speech = str(speech, 'utf-8')#
        params = {'dev_pid': DEV_PID,
             #"lm_id" : LM_ID,    #测试自训练平台开启此项
              'format': FORMAT,
              'rate': RATE,
              'token': token,
              'cuid': CUID,
              'channel': 1,
              'speech': speech,
              'len': length
              }
        post_data = json.dumps(params, sort_keys=False)
    # print post_data
        req = Request(ASR_URL, post_data.encode('utf-8'))
        req.add_header('Content-Type', 'application/json')
        try:
            begin = timer()
            f = urlopen(req)
            result_str = f.read()
            print ("Request time cost %f" % (timer() - begin))
        except URLError as err:
            print('asr http response http code : ' + str(err.code))
            result_str = err.read()

        if (IS_PY3):
            result_str = str(result_str, 'utf-8')
        print(result_str)
        b = re.findall(r'[\u4e00-\u9fa5]', result_str)
        
        
        if a == b:
            n_10 += 1
        #if a == c:
            #n_5 += 1
        score1_10 = sentence_bleu([a], b, weights=(1, 0, 0, 0))
        score2_10 = sentence_bleu([a], b, weights=(0.5, 0.5, 0, 0))
        score3_10 = sentence_bleu([a], b, weights=(0.33, 0.33, 0.33, 0))
        score4_10 = sentence_bleu([a], b, weights=(0.25, 0.25, 0.25, 0.25))
        bleu1_10.append(score1_10)
        bleu2_10.append(score2_10)
        bleu3_10.append(score3_10)
        bleu4_10.append(score4_10)
        a = ''.join(a)
        b = ''.join(b)
        
        with open('machinegun0.txt','a') as f0:
            print(a,file=f0)
        with open('machinegun0.txt','a') as f0:
            print(b,file=f0)
        if len(a)!=0:
            wer_10=Levenshtein.distance(a, b)/len(a)
            corr_10.append(1-wer_10)
        
    for i in range(len(bleu1_10)):
        sum1_10 += bleu1_10[i]
        sum2_10 += bleu2_10[i]
        sum3_10 += bleu3_10[i]
        sum4_10 += bleu4_10[i]
        #sum1_5 += bleu1_5[i]
        #sum2_5 += bleu2_5[i]
        #sum3_5 += bleu3_5[i]
        #sum4_5 += bleu4_5[i]
        
        #sumcorr_5 += corr_5[i]
    for i in range(len(corr_10)):
        sumcorr_10 += corr_10[i]
    bleu1_ave_10 = sum1_10/100
    bleu2_ave_10 = sum2_10/100
    bleu3_ave_10 = sum3_10/100
    bleu4_ave_10 = sum4_10/100

    #bleu1_ave_5 = sum1_5/100
    #bleu2_ave_5 = sum2_5/100
    #bleu3_ave_5 = sum3_5/100
    #bleu4_ave_5 = sum4_5/100
    corr_ave_10 = sumcorr_10/len(corr_10)
    #corr_ave_5 = sumcorr_5/100
    with open('machinegun0.txt','a') as f0:
        print(n_10,bleu1_ave_10,bleu2_ave_10,bleu3_ave_10,bleu4_ave_10,corr_ave_10,file=f0)
        
        
        
        

