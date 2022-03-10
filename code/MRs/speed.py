# -*- coding: utf-8 -*-
"""
Created on Sun Jan  9 22:30:33 2022

@author: Administrator
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Jan  2 22:27:27 2022

@author: Administrator
"""

import numpy as np
from scipy.signal import correlate2d,firwin,filtfilt
from skimage.util import view_as_windows
import os
from scipy.io import wavfile
#import pyworld
from scipy.signal import resample
#import low_cut_filter
class WSOLA(object):
    def __init__(self,fs,speech_rate,shiftms=10):
        self.fs = fs
        self.speech_rate = speech_rate
        self.shiftms = shiftms
        self.sl = int(self.fs * self.shiftms/1000)
        self.fl = self.sl *2
        self.epstep = int(self.sl *self.speech_rate)
        self.win = np.hanning(self.fl)
    def duration_modification(self,x):#x为输入的语音信号
        wlen = len(x)
        wsolaed = np.zeros(int(wlen/self.speech_rate),dtype = 'd')
        sp = self.sl * 2
        rp = sp + self.sl
        ep = sp + self.epstep
        outp = self.sl
        wsolaed[:outp] = x[:outp]
        
        while wlen > ep + self.fl:
            ref = x[rp - self.sl:rp + self.sl]
            buff = x[ep - self.fl:ep + self.fl]
            delta = self._search_minimum_distance(ref,buff)
            epd = ep + delta
            spdata = x[sp:sp+self.sl] * self.win[self.sl:]
            epdata = x[epd - self.sl : epd] * self.win[:self.sl]
            if len(spdata) == len(wsolaed[outp:outp + self.sl]):
                wsolaed[outp:outp + self.sl] = spdata + epdata
            else:
                wsolaed_len = len(wsolaed[outp:outp + self.sl])
                wsolaed[outp:outp + self.sl] = spdata[:wsolaed_len] + epdata[:wsolaed_len]
            outp += self.sl
            sp = epd
            rp = sp + self.sl
            ep += self.epstep
        return wsolaed
    
    def _search_minimum_distance(self,ref,buff):
        if len(ref) < self.fl:
            ref = np.r_[ref,np.zeros(self.fl - len(ref))]
            
        buffmat = view_as_windows(buff,self.fl) * self.win
        refwin = np.array(ref * self.win).reshape(1,self.fl)
        corr = correlate2d(buffmat,refwin,mode='valid')
        
        return np.argmax(corr) - self.sl
'''
#高频修复
def high_frenquency_completion(x,transformed,f0rate,par):
    x = np.array(x,dtype = np.float)
    f0,time_axis = pyworld.harvest(x,par['fs'],f0_floor=par['shiftms'],f0_ceil=par['maxf0'],frame_period=par['shiftms'])
    spc = pyworld.cheaptrick(x,f0,time_axis,par['fs'],fft_size=par['fftl'])
    ap = pyworld.d4c(x,f0,time_axis,par['fs'],fft_size=par['fftl'])
    
    uf0 = np.zeros(len(f0))
    unvoice_anasyn = pyworld.synthesize(uf0,spc,ap,par['fs'],frame_period=par['shiftms'])
    
    fil = firwin(255,f0rate,pass_zero=False)
    HPFed_unvoice_anasyn = filtfilt(fil,1,unvoice_anasyn)
    
    if len(HPFed_unvoice_anasyn) > len(transformed):
        return transformed + HPFed_unvoice_anasyn[:len(transformed)]
    else:
        transformed[:len(HPFed_unvoice_anasyn)] += HPFed_unvoice_anasyn
        return transformed







def transform_f0(x,f0rate,config):
    if f0rate < 1.0:
        completion = True
    else:   
        completion = False
    
    fs = config["fs"]
    #x = low_cut_filter(x,fs,cutoff=70)
    
    wsola = WSOLA(fs,speech_rate = f0rate,shiftms = 10)
    wsolaed = wsola.duration_modification(x)
    
    xlen = len(x)
    transformed = resample(wsolaed,xlen)#,random_state=xlen
    
    if completion:
        transformed = high_frenquency_completion(x,transformed,f0rate,config)
    
    return transformed

'''

        
if __name__=="__main__":
    #config = config_all["Feature"]



    cleandir = "G:/语音测试程序/代码/md_clean"
    for cleanwav in os.listdir(cleandir):
        
        fs,x = wavfile.read(cleandir+'/'+cleanwav)
        x = np.array(x,dtype = np.float)
        wsola_long=WSOLA(fs,speech_rate=1/1.25,shiftms=10)
        wsolaed_long = wsola_long.duration_modification(x)
    
        wsola_short = WSOLA(fs,speech_rate = 1/0.75,shiftms = 10)
        wsolaed_short = wsola_short.duration_modification(x)
    
        
        speedwav1 = "G:/语音测试程序/代码/speed1.25/"
        speedlong = speedwav1 + cleanwav[:-4]+"_"+"_long"+".wav"
        speedwav2 = "G:/语音测试程序/代码/speed0.75/"
        speedshort = speedwav2 + cleanwav[:-4]+"_"+"_short"+".wav"
        wavfile.write(speedlong,fs,wsolaed_long.astype(np.int16))
        wavfile.write(speedshort,fs,wsolaed_short.astype(np.int16))
'''
    
    
    fs,x = wavfile.read("G:/王斐斐/vcc/demo_clean/A2_23.wav")
    x = np.array(x,dtype = np.float)
    wsola_long=WSOLA(fs,speech_rate=1/1.25,shiftms=10)
    wsolaed_long = wsola_long.duration_modification(x)pi
    
    wsola_short = WSOLA(fs,speech_rate = 1/0.75,shiftms = 10)
    wsolaed_short = wsola_short.duration_modification(x)
    
    wavfile.write("wsola_long.wav",fs,wsolaed_long.astype(np.int16))
    wavfile.write("wsola_short.wav",fs,wsolaed_short.astype(np.int16))
    
'''
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    