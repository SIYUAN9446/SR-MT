# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 19:56:27 2021

@author: Administrator
"""

import soundfile as sf
import numpy as np
import sys
import os
import re

def add_noise(noisedir,cleandir,snr):
    # noisy
    splitdir=re.split(r"\\",noisedir)
    wavdir="" # 所有wav文件所在路径
    for i in range(len(splitdir)-1):
        wavdir += splitdir[i] + '/'
    print(wavdir)
    noisydir=wavdir+"noisy100_0/"  # 带噪语音存储路径
    print(noisydir)
    os.mkdir(noisydir)
    # noise
    for noisewav in os.listdir(noisedir):
        noise, fs = sf.read(noisedir+'/'+noisewav)
        print(fs)
        noisy_splitdir=noisydir+"add_"+noisewav[:-4]+"/"
        os.mkdir(noisy_splitdir)
    # clean
        for cleanwav in os.listdir(cleandir):
            clean, Fs = sf.read(cleandir+"/"+cleanwav)
            #print(Fs)
    # add noise
            if len(clean) <= len(noise):#fs == Fs and 
    # 纯净语音能量
                cleanenergy = np.sum(np.power(clean,2))
        # 随机索引与clean长度相同的noise信号
                ind = np.random.randint(1, len(noise) - len(clean) + 1)
                noiselen=noise[ind:len(clean) + ind]
		# 噪声语音能量
                noiseenergy = np.sum(np.power(noiselen,2))
                #print(cleanenergy / noiseenergy)
		# 噪声等级系数
                noiseratio = np.sqrt((cleanenergy / noiseenergy) / (np.power(10, snr * 0.1)))
		# 随机索引与clean长度相同的noise信号
                noisyAudio = clean + noise[ind:len(clean)+ind] * noiseratio
        # write wav
                noisywavname=noisy_splitdir+cleanwav[:-4]+"_"+noisewav[:-4]+"_snr"+str(snr)+".wav"
                sf.write(noisywavname, noisyAudio, 16000)
            else:
                print("fs of clean and noise is unequal or the length of clean is longer than noise's\n")
                sys.exit(-1)

noisedir="G:/语音测试程序/数据集/NoiseX-92/NoiseX-92"
cleandir="G:/语音测试程序/voice_data/english/TIMIT/TIMIT_clean"
snr=0
add_noise(noisedir,cleandir,snr)
