#!/usr/bin/env python
# -*- coding: utf-8 -*-


import argparse
import os
import traceback
import struct
import codecs
import re

import sys

from langconv import *
#繁简转换工具的导入
import difflib

import warnings
warnings.simplefilter("ignore")

usage="msgconv.py -d dos.msg -w 98chs.msg -e em.msg"

class MessageData:
  comment = ""
  begin = ""
  message = ""
  messagetemp = ""
  end = ""
      
def ParseOptions():

  #示例：msgconv.py -d dos.msg -w 98chs.msg -e em.msg
  parser = argparse.ArgumentParser(description='Convert palwin message file to paldos message file.')

  parser.add_argument('-d','--dos', dest='filepathd', 
                   help='Dos file path')
  parser.add_argument('-w','--win', dest='filepathw', 
                   help='Win file path')
  parser.add_argument('-e','--ext', dest='filepathe', 
                   help='External Message file path')
  
  args = parser.parse_args()
  #usage=parser.print_help()
  return args

def main():
    options = ParseOptions()
    messagedos = []
    messagewin = []
    messageext = []
    #存储一行行对话文本的数组。

    listdos = []
    listwin = []
    listext = []
    #存储对象的数组。
    
    textLine = ""
    #一行文字。
    indexCount = 0
    #索引编号。
    indexAdress = 0
    #文字地址。
    msg_bytes = ""
    #最终的dosext.msg的数据。
    part_bytes = ""
    partsim_bytes = ""
    partaggr_bytes = ""
    fail_bytes = ""
    #临时脚本数据。

    dos_msg_started = 0
    ext_msg_started = 0
    #是否已经进入了MESSAGE部分。
    dos_pre_lines = ""
    #MESSAGE部分之前的部分。
    ext_pre_lines = ""
    #MESSAGE部分之前的部分。
    scriptCount = 0
    #脚本计量。

    mratio = 0
    maxratio = 0
    #相似度匹配的当前值和最大值。

    tempcounter = 0
    partcounter = 0
    failcounter = 0

    isok =0
    

    is_msg_group = 0    #是否正在处理文字组的标示。
    
    print("")
    print("SDLPal Message Converter v0.55")
    print("Developed by SDLPal Team")

    print("CHT2CHS Convertion with code form nstools. You can get nstools on GitHub. ")
    print("This program is distributed under the terms of General Public License v2. \n")
    print("Now loading data...")

    try:
        with open(options.filepathd,'rt',encoding='utf-8') as f:
            messagedos=f.readlines()
    except:
        traceback.print_exc()
    #打开文字文件。
    try:
        with open(options.filepathw,'rt',encoding='utf-8') as f:
            messagewin=f.readlines()
    except:
        traceback.print_exc()
    #打开文字文件。
    try:
        with open(options.filepathe,'rt',encoding='utf-8') as f:
            messageext=f.readlines()
    except:
        traceback.print_exc()
    #打开文字文件。

    if messagedos[0][:3] == codecs.BOM_UTF8:
      messagedos[0] = messagedos[0][3:]
    #去掉BOM。

    if messagewin[0][:3] == codecs.BOM_UTF8:
      messagewin[0] = messagewin[0][3:]
    #去掉BOM。

    if messageext[0][:3] == codecs.BOM_UTF8:
      messageext[0] = messageext[0][3:]
    #去掉BOM。

    listdos.append(MessageData())
    listwin.append(MessageData())
    listext.append(MessageData())
    #建立第一个对象。
    
    pattern = re.compile('[\u4e00-\u9fa5]')
    c = Converter("zh-hans")

    for textLine in messagedos:
        #读入一行。
        if textLine.find("[BEGIN MESSAGE]") == 0:
            #新的段落开始。创建一个新的MessageData对象。
            dos_msg_started = 1
            
            is_msg_group = 1
            listdos[-1].begin = textLine
        elif textLine.find("[END MESSAGE]") == 0:
            #段落结束。
            is_msg_group = 0

            listdos[-1].messagetemp = listdos[-1].message

            listdos[-1].messagetemp = c.convert(str(listdos[-1].messagetemp))
            
            listdos[-1].messagetemp = listdos[-1].messagetemp.replace('∼', '～')
            listdos[-1].messagetemp = listdos[-1].messagetemp.replace('　', '')
            listdos[-1].messagetemp = listdos[-1].messagetemp.replace('•', '·')
            listdos[-1].messagetemp = listdos[-1].messagetemp.replace('．', '·')
            listdos[-1].messagetemp = listdos[-1].messagetemp.replace('妳', '你')
            listdos[-1].messagetemp = listdos[-1].messagetemp.replace('她', '他')
            listdos[-1].messagetemp = listdos[-1].messagetemp.replace('它', '他')
            listdos[-1].messagetemp = listdos[-1].messagetemp.replace('僮', '童')
            listdos[-1].messagetemp = listdos[-1].messagetemp.replace('麽', '么')
            listdos[-1].messagetemp = listdos[-1].messagetemp.replace('著', '着')
            listdos[-1].messagetemp = listdos[-1].messagetemp.replace('後', '后')
            listdos[-1].messagetemp = listdos[-1].messagetemp.replace('於', '于')
            listdos[-1].messagetemp = listdos[-1].messagetemp.replace('倌', '官')
            listdos[-1].messagetemp = listdos[-1].messagetemp.replace('嬷', '妈')
            listdos[-1].messagetemp = listdos[-1].messagetemp.replace('丶', '、')
            listdos[-1].messagetemp = listdos[-1].messagetemp.replace('一付', '一副')

            #m = pattern.findall(unicode(listdos[-1].messagetemp))
            #if m:
            #    listdos[-1].messagetemp = str("".join(m))
            listdos[-1].end = textLine
            
            listdos.append(MessageData())
            #新的段落要开始了，创建下一个对象。
        else:
            if dos_msg_started == 1:
            #如果已经在MESSAGE部分。
                if is_msg_group == 1:
                    #普通文字行。
                    listdos[-1].message += textLine
                    #将Message数据追加入Message对象的Message属性。
                else:
                    listdos[-1].comment += textLine
            else:
            #否则，就是WORD等部分的数据。在dos_pre_lines写入数据。
                dos_pre_lines += textLine

    for textLine in messagewin:
        #读入一行。
        if textLine.find("[BEGIN MESSAGE]") == 0:
            #新的段落开始。创建一个新的MessageData对象。
            
            is_msg_group = 1
            listwin[-1].begin = textLine
        elif textLine.find("[END MESSAGE]") == 0:
            #段落结束。
            is_msg_group = 0

            
            listwin[-1].messagetemp = listwin[-1].message

            listwin[-1].messagetemp = c.convert(str(listwin[-1].messagetemp))
            
            listwin[-1].messagetemp = listwin[-1].messagetemp.replace('∼', '～')
            listwin[-1].messagetemp = listwin[-1].messagetemp.replace('　', '')
            listwin[-1].messagetemp = listwin[-1].messagetemp.replace('•', '·')
            listwin[-1].messagetemp = listwin[-1].messagetemp.replace('．', '·')
            listwin[-1].messagetemp = listwin[-1].messagetemp.replace('妳', '你')
            listwin[-1].messagetemp = listwin[-1].messagetemp.replace('她', '他')
            listwin[-1].messagetemp = listwin[-1].messagetemp.replace('它', '他')
            listwin[-1].messagetemp = listwin[-1].messagetemp.replace('僮', '童')
            listwin[-1].messagetemp = listwin[-1].messagetemp.replace('麽', '么')
            listwin[-1].messagetemp = listwin[-1].messagetemp.replace('著', '着')
            listwin[-1].messagetemp = listwin[-1].messagetemp.replace('後', '后')
            listwin[-1].messagetemp = listwin[-1].messagetemp.replace('於', '于')
            listwin[-1].messagetemp = listwin[-1].messagetemp.replace('倌', '官')
            listwin[-1].messagetemp = listwin[-1].messagetemp.replace('嬷', '妈')
            listwin[-1].messagetemp = listwin[-1].messagetemp.replace('丶', '、')
            listwin[-1].messagetemp = listwin[-1].messagetemp.replace('一付', '一副')

            #m = pattern.findall(unicode(listwin[-1].messagetemp))
            #if m:
            #    listwin[-1].messagetemp = str("".join(m))
            #listwin[-1].end = textLine
            listwin.append(MessageData())
            #新的段落要开始了，创建下一个对象。
        else:
            if is_msg_group == 1:
                #普通文字行。
                listwin[-1].message += textLine
                #将Message数据追加入Message对象的Message属性。
            else:
                listwin[-1].comment += textLine

    for textLine in messageext:
        #读入一行。
        if textLine.find("[BEGIN MESSAGE]") == 0:
            ext_msg_started = 1
            
            is_msg_group = 1
            listext[-1].begin = textLine
        elif textLine.find("[END MESSAGE]") == 0:
            #段落结束。
            is_msg_group = 0
            listext[-1].end = textLine
            listext.append(MessageData())
            #新的段落要开始了。创建一个新的MessageData对象。
        else:
            if ext_msg_started == 1:
            #如果已经在MESSAGE部分。
                if is_msg_group == 1:
                    #普通文字行。
                    listext[-1].message += textLine
                    #将Message数据追加入Message对象的Message属性。
                else:
                    listext[-1].comment += textLine
            else:
            #否则，就是WORD等部分的数据。在ext_pre_lines写入数据。
                #pdb.set_trace()
                ext_pre_lines += textLine

    print("Processing start!")

    for currentdosobj in listdos:
        #遍历listdos中每一个对象，然后在listwin中找到对应对象。
        #再以begin数据从listext中找出对应的message，写回listdos中对应对象的message属性。
        isok = 0

        for currentwinobj in listwin:
            if currentdosobj.message.rstrip() == currentwinobj.message.rstrip():
                for currentextobj in listext:
                    if currentwinobj.begin.rstrip() == currentextobj.begin.rstrip():
                        tempcounter += 1
                        isok = 1
                        currentdosobj.message = currentextobj.message
                        break

            elif currentdosobj.messagetemp.rstrip() == currentwinobj.messagetemp.rstrip():
                for currentextobj in listext:
                    if currentwinobj.begin.rstrip() == currentextobj.begin.rstrip():
                        tempcounter += 1
                        partcounter += 1
                        isok = 1

                        #part_bytes += str(partcounter)
                        #part_bytes += currentdosobj.message + "\n"
                        #part_bytes += currentwinobj.message + "\n"
                        #part_bytes += "\n\n"
                        
                        currentdosobj.message = currentextobj.message
                        break
                      

            if isok == 1:
                break
        if isok ==0:
            mratio = 0
            maxratio = 0.75
            for currentwinobj in listwin:
                mratio = difflib.SequenceMatcher(None,currentdosobj.messagetemp,currentwinobj.messagetemp).ratio()
                if  mratio>= maxratio:
                    maxratio = mratio
                    for currentextobj in listext:
                        if currentwinobj.begin.rstrip() == currentextobj.begin.rstrip():
                            tempcounter += 1
                            partcounter += 1
                            isok = 1

                            partaggr_bytes += str(partcounter) + "\n"
                            partaggr_bytes += "mratio: " + str(mratio) + "\n"
                            partaggr_bytes += "maxratio: " + str(maxratio) + "\n"
                            partaggr_bytes += currentdosobj.begin + "\n"
                            partaggr_bytes += currentdosobj.messagetemp + "\n"
                            partaggr_bytes += currentwinobj.begin + "\n"
                            partaggr_bytes += currentwinobj.messagetemp + "\n"
                            partaggr_bytes += "\n\n"

                        
                            currentdosobj.message = currentextobj.message
                            break
        
        if isok == 0:
            mratio = 0
            maxratio = 0.75
            #print "Failed matching the following message. Now trying partial matching! \n" + currentdosobj.message.decode("utf8")
            for currentwinobj in listwin:
                mratio = difflib.SequenceMatcher(None,currentdosobj.messagetemp[0:32],currentwinobj.messagetemp[0:32]).ratio()
                if  mratio>= maxratio:
                    #print "Success!"
                    for currentextobj in listext:
                        if currentwinobj.begin.rstrip() == currentextobj.begin.rstrip():
                            tempcounter += 1
                            partcounter += 1
                            isok = 1

                            partaggr_bytes += str(partcounter) + "\n"
                            partaggr_bytes += "Partial mratio: " + str(mratio) + "\n"
                            partaggr_bytes += "Partial maxratio: " + str(maxratio) + "\n"
                            partaggr_bytes += currentdosobj.begin + "\n"
                            partaggr_bytes += currentdosobj.message + "\n"
                            partaggr_bytes += currentwinobj.begin + "\n"
                            partaggr_bytes += currentwinobj.message + "\n"
                            partaggr_bytes += "\n\n"

                        
                            currentdosobj.message = currentextobj.message
                            break
        
        if isok ==0:
            print(f"Failed to match. Block begin:{currentdosobj.begin.rstrip()};msg:{currentdosobj.message.rstrip()}")
            failcounter += 1
            fail_bytes += currentdosobj.begin + "\n"
            fail_bytes += currentdosobj.message + "\n\n"

            
        print(str(tempcounter) + " of " + str(len(listdos)) + "\r", end=' ')


    msg_bytes += ext_pre_lines
    
    for currentdosobj in listdos:
        
        
        msg_bytes += currentdosobj.comment
        msg_bytes += currentdosobj.begin
        msg_bytes += currentdosobj.message
        msg_bytes += currentdosobj.end
        msg_bytes += "\n\n"

    try:

        with open("dosextOKTest.msg.txt","w",encoding='utf-8') as f:
            f.write(msg_bytes)
    except:
        traceback.print_exc()

    try:

        with open("part.txt","w",encoding='utf-8') as f:
            f.write(partaggr_bytes)
    except:
        traceback.print_exc()

    #try:

       # with open("partsim.txt","w") as f:
            #f.write(bytearray(partsim_bytes))
    #except:
        #traceback.print_exc()

    try:

        with open("fail.txt","w",encoding='utf-8') as f:
            f.write(fail_bytes)
    except:
        traceback.print_exc()
        
    print("OK! Convertion finished!")
    #print "Success: " + str(tempcounter) + " of " + str(len(listdos))
    print("Partial: " + str(partcounter))
    print("Failed: " + str(failcounter))
    
if __name__ == '__main__':
    main()
