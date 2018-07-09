#-*- coding: utf-8 -*- 
import xlrd
import xlwt
import re
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import wx

import wx

class log(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,parent=None,id=-1,title="日志分析",size=(400,400))
        panel = wx.Panel(self,-1)

        button = wx.Button(panel,label=u"Start",pos=(100,280),size=(50,50))
        dir_stat = wx.StaticText(panel,-1,u"输入日志所在目录:",pos=(20,100))
        self.dname = wx.TextCtrl(panel,-1,r"E:\data\0705\8G-56M1024QAM", pos=(150,100))
        bd_stat = wx.StaticText(panel, -1, u"输入板ID:", pos=(20, 150))
        self.bd_id = wx.TextCtrl(panel, -1, r"3", pos=(150, 150))
        ne_stat = wx.StaticText(panel, -1, u"输入网元类型:", pos=(20, 200))
        self.ne_type = wx.TextCtrl(panel, -1, r"LH", pos=(150, 200))

        self.Bind(wx.EVT_BUTTON,self.OnClick,button)
        self.Centre()
        # dname.GetValue()
        self.filedir,self.board, self.type = "", "", ""
    def OnClick(self,event):
        self.filedir = self.dname.GetValue()
        self.board = self.bd_id.GetValue()
        self.type = self.ne_type.GetValue()
        # print(filedir)
        self.Close(True)

app = wx.App()
frame = log()
frame.Show()
app.MainLoop()

try:
    data=xlwt.Workbook()
    sheet=data.add_sheet("data")
except Exception as e:
    print(str(e))
#input the dir name and board name
filedir=frame.filedir
print(filedir)
board=frame.board
type=frame.type

# filedir=r"E:\data\0705\8G-56M-129.9.121.7_szhw_2018-07-05"
# board='4'
# type = 'LH'  #LH or SPLIT
# for index in range(len(board)) LH +50 +70, 20+40
if type == 'LH':
    port1_odu = str(50+int(board))
    port2_odu = str(70+int(board))
elif type == 'SPLIT':
    port1_odu = str(20 + int(board))
    port2_odu = str(40 + int(board))
else:
    pass

filenames=glob.glob(filedir+'\\'+'*.nv2log')
# print(port2_odu)
#patterns
# pattern_log_mse = re.compile(r'\s*?if_mse_(m\w+).*?:00\s+([-\d]+).*board=(\d+),subcard=255,port=(\d).*$') #right
pattern_log_mse = re.compile(r'\s*?if_mse_(m\w+)\s+15m\s+(2018-\d+-\d+\s\d+:\d+:\d+)\+\d+:00\s+([-\d]+).*board=(\d+),subcard=255,port=(\d).*$')
# pattern_es = re.compile(r'\s*?if_es.*:00\s+(\d+).*board=(\d+),subcard=255,port=(\d).*$')
pattern_es = re.compile(r'\s*?if_es\s+15m.*:00\s+(\d+).*board=(\d+),subcard=255,port=(\d).*$')
# pattern_ses = re.compile(r'\s*?if_ses.*:00\s+(\d+).*board=(\d+),subcard=255,port=(\d).*$')
pattern_ses = re.compile(r'\s*?if_ses\s+15m.*:00\s+(\d+).*board=(\d+),subcard=255,port=(\d).*$')
pattern_lof = re.compile(r'\s+.*MW_LOF.*board=(\d+),subcard=255,port=(\d).*$')
pattern_block = re.compile(r'>>>.*')
# pattern_eagc = re.compile(r'>>> :cfg-modem-dfx:(\d+),.*,(\d)"\s')
pattern_eagc = re.compile(r'>>> :cfg-modem-dfx:(\d+),"\w+_\w+,(\d+),(\d).*$')
# pattern_eagc = re.compile(r'>>> :cfg-modem-dfx:(\d+),.*,(\d)"$')
pattern_agcpwr = re.compile(r'EAGC_PWR_(\w+) = (0x[0-9a-f]+)')
pattern_ph = re.compile(r'PhaseHit_(\w) = (\d*.\d+)kHz\s')
pattern_temp = re.compile(r'\s+(\d{2})\s+([-\d]+)\s+$')
pattern_ffcr = re.compile(r'.*LMS_ffcr.max=([-\d]+\.\d+)\(dB.*LMS_ffcr.min=([-\d]+\.\d+)\(dB.*')


#index
index_log_mse_port1=1
index_log_mse_port2=1

index_eagc_port1=1
index_eagc_port2=1

index_ph_port1=1
index_ph_port2=1

index_temp_port1=1
index_temp_port2=1
index_ffcr_port1 = 1
index_ffcr_port2 = 1

# index_lof=1;
port1_start = 0
port2_start = 0


#mulu
sheet.write(0,0,"Time")
sheet.write(0,1,"mse max port1")
sheet.write(0,2,"mse min port1")
sheet.write(0,3,"mse max port2")
sheet.write(0,4,"mse min port2")
sheet.write(0,5,"ifes port1")
sheet.write(0,6,"ifes port2")
sheet.write(0,7,"ifses port1")
sheet.write(0,8,"ifses port2")
sheet.write(0,9,"eagc max port1")
sheet.write(0,10,"eagc min port1")
sheet.write(0,11,"eagc max port2")
sheet.write(0,12,"eagc min port2")
sheet.write(0,13,"phasehit M port1")
sheet.write(0,14,"phasehit S port1")
sheet.write(0,15,"phasehit M port2")
sheet.write(0,16,"phasehit S port2")
sheet.write(0,17,"temp port1")
sheet.write(0,18,"temp port2")
sheet.write(0,19,"ffcr_max1")
sheet.write(0,20,"ffcr_min1")
sheet.write(0,21,"ffcr_max2")
sheet.write(0,22,"ffcr_min2")

mse_max1=[]
mse_min1=[]
mse_max2=[]
mse_min2=[]
agc_max1=[]
agc_min1=[]
agc_max2=[]
agc_min2=[]
phm1=[]
phs1=[]
phm2=[]
phs2=[]
temp1=[]
temp2=[]
ffcr_max1=[]
ffcr_min1=[]
ffcr_max2=[]
ffcr_min2=[]
# filedir=r"E:\data\0627\6.27(-40-65)_XMC-3H_23G_28M_4096QAM_ISM8_IS8_XPIC-FAIL\129.9.176.120_1400_0"
# filenames=glob.glob(filedir+'\\'+'*.nv2log')

# print(filenames)
for filename in filenames:
    for line in open(filename):
        log_mse_match=re.match(pattern_log_mse,line)
        log_es=re.match(pattern_es,line)
        log_ses = re.match(pattern_ses, line)
        # mw_lof = re.match(pattern_lof,line)
        block = re.match(pattern_block,line)
        eagc = re.match(pattern_eagc,line)
        eagc_pwr = re.match(pattern_agcpwr,line)
        ph = re.match(pattern_ph,line)
        temp = re.match(pattern_temp,line)
        ffcr = re.match(pattern_ffcr,line)

##log_mse
        if log_mse_match:
            if log_mse_match.group(4) == board:
                if log_mse_match.group(1) == 'max'and log_mse_match.group(5) == '1':
                    # print(log_mse_match.group(1))
                    # print(log_mse_match.group(4))
                    sheet.write(index_log_mse_port1, 1, log_mse_match.group(3))
                    sheet.write(index_log_mse_port1, 0, log_mse_match.group(2))
                    mse_max1.append(int(log_mse_match.group(3)))
                elif log_mse_match.group(1) == 'min' and log_mse_match.group(5) == '1':
                    sheet.write(index_log_mse_port1, 2, log_mse_match.group(3))
                    mse_min1.append(int(log_mse_match.group(3)))
                    index_log_mse_port1=index_log_mse_port1+1
                elif log_mse_match.group(1) == 'max' and log_mse_match.group(5) == '2':
                    sheet.write(index_log_mse_port2, 3, log_mse_match.group(3))
                    mse_max2.append(int(log_mse_match.group(3)))
                elif log_mse_match.group(1) == 'min' and log_mse_match.group(5) == '2':
                    sheet.write(index_log_mse_port2, 4, log_mse_match.group(3))
                    mse_min2.append(int(log_mse_match.group(3)))
                    index_log_mse_port2 = index_log_mse_port2 + 1
                else:
                    pass
            else:
                pass
## log_es
        elif log_es:
            if log_es.group(2) == board:
                # print(log_es.group(2))
                if log_es.group(3) == '1':
                    sheet.write(index_log_mse_port1, 5, log_es.group(1))
                elif log_es.group(3) == '2':
                    sheet.write(index_log_mse_port2, 6, log_es.group(1))
                else:
                    pass
            else:
                pass
        elif log_ses:
            if log_ses.group(2) == board:
                # print(log_ses.group(2))
                if log_ses.group(3) == '1':
                    sheet.write(index_log_mse_port1, 7, log_ses.group(1))
                elif log_ses.group(3) == '2':
                    sheet.write(index_log_mse_port2, 8, log_ses.group(1))
                else:
                    pass
            else:
                pass
#EAGC
        elif block:
            if eagc:
                # print(eagc.group(0))
                if eagc.group(1) == board and eagc.group(3) == '0':
                    port1_start = 1
                    port2_start = 0
                elif eagc.group(1) == board and eagc.group(3) == '1':
                    port2_start = 1
                    port1_start = 0
                    # print(port2_start)
                else:
                    port1_start = 0
                    port2_start = 0
            else:
                pass
                # port1_start = 0
                # port2_start = 0
##EAGC PWR
        elif eagc_pwr:
            # print(eagc_pwr.group(1))
            # print(eagc_pwr.group(2))
            if port1_start == 1 and eagc_pwr.group(1) == 'MAX':
                sheet.write(index_eagc_port1, 9, int(eagc_pwr.group(2),16))
                # print(eagc_pwr.group(2))
                agc_max1.append(int(eagc_pwr.group(2),16))
            elif port1_start == 1 and eagc_pwr.group(1) == 'MIN':
                sheet.write(index_eagc_port1, 10, int(eagc_pwr.group(2), 16))
                agc_min1.append(int(eagc_pwr.group(2),16))
                index_eagc_port1=index_eagc_port1+1
            elif port2_start == 1 and eagc_pwr.group(1) == 'MAX':
                sheet.write(index_eagc_port2, 11, int(eagc_pwr.group(2), 16))
                agc_max2.append(int(eagc_pwr.group(2),16))
                # print(eagc_pwr.group(2))
            elif port2_start == 1 and eagc_pwr.group(1) == 'MIN':
                sheet.write(index_eagc_port2, 12, int(eagc_pwr.group(2), 16))
                agc_min2.append(int(eagc_pwr.group(2),16))
                index_eagc_port2=index_eagc_port2+1
            else:
                pass
#phasehit
        elif ph:
            # print(ph.group(1))
            # print(ph.group(2))
            if port1_start == 1 and ph.group(1) == 'M':
                sheet.write(index_ph_port1, 13, ph.group(2))
                phm1.append(float(ph.group(2)))
            elif port1_start == 1 and ph.group(1) == 'S':
                sheet.write(index_ph_port1, 14, ph.group(2))
                phs1.append(float(ph.group(2)))
                index_ph_port1=index_ph_port1+1
                # print(ph.group(2))
            elif port2_start == 1 and ph.group(1) == 'M':
                sheet.write(index_ph_port2, 15, ph.group(2))
                phm2.append(float(ph.group(2)))
                # print(ph.group(2))
            elif port2_start == 1 and ph.group(1) == 'S':
                sheet.write(index_ph_port2, 16, ph.group(2))
                phs2.append(float(ph.group(2)))
                index_ph_port2 = index_ph_port2 + 1
            else:
                pass
##temp
        elif temp:
            # print(temp.group(2))
            # print(ph.group(2))
            if temp.group(1) == port1_odu:
                sheet.write(index_temp_port1, 17, temp.group(2))
                temp1.append(int(temp.group(2)))
                index_temp_port1=index_temp_port1+1
            elif temp.group(1) == port2_odu:
                sheet.write(index_temp_port2, 18, temp.group(2))
                temp2.append(int(temp.group(2)))
                index_temp_port2=index_temp_port2+1
            else:
                pass
#ffcr_mse
        elif ffcr:
            if port1_start == 1:
                sheet.write(index_ffcr_port1,19,ffcr.group(1))
                sheet.write(index_ffcr_port1, 20, ffcr.group(2))
                ffcr_max1.append(ffcr.group(1))
                ffcr_min1.append(ffcr.group(2))
                index_ffcr_port1 = index_ffcr_port1 + 1
            elif port2_start == 1:
                sheet.write(index_ffcr_port2,21,ffcr.group(1))
                sheet.write(index_ffcr_port2, 22, ffcr.group(2))
                ffcr_max2.append(ffcr.group(1))
                ffcr_min2.append(ffcr.group(2))
                index_ffcr_port2 = index_ffcr_port2 +1
            else:
                pass
##EOF

        else:
            pass
            # sheet.write(index_log_mse_port1, 5, 0)
            # sheet.write(index_log_mse_port2, 6, 0)



#plot
Fig=plt.figure(figsize=(16,8))
agc_max1=np.array(agc_max1)
agc_min1=np.array(agc_min1)
agc_max2=np.array(agc_max2)
agc_min2=np.array(agc_min2)

mse_max1=np.array(mse_max1)
mse_min1=np.array(mse_min1)
mse_max2=np.array(mse_max2)
mse_min2=np.array(mse_min2)

ffcr_max1=np.array(ffcr_max1)
ffcr_min1=np.array(ffcr_min1)
ffcr_max2=np.array(ffcr_max2)
ffcr_min2=np.array(ffcr_min2)

plt.subplot(421)
plt.plot(agc_max1[2:]-agc_min1[2:])
plt.title(filedir+"board"+board+"_Port1")
plt.ylabel("EAGC Jitter(MAX-MIN)")
plt.grid()

plt.subplot(422)
plt.plot(agc_max2[2:]-agc_min2[2:])
plt.title(filedir+"board"+board+"_Port2")
plt.ylabel("EAGC Jitter(MAX-MIN)")
plt.grid()

#
# plt.subplot(523)
# plt.plot(agc_max1[1:])
# plt.plot(agc_min1[1:],'--r')
# plt.title("Port1")
# plt.ylabel("max and min of EAGC")
# plt.grid()
#
# plt.subplot(524)
# plt.plot(agc_max2[1:])
# plt.plot(agc_min2[1:],'--r')
# plt.title("Port2")
# plt.ylabel("max and min of EAGC")
# plt.grid()

plt.subplot(423)
plt.plot(mse_max1[2:]*0.1)
plt.plot(mse_min1[2:]*0.1,'--r')
# plt.plot(ffcr_max1[2:],'y')
plt.ylim(-51,-35)
plt.ylabel("MSE max and min(dB)")
# plt.grid(which='minor',linestyle=':', linewidth='0.5', color='black')
plt.grid()
plt.subplot(424)
plt.plot(mse_max2[2:]*0.1)
plt.plot(mse_min2[2:]*0.1,'--r')
# plt.plot(ffcr_max2[2:],'y')
# plt.legend("min")
plt.ylim(-51,-35)
plt.ylabel("MSE max and min(dB)")
plt.grid()

plt.subplot(425)
plt.plot(phm1[2:])
plt.plot(phs1[2:],'--r')
plt.ylabel("Phasehit M and S(KHz)")
plt.ylim(0,20)
plt.grid()
plt.subplot(426)
plt.plot(phm2[2:])
plt.plot(phs2[2:],'--r')
plt.ylabel("Phasehit M and S(KHz)")
plt.ylim(0,20)
plt.grid()

plt.subplot(427)
plt.plot(temp1[2:])
plt.ylabel("temperature")
plt.grid()
plt.subplot(428)
plt.plot(temp2[2:])
plt.ylabel("temperature")
plt.grid()
plt.show()

# Fig.savefig(filedir+'\\'+'board'+board+'.pdf')
# Fig.savefig(filedir+'\\'+'board'+board+'.png')
fname=filedir.replace("\\","-")
fname=fname.replace(":","-")
data.save(filedir+'\\'+fname[-50:]+'_'+'board'+board+'.xls')
Fig.savefig(filedir+'\\'+fname[-50:]+'_'+'board'+board+'.png')
Fig.savefig(filedir+'\\'+fname[-50:]+'_'+'board'+board+'.pdf')
