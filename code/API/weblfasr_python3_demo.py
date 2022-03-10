# -*- coding: utf-8 -*-
# 
#   author: yanmeng2
# 
# 非实时转写调用demo

import base64
import hashlib
import hmac
import json
import os
import time
import re
import requests
from nltk.translate.bleu_score import sentence_bleu

import Levenshtein
lfasr_host = 'http://raasr.xfyun.cn/api'

# 请求的接口名
api_prepare = '/prepare'
api_upload = '/upload'
api_merge = '/merge'
api_get_progress = '/getProgress'
api_get_result = '/getResult'
# 文件分片大小10M
file_piece_sice = 10485760

# ——————————————————转写可配置参数————————————————
# 参数可在官网界面（https://doc.xfyun.cn/rest_api/%E8%AF%AD%E9%9F%B3%E8%BD%AC%E5%86%99.html）查看，根据需求可自行在gene_params方法里添加修改
# 转写类型
lfasr_type = 0
# 是否开启分词
has_participle = 'false'
has_seperate = 'true'
# 多候选词个数
max_alternatives = 0
# 子用户标识
suid = ''


class SliceIdGenerator:
    """slice id生成器"""

    def __init__(self):
        self.__ch = 'aaaaaaaaa`'

    def getNextSliceId(self):
        ch = self.__ch
        j = len(ch) - 1
        while j >= 0:
            cj = ch[j]
            if cj != 'z':
                ch = ch[:j] + chr(ord(cj) + 1) + ch[j + 1:]
                break
            else:
                ch = ch[:j] + 'a' + ch[j + 1:]
                j = j - 1
        self.__ch = ch
        return self.__ch


class RequestApi(object):
    def __init__(self, appid, secret_key, upload_file_path):
        self.appid = appid
        self.secret_key = secret_key
        self.upload_file_path = upload_file_path

    # 根据不同的apiname生成不同的参数,本示例中未使用全部参数您可在官网(https://doc.xfyun.cn/rest_api/%E8%AF%AD%E9%9F%B3%E8%BD%AC%E5%86%99.html)查看后选择适合业务场景的进行更换
    def gene_params(self, apiname, taskid=None, slice_id=None):
        appid = self.appid
        secret_key = self.secret_key
        upload_file_path = self.upload_file_path
        ts = str(int(time.time()))
        m2 = hashlib.md5()
        m2.update((appid + ts).encode('utf-8'))
        md5 = m2.hexdigest()
        md5 = bytes(md5, encoding='utf-8')
        # 以secret_key为key, 上面的md5为msg， 使用hashlib.sha1加密结果为signa
        signa = hmac.new(secret_key.encode('utf-8'), md5, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        file_len = os.path.getsize(upload_file_path)
        file_name = os.path.basename(upload_file_path)
        param_dict = {}

        if apiname == api_prepare:
            # slice_num是指分片数量，如果您使用的音频都是较短音频也可以不分片，直接将slice_num指定为1即可
            slice_num = int(file_len / file_piece_sice) + (0 if (file_len % file_piece_sice == 0) else 1)
            param_dict['app_id'] = appid
            param_dict['signa'] = signa
            param_dict['ts'] = ts
            param_dict['file_len'] = str(file_len)
            param_dict['file_name'] = file_name
            param_dict['slice_num'] = str(slice_num)
        elif apiname == api_upload:
            param_dict['app_id'] = appid
            param_dict['signa'] = signa
            param_dict['ts'] = ts
            param_dict['task_id'] = taskid
            param_dict['slice_id'] = slice_id
        elif apiname == api_merge:
            param_dict['app_id'] = appid
            param_dict['signa'] = signa
            param_dict['ts'] = ts
            param_dict['task_id'] = taskid
            param_dict['file_name'] = file_name
        elif apiname == api_get_progress or apiname == api_get_result:
            param_dict['app_id'] = appid
            param_dict['signa'] = signa
            param_dict['ts'] = ts
            param_dict['task_id'] = taskid
        return param_dict

    # 请求和结果解析，结果中各个字段的含义可参考：https://doc.xfyun.cn/rest_api/%E8%AF%AD%E9%9F%B3%E8%BD%AC%E5%86%99.html
    def gene_request(self, apiname, data, files=None, headers=None):
        response = requests.post(lfasr_host + apiname, data=data, files=files, headers=headers)
        result = json.loads(response.text)
        if result["ok"] == 0:
            print("{} success:".format(apiname) + str(result))
            if "{} success:".format(apiname) == "/getResult success:":
                '''
                result_one=result["data"]
                result_one = result_one.encode('utf-8').decode('utf-8')
                
                #print(len(result_one))

                for i in range(len(result_one)):
                    #print(result_one[i-1])
                    if result_one[i-1] == 't':
                        n = i
                        #result_one = result_one[i:]
                result_one = result_one[n+2:]
                '''
                
                result_one=result["data"]
                result_one = re.findall(r'[\u4e00-\u9fa5]', result_one)
                
                
                return result_one
            #if "{} success:" == "/getResult success:":
                #print("{} success:".format(apiname)["onebest"])
            return result
        else:
            #print("{} error:".format(apiname) + str(result))
            exit(0)
            return result

    # 预处理
    def prepare_request(self):
        return self.gene_request(apiname=api_prepare,
                                 data=self.gene_params(api_prepare))

    # 上传
    def upload_request(self, taskid, upload_file_path):
        file_object = open(upload_file_path, 'rb')
        try:
            index = 1
            sig = SliceIdGenerator()
            while True:
                content = file_object.read(file_piece_sice)
                if not content or len(content) == 0:
                    break
                files = {
                    "filename": self.gene_params(api_upload).get("slice_id"),
                    "content": content
                }
                response = self.gene_request(api_upload,
                                             data=self.gene_params(api_upload, taskid=taskid,
                                                                   slice_id=sig.getNextSliceId()),
                                             files=files)
                if response.get('ok') != 0:
                    # 上传分片失败
                    #print('upload slice fail, response: ' + str(response))
                    return False
                #print('upload slice ' + str(index) + ' success')
                index += 1
        finally:
            'file index:' + str(file_object.tell())
            file_object.close()
        return True

    # 合并
    def merge_request(self, taskid):
        return self.gene_request(api_merge, data=self.gene_params(api_merge, taskid=taskid))

    # 获取进度
    def get_progress_request(self, taskid):
        return self.gene_request(api_get_progress, data=self.gene_params(api_get_progress, taskid=taskid))

    # 获取结果
    def get_result_request(self, taskid):
        return self.gene_request(api_get_result, data=self.gene_params(api_get_result, taskid=taskid))

    def all_api_request(self):
        # 1. 预处理
        pre_result = self.prepare_request()
        taskid = pre_result["data"]
        # 2 . 分片上传
        self.upload_request(taskid=taskid, upload_file_path=self.upload_file_path)
        # 3 . 文件合并
        self.merge_request(taskid=taskid)
        # 4 . 获取任务进度
        while True:
            # 每隔20秒获取一次任务进度
            progress = self.get_progress_request(taskid)
            progress_dic = progress
            if progress_dic['err_no'] != 0 and progress_dic['err_no'] != 26605:
                #print('task error: ' + progress_dic['failed'])
                return
            else:
                data = progress_dic['data']
                task_status = json.loads(data)
                if task_status['status'] == 9:
                    #print('task ' + taskid + ' finished')
                    break
                #print('The task ' + taskid + ' is in processing, task status: ' + str(data))

            # 每次获取进度间隔20S
            time.sleep(20)
        # 5 . 获取结果
        #self.get_result_request(taskid=taskid)
        return self.get_result_request(taskid=taskid)


# 注意：如果出现requests模块报错："NoneType" object has no attribute 'read', 请尝试将requests模块更新到2.20.0或以上版本(本demo测试版本为2.20.0)
# 输入讯飞开放平台的appid，secret_key和待转写的文件路径
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
    for cleanwav in os.listdir("G:/语音测试程序/代码/md_clean"):
        cleanwavpath = "G:/语音测试程序/代码/md_clean/" + cleanwav
        
        '''
        api = RequestApi(appid="0500aed8", secret_key="fb047febcb6d5b5e522c976cb028075e", upload_file_path=cleanwavpath)
        a = api.all_api_request()
        
        noisewavpath = "G:/王斐斐/demo_noisy_8/add_babble" + "/" + cleanwav[:-4] + "_babble_snr8.wav"
        api1 = RequestApi(appid="0500aed8", secret_key="fb047febcb6d5b5e522c976cb028075e", upload_file_path=noisewavpath)
        b = api1.all_api_request()
        #print(b)
        noisewavpath = "G:/王斐斐/demo_noisy_5/add_babble" + "/" + cleanwav[:-4] + "_babble_snr5.wav"
        api2 = RequestApi(appid="0500aed8", secret_key="fb047febcb6d5b5e522c976cb028075e", upload_file_path=noisewavpath)
        c = api1.all_api_request()
        
        
    
        #print(a)
        '''
        api = RequestApi(appid="0500aed8", secret_key="fb047febcb6d5b5e522c976cb028075e", upload_file_path=cleanwavpath)
        a = api.all_api_request()
        
        noisewavpath = "G:/语音测试程序/代码/noisy100_10long/add_machinegun/" + cleanwav[:-4] + "__long_machinegun_snr10.wav"
        api1 = RequestApi(appid="0500aed8", secret_key="fb047febcb6d5b5e522c976cb028075e", upload_file_path=noisewavpath)
        b = api1.all_api_request()
        #print(b)
        #noisewavpath = "G:/王斐斐/noisy100_5/add_destroyerengine" + "/" + cleanwav[:-4] + "_destroyerengine_snr5.wav"
        #api2 = RequestApi(appid="8ac23318", secret_key="bc229a01a855d11e648c21381bfd1185", upload_file_path=noisewavpath)
        #c = api1.all_api_request()
        
        
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
        #
        with open('long_machinegun.txt','a') as f0:
            print(a,file=f0)
        with open('long_machinegun.txt','a') as f0:
            print(b,file=f0)
        #print(len(reference))

        #print(len(str(reference))
        wer_10=Levenshtein.distance(a, b)/len(a)
        corr_10.append(1-wer_10)
        '''
        score1_5 = sentence_bleu([a], c, weights=(1, 0, 0, 0))
        score2_5 = sentence_bleu([a], c, weights=(0.5, 0, 0, 0))
        score3_5 = sentence_bleu([a], c, weights=(0.33, 0.33, 0.33, 0))
        score4_5 = sentence_bleu([a], c, weights=(0.25, 0.25, 0.25, 0.25))
        bleu1_5.append(score1_5)
        bleu2_5.append(score2_5)
        bleu3_5.append(score3_5)
        bleu4_5.append(score4_5)

        #a = ''.join(a)
        c = ''.join(c)
        #
        
        with open('destroyerengine.txt','a') as f0:
            print(c,file=f0)
        #print(len(reference))

        #print(len(str(reference))
        wer_5=Levenshtein.distance(a, c)/len(c)
        corr_5.append(1-wer_5)
        '''
        
    for i in range(len(bleu1_10)):
        sum1_10 += bleu1_10[i]
        sum2_10 += bleu2_10[i]
        sum3_10 += bleu3_10[i]
        sum4_10 += bleu4_10[i]
        #sum1_5 += bleu1_5[i]
        #sum2_5 += bleu2_5[i]
        #sum3_5 += bleu3_5[i]
        #sum4_5 += bleu4_5[i]
        sumcorr_10 += corr_10[i]
        #sumcorr_5 += corr_5[i]
    bleu1_ave_10 = sum1_10/100
    bleu2_ave_10 = sum2_10/100
    bleu3_ave_10 = sum3_10/100
    bleu4_ave_10 = sum4_10/100

    #bleu1_ave_5 = sum1_5/100
    #bleu2_ave_5 = sum2_5/100
    #bleu3_ave_5 = sum3_5/100
    #bleu4_ave_5 = sum4_5/100
    corr_ave_10 = sumcorr_10/100
    #corr_ave_5 = sumcorr_5/100
    with open('long_machinegun.txt','a') as f0:
        print(n_10,bleu1_ave_10,bleu2_ave_10,bleu3_ave_10,bleu4_ave_10,corr_ave_10,file=f0)
    #print(corr)    
    '''
    api = RequestApi(appid="0500aed8", secret_key="fb047febcb6d5b5e522c976cb028075e", upload_file_path=r"G:\王斐斐\THCHS-30\data_thchs30\data_thchs30\data\A2_3.wav")
    b = api.all_api_request()
   # print(a)
    print(b)
    '''
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
