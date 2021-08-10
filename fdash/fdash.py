import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import re
import numpy as np
import unicodedata
import collections
import string
import os
import math
import json
import sys
import distutils.core
from bs4 import BeautifulSoup
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output
from datetime import date as dt
from datetime import datetime

maindir = os.getcwd()
targetdir = maindir

name = ''
given ='C:\\'
lang = 'en'
trimming = True
res = 50
trimlimit = 2
mode = 'json'
l = 15
wordn = 40
chattercolor = ['#C73679','#3679C7']
trimexclusions = []
bw = '1'

if len(sys.argv) > 1:
    name = sys.argv[1]
    given = sys.argv[2]
    lang = sys.argv[3]
    trimming = bool(distutils.util.strtobool(sys.argv[4]))
    res = int(sys.argv[5])
    trimlimit = int(sys.argv[6])
    mode = sys.argv[7]
    l = int(sys.argv[8])
    wordn = int(sys.argv[9])
    chattercolor[0] = sys.argv[10]
    chattercolor[1] = sys.argv[11]
    bw = sys.argv[12]

if bw == '1':
    textcolor = '#ffffff'
else:
    textcolor = '#1d1d1d'

messmode = 0
dictionary = ['Messages','Words']

mptc = 0
tptc = 0

maxval = 0
i = 0
days = 0
m = 0
last = [0,0,0]
fileN = 1

lastbtnV = [[0,0],[0,0],[0,0]]

zoom = [0,0]

dates = []
hours = []
chatters = []   

months = []
weekdays = ['MON','TUE','WED','THU','FRI','SAT','SUN']
stopwords = ['/p/','/v/','/l/']
messexclusions = []

counter = [collections.Counter(),collections.Counter(),collections.Counter()]
totalcount = [0,0,0,0,0,0]
data = [[],[],[],[],[],[],[]]
orderedData = [[],[],[],[],[],[]]
dateBuckets = []
hourBuckets = [[],[],[],[],[],[]]
weekdayBuckets = [[],[],[],[],[],[]]
linepBuckets = []

for i in range(0, 6):
    for x in range(0, 7):
        weekdayBuckets[i].append(0)

for i in range(0, l):
    dateBuckets.append([[],[],[],[],[],[],[],[]])
    linepBuckets.append([[],[],[],[],[],[],[],[]])

for i in range(0, 24):
    hours.append(i)
    hourBuckets[0].append(0)
    hourBuckets[1].append(0)
    hourBuckets[2].append(0)
    hourBuckets[3].append(0)
    hourBuckets[4].append(0)
    hourBuckets[5].append(0)

hours.append(hours[0])
weekdays.append(weekdays[0])


def replace(s, newstring, index):
    if index < 0:
        return newstring + s
    if index > len(s):
        return s + newstring

    return s[:index] + newstring + s[index + 1:]

def normalize(dt):
    text = ''.join(char for char in
                   unicodedata.normalize('NFKD', dt)
                   if unicodedata.category(char) != 'Mn')
    for i in range(0,len(text)):
        if text[i] == 'Ł':
            text = replace(text, 'l', i)
        elif text[i] == 'ł':
            text = replace(text, 'l', i)

    return text.lower()

def trim(word):
    w = word[0]
    trimmed = word[0]
    c = len(collections.Counter(word))
    if c >= trimlimit:
        for i in range(0,len(word)):
            if word[i] != w:
                trimmed = trimmed + word[i]
            w = word[i]
        if trimmed in trimexclusions:
            return word
        else:
            return trimmed
    else:
        return word

def scandir(name,given):
    global fileN
    global customFileN

    if name == '':
        raise Exception("E1")

    ar = ['messages','inbox']
    directory = given
    name = normalize(name)

    name = ''.join(x for x in name if x != ' ')

    fd1 = False
    fd2 = False

    for i in range(0,len(ar)):
        if len(given) >= len(ar[i]):
            if given[-len(ar[i]):] == ar[i]:
                for y in range(i + 1,len(ar)):
                    directory = directory + '\\' + ar[y]
                fd1 = True
                break

    if fd1 == False:
        for i in range(0,len(ar)):
            if ar[i] in os.listdir(given):
                for y in range(i,len(ar)):
                    directory = directory + '\\' + ar[y]
                fd2 = True
                break

    tmp = []
    fldrs = os.listdir(directory)
    for i in range(len(fldrs)):
        if name in fldrs[i].lower() and os.path.isdir(directory+'\\'+fldrs[i]):
            if 'message_1.'+mode in os.listdir(directory + '\\' + fldrs[i]):
                os.chdir(directory + '\\' + fldrs[i])
                with open('message_1.'+mode) as f:
                    if mode == 'json':
                        filedata = json.load(f)
                        content = filedata.get('thread_type')
                        if content == 'Regular':
                            tmp.append(fldrs[i])
                    else:
                        tmp.append(fldrs[i])

    mx = 0
    id = 0
    if len(tmp) > 1:
        mx = len(os.listdir(directory + '\\' + tmp[0]))
        for i in range(1,len(tmp)):
            if len(os.listdir(directory + '\\' + tmp[i])) > mx:
                id = i
                mx = len(os.listdir(directory + '\\' + tmp[i]))
        directory = directory + '\\' + tmp[id]
    elif len(tmp) == 1:
        directory = directory + '\\' + tmp[0]
    else:
        raise Exception("E1")

    fileN = 0
    listdir = os.listdir(directory)
    for i in range(0, len(listdir)):
        if 'message' in listdir[i]:
            fileN = fileN + 1

    return directory

def connectGaps():
    hourBuckets[0].append(hourBuckets[0][0])
    hourBuckets[1].append(hourBuckets[1][0])
    hourBuckets[2].append(hourBuckets[2][0])
    hourBuckets[3].append(hourBuckets[3][0])
    weekdayBuckets[0].append(weekdayBuckets[0][0])
    weekdayBuckets[1].append(weekdayBuckets[1][0])
    weekdayBuckets[2].append(weekdayBuckets[2][0])
    weekdayBuckets[3].append(weekdayBuckets[3][0])

def readCounters():
    global mc
    global mcw
    global tmpa
    global maxval
    global counter

    tmpa = counter[2].most_common(wordn)

    mcw = [[],[]]
    mc = [[[],[]],[[],[]]]
    for i in range(0, len(tmpa)):
        mcw[0].insert(0, tmpa[i][0].upper())
        mcw[1].insert(0, tmpa[i][1])
        mc[0][0].insert(0, tmpa[i][0])
        mc[0][1].insert(0, counter[0][tmpa[i][0]])
        mc[1][0].insert(0, tmpa[i][0])
        mc[1][1].insert(0, counter[1][tmpa[i][0]])

    if len(tmpa) >= 1:
        maxval = int(np.max([np.max(mc[0][1]),np.max(mc[1][1])]))
    else:
        maxval = 1

    for i in range(0, len(tmpa)):
        mc[0][1][i] = mc[0][1][i] * -1

def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier

def calcTicks(v,tn):
    e = 0
    f = 0

    while True:
        if v / pow(10,e) < 1:
            n = e
            break
        e = e + 1

    if n > 2:
        vn = round_down(v,-n + 2)
    elif n == 2:
        vn = round_down(v,-n + 1)
    elif n == 1:
        vn = v

    if n <= 2:
        return [-vn,0,vn]
    if n >= 3:
        return [-vn,-vn / 2,0,vn / 2,vn]

def dateFormat(date):
    m = date.split(' ')[0]
    for i in range(0,12):
        if m.lower() in months[i].lower():
            if i+1 >= 10:
                mth = str(i+1)
            else:
                mth = '0' + str(i+1)
             
             
    r = date.split(' ')[2] + '-' + mth + '-' + date.split(' ')[1] + ' ' + date.split(' ')[3]
    r = r.replace(',','')
    #print(r)
    return r

def dateFormatJSON(ms):
    return datetime.fromtimestamp(ms / 1000.0)

def clearCounters():
    a = string.ascii_lowercase.join("0123456789")
    for i in range(0,len(stopwords)):
        del counter[0][stopwords[i]]
        del counter[1][stopwords[i]]
        del counter[2][stopwords[i]]
    for i in range(0,len(a)):
        del counter[0][a[i]]
        del counter[1][a[i]]
        del counter[2][a[i]]

def readDataHTML():
    global days
    global weekdayBuckets
    global mptc
    global tptc
    global targetdir
    
    os.chdir(targetdir)

    for i in range(1,fileN + 1):
        f = open("message_" + str(i) + ".html", "r", encoding='utf8')

        if f.mode == 'r':

            soup = BeautifulSoup(f.read(), "html.parser")

            content = soup.find_all('div', attrs={"class": "pam _3-95 _2pi0 _2lej uiBoxWhite noborder"})

            cnt = 0

            #counttime = 0
            for msg in content:
                
                cnt = cnt + 1
                if (len(content) == cnt) and (i == fileN):
                    continue

                msg = msg.contents

                if msg[1].find('ul') and msg[1].find('li'):
                    msg[1].find('ul').clear()


                Messenger = msg[0].text
                Message = msg[1].text.strip()
                Date = dateFormat(msg[2].text)


                if len(chatters) == 0:
                    chatters.append(Messenger)
                    m = 0
                elif len(chatters) == 1:
                    if chatters[0] != Messenger:
                        chatters.append(Messenger)
                        m = 1
                    else:
                        m = 0
                else:
                    if Messenger == chatters[0]:
                        m = 0
                    else:
                        m = 1



                if msg[1].find('video'):
                    Message = ""
                elif msg[1].find('img'):
                    Message = ""
                elif msg[1].find('a') or ".com" in Message or "www." in Message or 'http' in Message:
                    Message = ""
                elif any(item in Message for item in messexclusions):
                    Message = ""
                
                if Message == '':
                    mptc = mptc + 1
                tptc = tptc + 1

                Message = normalize(Message)

                text = re.findall(r"[\w']+", Message)

                if trimming:
                    for x in range(0,len(text)):
                        text[x] = trim(text[x])

                counter[m].update(text)
                counter[2].update(text)
                #counttime = counttime + (time4 - time3)

                date = dt(int(Date.split(' ')[0].split('-')[0]),int(Date.split(' ')[0].split('-')[1]),int(Date.split(' ')[0].split('-')[2]))
                datenum = date.toordinal()
                wkday = date.weekday()


                data[0].insert(0,Messenger)
                data[1].insert(0,datenum)
                data[2].insert(0,int(Date.split(' ')[1][0:2].replace(':','')))
                data[3].insert(0,text)
                data[4].insert(0,len(text))
                data[5].insert(0,wkday)
                data[6].insert(0,date)
                
                totalcount[m * 2] = totalcount[m * 2] + 1
                totalcount[1 + (m * 2)] = totalcount[1 + (m * 2)] + len(text)
                totalcount[4] = totalcount[4] + 1
                totalcount[5] = totalcount[5] + len(text)
                
                weekdayBuckets[m * 2][wkday] = weekdayBuckets[m * 2][wkday] + 1
                weekdayBuckets[1 + (m * 2)][wkday] = weekdayBuckets[1 + (m * 2)][wkday] + len(text)
                weekdayBuckets[4][wkday] = weekdayBuckets[4][wkday] + 1
                weekdayBuckets[5][wkday] = weekdayBuckets[5][wkday] + len(text)
        
            f.close()
        else:
            os.write(1, bytes('readfile error\n', 'utf-8'))
            
    clearCounters()
    days = int(data[1][-1] - data[1][0] + 1)

def readDataJSON():
    global days
    global mptc
    global tptc
    global targetdir
    global fileN

    done = False
    
    os.chdir(targetdir)
    for i in range(1,fileN + 1):
        
        with open('message_' + str(i) + '.json') as f:

            filedata = json.load(f)

            content = filedata.get('messages')

            if len(chatters) == 0:
                chatters.append(filedata.get('participants')[0].get('name').encode('raw_unicode_escape').decode('utf8'))
                chatters.append(filedata.get('participants')[1].get('name').encode('raw_unicode_escape').decode('utf8'))
            
            cnt = 0
            for msg in content:

                cnt = cnt + 1
                if (len(content) == cnt) and (i == fileN):
                    continue

                Messenger = msg.get('sender_name').encode('raw_unicode_escape').decode('utf8')
                if 'content' in msg:
                    Message = msg.get('content').encode('raw_unicode_escape').decode('utf8')
                else:
                    Message = ''
                Date = dateFormatJSON(msg.get('timestamp_ms'))
                Type = msg.get('type')

                if Messenger == chatters[0]:
                    m = 0
                else:
                    m = 1
                
                if Type != 'Generic':
                    continue

                if any(item in Message for item in messexclusions):
                    Message = ""

                if Message == '':
                    mptc = mptc + 1
                tptc = tptc + 1


                Message = normalize(Message)


                text = re.findall(r"[\w']+", Message)

                if trimming:
                    for x in range(0,len(text)):
                        text[x] = trim(text[x])

                counter[m].update(text)
                counter[2].update(text)
                    
                datenum = Date.toordinal()
                wkday = Date.weekday()
                
                data[0].insert(0,Messenger)
                data[1].insert(0,datenum)
                data[2].insert(0,Date.hour)
                data[3].insert(0,text)
                data[4].insert(0,len(text))
                data[5].insert(0,wkday)
                data[6].insert(0,Date)
                
                totalcount[m * 2] = totalcount[m * 2] + 1
                totalcount[1 + (m * 2)] = totalcount[1 + (m * 2)] + len(text)
                totalcount[4] = totalcount[4] + 1
                totalcount[5] = totalcount[5] + len(text)
                
                weekdayBuckets[m * 2][wkday] = weekdayBuckets[m * 2][wkday] + 1
                weekdayBuckets[1 + (m * 2)][wkday] = weekdayBuckets[1 + (m * 2)][wkday] + len(text)
                weekdayBuckets[4][wkday] = weekdayBuckets[4][wkday] + 1
                weekdayBuckets[5][wkday] = weekdayBuckets[5][wkday] + len(text)
                

    days = int(data[1][-1] - data[1][0] + 1)

    clearCounters()

def subdiv(inv,n):
    global days
    global datesD
    global dateBuckets

    base = int(data[1][0])
    
    hB = [[],[],[],[],[],[]]
    wB = [[],[],[],[],[],[]]
    cB = [collections.Counter(),collections.Counter(),collections.Counter()]
    tB = [0,0,0,0,0,0]

    for i in range(0,24):
        hB[0].append(0)
        hB[1].append(0)
        hB[2].append(0)
        hB[3].append(0)
        hB[4].append(0)
        hB[5].append(0)
        
    for i in range(0,6):
        for x in range(0,7):
            wB[i].append(0)

    interval = inv

    messcount = 0
    wordcount = 0
    mcount = []
    wcount = []
    x = 0
    y = 0
    brk = False
    
    for i in range(0,2):
        mcount.append(0)
        wcount.append(0)

    for i in range(0,int(days / interval) + 2):
        
        dateBuckets[n][0].append(base + (interval * i))
        dateBuckets[n][5].append(dt.fromordinal(base + ((interval * i) + (int(interval / 2)))))
        linepBuckets[n][0].append(base + (interval * i))
        linepBuckets[n][7].append(dt.fromordinal(base + ((interval * i) + (int(interval / 2)))))


        while True:
            if x + y == len(data[1]):
                brk = True
                break
            
            if data[0][x + y] == chatters[0]:
                m = 0
            else:
                m = 1

            if data[1][x + y] >= dateBuckets[n][0][-1] + interval:
                break
            else:
                messcount = messcount + 1

                indx = x + y

                wkday = data[5][indx]

                cB[m].update(data[3][indx])
                cB[2].update(data[3][indx])

                wB[m * 2][wkday] = wB[m * 2][wkday] + 1
                wB[1 + (m * 2)][wkday] = wB[1 + (m * 2)][wkday] + data[4][indx]
                wB[4][wkday] = wB[4][wkday] + 1
                wB[5][wkday] = wB[5][wkday] + data[4][indx]

                hB[(m * 2)][data[2][indx]] = hB[(m * 2)][data[2][indx]] + 1
                hB[1 + (m * 2)][data[2][indx]] = hB[1 + (m * 2)][data[2][indx]] + data[4][indx]
                hB[4][data[2][indx]] = hB[4][data[2][indx]] + 1
                hB[5][data[2][indx]] = hB[5][data[2][indx]] + data[4][indx]
        
                tB[m * 2] = tB[m * 2] + 1
                tB[1 + (m * 2)] = tB[1 + (m * 2)] + data[4][indx]
                tB[4] = tB[4] + 1
                tB[5] = tB[5] + data[4][indx]

            x = x + 1

        dateBuckets[n][1].append(hB)
        dateBuckets[n][2].append(wB)
        dateBuckets[n][3].append(tB)
        dateBuckets[n][4].append(cB)

        linepBuckets[n][1].append(tB[0])
        linepBuckets[n][2].append(tB[1])
        linepBuckets[n][3].append(tB[2])
        linepBuckets[n][4].append(tB[3])
        linepBuckets[n][5].append(tB[4])
        linepBuckets[n][6].append(tB[5])


        hB = [[],[],[],[],[],[]]
        wB = [[],[],[],[],[],[]]
        cB = [collections.Counter(),collections.Counter(),collections.Counter()]
        tB = [0,0,0,0,0,0]

        for i in range(0,24):
            hB[0].append(0)
            hB[1].append(0)
            hB[2].append(0)
            hB[3].append(0)
            hB[4].append(0)
            hB[5].append(0)
        
        for i in range(0,6):
            for x in range(0,7):
                wB[i].append(0)

        x = 0
        y = y + messcount
        
        messcount = 0
        
        if brk == True:
            break

def setValuesN(d1,d2,n,mm):
    global days
    global weekdayBuckets
    global hourBuckets
    global chatters
    global totalcount
    global counter
    global data
    
    base = int(data[1][0])
    if n == len(dateBuckets) - 1:
        x1 = d1 - base
        x2 = d2 - base

        if x1 < 0:
            x1 = 0
        if x2 >= len(dateBuckets[n][0]):
            x2 = len(dateBuckets[n][0]) - 1
    else:
        x = 0
        while True:
            if x >= len(dateBuckets[n][0]):
                x1 = x - 1
                break
            if dateBuckets[n][0][x] >= d1:
                x1 = x
                break
            x = x + 1
        x = x1
        while True:
            if x >= len(dateBuckets[n][0]):
                x2 = x - 1
                break
            if dateBuckets[n][0][x] >= d2:
                x2 = x
                break
            x = x + 1

    w = []
    h = []
    t = []
    c = [collections.Counter(),collections.Counter(),collections.Counter()]

    for i in range(0,6):
        w.append([])
        h.append([])
        t.append(0)
        for y in range(0,7):
            w[i].append(0)
        for y in range(0,24):
            h[i].append(0)
 
    for i in range(x1,x2 + 1):

        for y in range(0,4):
            t[y] = t[y] + dateBuckets[n][3][i][y]
        w[mm] = [x + y for x, y in zip(w[mm], dateBuckets[n][2][i][mm])]
        h[mm] = [x + y for x, y in zip(h[mm], dateBuckets[n][1][i][mm])]
        w[mm + 2] = [x + y for x, y in zip(w[mm + 2], dateBuckets[n][2][i][mm + 2])]
        h[mm + 2] = [x + y for x, y in zip(h[mm + 2], dateBuckets[n][1][i][mm + 2])]

        for y in range(0,3):
            c[y] = c[y] + dateBuckets[n][4][i][y]

    weekdayBuckets = w
    hourBuckets = h
    totalcount = t
    counter = c
    
    connectGaps()
    clearCounters()
    readCounters()
   
def importLang():
    global trimexclusions
    global stopwords
    global messexclusions
    os.chdir(maindir)
    if 'lang' in os.listdir():
        os.chdir(maindir+'\\lang')
        if lang + '.txt' in os.listdir(maindir+'\\lang'):
            f = open(lang + '.txt', encoding='utf8')
        else:
            os.write(1, bytes('E2', 'utf-8'))
    else:
        os.write(1, bytes('E3', 'utf-8'))

    if f.mode == 'r':
        while True:
            line = f.readline()
            if not line:
                break
            stopwords.append(line.strip())
    else:
        os.write(1, bytes('E4', 'utf-8'))
        
    os.chdir(maindir+'\\lang')
    f = open('messexclusions.txt', encoding='utf8')
    if f.mode == 'r':

        while True:
            line = f.readline()
            if not line:
                break
            messexclusions.append(line.replace('\n',''))
    else:
        os.write(1, bytes('E5', 'utf-8'))


    f = open('trimexclusions.txt', encoding='utf8')
    if f.mode == 'r':

        while True:
            line = f.readline()
            if not line:
                break
            trimexclusions.append(line.replace('\n',''))
    else:
        os.write(1, bytes('E6', 'utf-8'))

    f = open(lang + 'm.txt',encoding='utf8')
    if f.mode == 'r':
        for i in range(0,12):
            line = f.readline()
            if not line:
                break
            months.append(line.replace('\n',''))
    else:
        os.write(1, bytes('E6', 'utf-8'))

def prepareArrays(d,r,n):
    global l
    intervals = []
    i0 = round(d / r)

    while True:
        if n == 1:
            break
        if i0 / (n - 1) < 1:
            n = n - 1
        else:
            break
        
    #if n is 1 then res to high
    if n == 1:
        os.write(1, bytes('E7', 'utf-8'))

    iN = (d / r) / (n - 1)
    intervals.append(i0)
    for i in range(1,n):
        if i == n - 1:
            if intervals[-1] != 1:
                intervals.append(1)
            break
        if intervals[-1] != round(iN * ((n - 1) - i)):
            intervals.append(round(iN * ((n - 1) - i)))


    for i in range(0,len(intervals)):
        subdiv(intervals[i],i)
    l = len(intervals)
    return intervals

os.write(1, bytes('searching conversation...\n', 'utf-8'))

targetdir = scandir(name,given)

os.write(1, bytes('reading language file...\n', 'utf-8'))

importLang()

os.write(1, bytes('reading messages...\n', 'utf-8'))

if mode == 'html':
    readDataHTML()
elif mode == 'json':   
    readDataJSON()

intervals = prepareArrays(days,res,l)

os.write(1, bytes('preparing data...\n', 'utf-8'))

def getPlots(mm):
    wordAxisText = [np.asarray(mc[0][1]),np.asarray(mcw[0])]
    arrV = calcTicks(maxval,6)
    arrT = [str(int(abs(x))) for x in arrV]

    pieM = go.Pie(values=[totalcount[0],totalcount[2]],
            labels=[chatters[0].split()[0],chatters[1].split()[0]],
            hole=0.4,
            pull=0.01,
            hovertemplate =
            '%{label} %{percent}' + '<br>%{value} messages</br><extra></extra>',
            marker = dict(colors=chattercolor),
            domain=dict(x=[0.77,0.965],y=[0.075,0.375]),
            rotation=90,
            textfont=dict(family='Roboto'))
    pieW = go.Pie(values=[totalcount[1],totalcount[3]],
            labels=[chatters[0].split()[0],chatters[1].split()[0]],
            hole=0.4,
            pull=0.01,
            hovertemplate =
            '%{label} %{percent}' + '<br>%{value} words</br><extra></extra>',
            marker = dict(colors=chattercolor),
            domain=dict(x=[0.77,0.965],y=[0.575,0.875]),
            rotation=90,
            textfont=dict(family='Roboto'))
    

    polH1 = go.Scatterpolar(cliponaxis=True,
        connectgaps=True,
        subplot='polar1',
        hoveron="points",
        name=chatters[0].split(' ')[0],
        r=hourBuckets[mm], 
        theta=hours,
        hovertemplate =
        chatters[0].split(' ')[0] + '<br>' + dictionary[mm] + ': %{r}</br>' + 'Hour: %{theta}<extra></extra>',
        fill='toself',
        line=dict(color=chattercolor[0]))

    polH2 = go.Scatterpolar(cliponaxis=True,
        connectgaps=True,
        subplot='polar1',
        hoveron="points",
        r=hourBuckets[mm + 2], 
        theta=hours,
        hovertemplate =
        chatters[1].split(' ')[0] + '<br>' + dictionary[mm] + ': %{r}</br>' + 'Hour: %{theta}<extra></extra>',
        fill='toself',
        customdata = ['1:23pm'],
        line=dict(color=chattercolor[1]))

    polW1 = go.Scatterpolar(cliponaxis=True,
        connectgaps=True,
        subplot='polar2',
        hoveron="points",
        name=chatters[0],
        r=weekdayBuckets[mm], 
        theta=weekdays,
        hovertemplate =
        chatters[0].split(' ')[0] + '<br>' + dictionary[mm] + ': %{r}</br>' + 'Day: %{theta}<extra></extra>',
        fill='toself',
        line=dict(color=chattercolor[0]))

    polW2 = go.Scatterpolar(cliponaxis=True,
        connectgaps=True,
        subplot='polar2',
        hoveron="points",
        name=chatters[1],
        r=weekdayBuckets[mm + 2], 
        theta=weekdays,
        hovertemplate =
        chatters[1].split(' ')[0] + '<br>' + dictionary[mm] + ': %{r}</br>' + 'Day: %{theta}<extra></extra>',
        fill='toself',
        line=dict(color=chattercolor[1]))

    barL = go.Bar(y=mcw[0],
        x=mc[0][1],
        xaxis='x2',
        yaxis='y2',
        orientation='h',
        text= -1 * wordAxisText[0].astype('int'),
        hovertemplate =
        chatters[0].split(' ')[0] + '<br>Word: %{y}</br>' + 'Count: %{text}<extra></extra>',
        marker=dict(color=chattercolor[0]))

    barR = go.Bar(y=mcw[0],
        x=mc[1][1],
        orientation='h',
        xaxis='x2',
        yaxis='y2',
        text= wordAxisText[1].astype(str),
        textposition='outside',
        texttemplate=' %{y}',
        hovertemplate =
        chatters[1].split(' ')[0] + '<br>Word: %{y}</br>' + 'Count: %{x}<extra></extra>',
        textfont=dict(family = 'Open Sans, light'),
        marker=dict(color=chattercolor[1]))
    

    layout = go.Layout(autosize=True,
        margin=dict(t=0,b=0,l=0,r=0,pad=0),
        template='plotly_dark',
        polar1=dict(domain=dict(x=[0.035,0.23],y=[0.075,0.375]),
            radialaxis=dict(visible=True,
               showticklabels=False,
               showline=False,
               angle=45,
               tickangle=45,
               tickmode='auto',
               nticks=4,
               tickfont=dict(size=10,
                   family='Roboto')),
            angularaxis=dict(rotation=90,
               direction='clockwise',
               type='category',
               tickfont=dict(family='Roboto'))),

        polar2=dict(domain=dict(x=[0.035,0.23],y=[0.575,0.875]),
            
            radialaxis=dict(visible=True,
               showticklabels=False,
               showline=False,
               angle=45,
               tickangle=45,
               tickmode='auto',
               nticks=5,
               tickfont=dict(size=8,
                   family='Roboto')),
            angularaxis=dict(rotation=90,
               direction='clockwise',
               type='category',
               tickfont=dict(family='Roboto'))),
        
        xaxis2=dict(domain=[0.25,0.75],
            tickfont=dict(family='Roboto'),
            position=0,
            anchor = 'free',
            range=[-maxval * 1.1,maxval * 1.1],
            uirevision='n',
            tickvals=arrV,
            ticktext=arrT,
            nticks=6),
        yaxis2=dict(domain=[0,0.93],
            tickfont=dict(family='Roboto'),
            showticklabels = False,
            type='category'),

        showlegend=False,
        barmode='overlay',
        transition = {'duration': 500, 'ordering': "traces first"}
        ,
        annotations=[
                dict(text=dictionary[mm] + '<br>per weekday',
                showarrow=False,
                font=dict(size=35),
                xref="paper",
                yref="paper",
                xanchor = 'center',
                x=0.1328,
                y=1,
                height=100,
                width=250,
                align='center'
                ),
                dict(text=dictionary[mm] + '<br>per hour',
                showarrow=False,
                font=dict(size=35),
                xref="paper",
                yref="paper",
                xanchor = 'center',
                x=0.1328,
                y=0.45,
                height=500,
                width=250,
                align='center'
                ),
                dict(
                text='Most used words',
                showarrow=False,
                font=dict(size=40),
                xref="paper",
                yref="paper",
                xanchor = 'center',
                x=0.5,
                y=1,
                width=400),
                dict(text='Words<br>per person',
                showarrow=False,
                font=dict(size=35),
                xref="paper",
                yref="paper",
                xanchor = 'center',
                x=0.8672,
                y=1,
                height=100,
                width=250,
                align='center'
                ),
                dict(text='Messages<br>per person',
                showarrow=False,
                font=dict(size=35),
                xref="paper",
                yref="paper",
                xanchor = 'center',
                x=0.8672,
                y=0.45,
                height=500,
                width=250,
                align='center'
                )
                ])
    
    if totalcount[mm] >= totalcount[mm + 2]:
        data = [pieM,pieW,polH1,polH2,polW1,polW2,barL,barR]    
    else:
        data = [pieM,pieW,polH2,polH1,polW2,polW1,barL,barR]   
     
    fig = go.Figure(data=data,layout=layout)
    return fig

def getLineP(n,mm):
    
    
    line1 = go.Scatter(x=linepBuckets[n][7],
        y=linepBuckets[n][mm + 1],

        xaxis='x1',
        yaxis='y1',
        name=chatters[0],
        hovertemplate =
        chatters[0].split(' ')[0] + '<br>' + dictionary[mm] + ': %{y}</br>' + '%{x}<extra></extra>',
        line=dict(color=chattercolor[0], 
            width=2))

    line2 = go.Scatter(x=linepBuckets[n][7],
        y=linepBuckets[n][mm + 3],

        xaxis='x1',
        yaxis='y1',
        name=chatters[1],
        hovertemplate =
        chatters[1].split(' ')[0] + '<br>' + dictionary[mm] + ': %{y}</br>' + '%{x}<extra></extra>',
        line=dict(color=chattercolor[1], 
            width=2))


    layout = go.Layout(autosize=True,
        margin=dict(t=0,b=0,pad=0),
        template='plotly_dark',

        xaxis1=dict(domain=[0,1],
            tickfont=dict(family='Roboto'),
            uirevision='n',
            showgrid=False),
        yaxis1=dict(domain=[0,0.9],
            tickfont=dict(family='Roboto'),
            nticks=3,
            type='linear'),

        showlegend=False,
        barmode='overlay'
        )
    
    if totalcount[mm] >= totalcount[mm + 2]:
        data = [line1,line2]    
    else:
        data = [line2,line1]   
     
    fig = go.Figure(data=data,layout=layout)
    return fig

os.write(1, bytes('preparing plots...\n', 'utf-8'))

basePlot = []
setValuesN(dateBuckets[0][0][0],dateBuckets[0][0][-1],0,0)
basePlot.append(getPlots(0))
setValuesN(dateBuckets[0][0][0],dateBuckets[0][0][-1],0,1)
basePlot.append(getPlots(1))

last = [0,dateBuckets[0][0][0] - 1,dateBuckets[0][0][-1]]

figs = [[],[]]
for i in range(0,l):
    figs[0].append(getLineP(i,0))
    figs[1].append(getLineP(i,1))

os.chdir(maindir)

zoom = [0,len(linepBuckets[0][messmode]) - 1]

app = dash.Dash(__name__)

app.config['suppress_callback_exceptions'] = False

if messmode == 0:
    tpl = [1,0]
else:
    tpl = [0,1]

app.title = "HReader"

app.layout = html.Div([html.Link(href="https://fonts.googleapis.com/css?family=Roboto:500&display=swap", rel="stylesheet"),
    html.Link(href="https://fonts.googleapis.com/css?family=Spartan&display=swap", rel="stylesheet"),
    html.Link(href="https://fonts.googleapis.com/css?family=Source+Sans+Pro&display=swap", rel="stylesheet"),
    html.Link(href="https://fonts.googleapis.com/css?family=Open+Sans:300,400&display=swap", rel="stylesheet"),

    html.Div([html.Div([html.H2('Showing:', className="B4")]),
    html.Div([html.Button('Messages', id='btn-nclicks-m', n_clicks=tpl[0], className="B1", style={'background-color':chattercolor[1],'border-color':chattercolor[0],'color':textcolor})],style={'float':'left','position':'relative'}),
    html.Div([html.Button('Words', id='btn-nclicks-w', n_clicks=tpl[1], className="B2", style={'background-color':chattercolor[1],'border-color':chattercolor[0],'color':textcolor})], style={'float':'left','position':'relative'}),
    html.Div([html.Div(chatters[0] + ' & ' + chatters[1], className="B3")])], style={'text-align':'center', 'margin':'0px', 'background-color':'#111111', 'height':'8vh', 'font':'Roboto', 'position':'relative'}, className='D1'),

    dcc.Graph(id='line-graph',
        figure=figs[messmode][0],
        style=dict(height='50vh')),

    html.Div(style={'width':'50vw','height':'3.5vh',}),

    dcc.Graph(id='o-graph',
        figure=basePlot[messmode],
        style=dict(height='125vh')),

    html.Div(style={'width':'50vw','height':'3.5vh',}),
    
    
    ],style={'padding': '0px 0px 0px 0px', 'background-color':'#111111', 'margin':'0px'})

@app.callback(Output('line-graph', 'figure'),
              [Input('line-graph', 'relayoutData'),
               Input('btn-nclicks-m', 'n_clicks'),
               Input('btn-nclicks-w', 'n_clicks')])
def update_graph_live(relayoutData, btn1, btn2):
    global last
    global figs
    global days
    global dateBuckets
    global i1
    global intervals
    global res
    global messmode
    global lastbtnV
    global zoom

    if btn1 == 0 and btn2 == 0:
        return figs[messmode][last[0]]

    if btn1 != lastbtnV[0][0]:
        messmode = 0
        lastbtnV[0] = [btn1,btn2]

        n = last[0]
        minv = int(np.amin([int(np.amin(linepBuckets[n][messmode + 1][zoom[0]:zoom[1]])),int(np.amin(linepBuckets[n][messmode + 3][zoom[0]:zoom[1]]))]))
        maxv = int(np.amax([int(np.amax(linepBuckets[n][messmode + 1][zoom[0]:zoom[1]])),int(np.amax(linepBuckets[n][messmode + 3][zoom[0]:zoom[1]]))]))

        minv = int(round(minv / 1.5))
        maxv = int(round(maxv / 0.9))

        if maxv + minv != 0:
            if minv / (maxv + minv) < 0.1: minv = 0
        else:
            minv = 0
            maxv = 1


        pt = figs[messmode][n]
            
        pt['layout']['yaxis']['range'] = [minv,maxv]

        return pt
    if btn2 != lastbtnV[0][1]:
        messmode = 1
        lastbtnV[0] = [btn1,btn2]

        n = last[0]
        minv = int(np.amin([int(np.amin(linepBuckets[n][messmode + 1][zoom[0]:zoom[1]])),int(np.amin(linepBuckets[n][messmode + 3][zoom[0]:zoom[1]]))]))
        maxv = int(np.amax([int(np.amax(linepBuckets[n][messmode + 1][zoom[0]:zoom[1]])),int(np.amax(linepBuckets[n][messmode + 3][zoom[0]:zoom[1]]))]))

        minv = int(round(minv / 1.5))
        maxv = int(round(maxv / 0.9))

        if maxv + minv != 0:
            if minv / (maxv + minv) < 0.1: minv = 0
        else:
            minv = 0
            maxv = 1

        pt = figs[messmode][n]
            
        pt['layout']['yaxis']['range'] = [minv,maxv]

        return pt

    l = len(intervals)

    mm = messmode

    if relayoutData != None:

        if 'xaxis.range[0]' in relayoutData:
            d1 = datetime.strptime(relayoutData.get('xaxis.range[0]').split(' ')[0],'%Y-%m-%d').toordinal() + 1
            d2 = datetime.strptime(relayoutData.get('xaxis.range[1]').split(' ')[0],'%Y-%m-%d').toordinal()

            d = d2 - d1 + 1

            s = d / res
            n = 0
            df = abs(s - intervals[0])
            for i in range(1,l):
                if abs(s - intervals[i]) < df:
                    n = i
                    df = abs(s - intervals[i])

            if n == l - 1:
                x1 = d1 - int(linepBuckets[n][0][0]) 
                x2 = d2 - int(linepBuckets[n][0][0]) + 1
                if x1 < 0: x1 = 0
                if x2 < 0: x2 = 0

                zoom = [x1,x2]

                minv = int(np.amin([int(np.amin(linepBuckets[n][mm + 1][x1:x2])),int(np.amin(linepBuckets[n][mm + 3][x1:x2]))]))
                maxv = int(np.amax([int(np.amax(linepBuckets[n][mm + 1][x1:x2])),int(np.amax(linepBuckets[n][mm + 3][x1:x2]))]))

                minv = int(round(minv / 1.5))
                maxv = int(round(maxv / 0.9))

                if maxv + minv != 0:
                    if minv / (maxv + minv) < 0.1: minv = 0
                else:
                    minv = 0
                    maxv = 1

            else:
                x1 = int((d1 - linepBuckets[n][0][0]) / intervals[n])
                x2 = int((d2 - linepBuckets[n][0][0]) / intervals[n])
                if x1 < 0: x1 = 0
                if x2 < 0: x2 = 0
                    
                zoom = [x1,x2]

                minv = int(np.amin([int(np.amin(linepBuckets[n][mm + 1][x1:x2])),int(np.amin(linepBuckets[n][mm + 3][x1:x2]))]))
                maxv = int(np.amax([int(np.amax(linepBuckets[n][mm + 1][x1:x2])),int(np.amax(linepBuckets[n][mm + 3][x1:x2]))]))
                    
                minv = int(round(minv / 1.5))
                maxv = int(round(maxv / 0.9))

                if maxv + minv != 0:
                    if minv / (maxv + minv) < 0.1: minv = 0
                else:
                    minv = 0
                    maxv = 1



            pt = figs[mm][n]
            
            pt['layout']['yaxis']['range'] = [minv,maxv]

            last[0] = n

            
            return pt
        elif 'autosize' in relayoutData or 'xaxis.autorange' in relayoutData:
            last[0] = 0
            zoom = [0,len(linepBuckets[0][mm]) - 1]
            return figs[mm][0]
        else:
            raise PreventUpdate
    else:
        raise PreventUpdate


@app.callback(Output('o-graph', 'figure'),
              [Input('line-graph', 'relayoutData'),
               Input('btn-nclicks-m', 'n_clicks'),
               Input('btn-nclicks-w', 'n_clicks')])
def update_graph_live(relayoutData, btn1, btn2):
    global orderedData
    global messmode
    global last
    global lastbtnV

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if btn1 == 0 and btn2 == 0:
        setValuesN(last[1],last[2],last[0],messmode)
        
        lastbtnV[1] = [btn1,btn2]
        return getPlots(messmode)

    if btn1 != lastbtnV[1][0]:
        setValuesN(last[1],last[2],last[0],0)
        lastbtnV[1] = [btn1,btn2]
        return getPlots(0)
    if btn2 != lastbtnV[1][1]:
        setValuesN(last[1],last[2],last[0],1)
        lastbtnV[1] = [btn1,btn2]
        return getPlots(1)

    mm = messmode

    if relayoutData != None:

        if 'xaxis.range[0]' in relayoutData:
            d1 = datetime.strptime(relayoutData.get('xaxis.range[0]').split(' ')[0],'%Y-%m-%d').toordinal() + 1
            d2 = datetime.strptime(relayoutData.get('xaxis.range[1]').split(' ')[0],'%Y-%m-%d').toordinal()
            
            d = d2 - d1 + 1

            last[1] = d1
            last[2] = d2

            s = d / res
            n = 0
            df = abs(s - intervals[0])
            for i in range(1,l):
                if abs(s - intervals[i]) < df:
                    n = i
                    df = abs(s - intervals[i])

            setValuesN(d1,d2,n,mm)
            
            return getPlots(mm)
        elif 'autosize' in relayoutData or 'xaxis.autorange' in relayoutData:
            last = [0,dateBuckets[0][0][0],dateBuckets[0][0][-1]]
            return basePlot[mm]
        else:
            raise PreventUpdate
    else:
        raise PreventUpdate

os.write(1, bytes('statring dashboard...\n', 'utf-8'))

if __name__ == '__main__':
    app.run_server(debug=False)