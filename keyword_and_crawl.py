# -*- coding:utf-8 -*-
import collections
from bs4 import BeautifulSoup
import urllib.request
import requests
from konlpy.tag import Twitter
import re
collections.namedtuple("a", "b")
FILE_NAME_1 = 'href.txt'
FILE_NAME_2 = 'a.txt'
FILE_NAME_3 = 'keyword.txt'
def crawler_href (eve):
    if eve == "all":                    #종합
        event = "nclicks(rig.rankpol)"
    elif eve == "pol":                 #정치
        event = "nclicks(rig.rankpol)"
    elif eve == "eco":                 #경제
        event = "nclicks(rig.rankeco)"
    elif eve == "soc":                 #사회
        event = "nclicks(rig.ranksoc)"
    elif eve == "lif":                 #생활/문화
        event = "nclicks(rig.ranklif)"
    elif eve == "wor":                 #세계
        event = "nclicks(rig.rankwor)"
    elif eve == "sci":                 #IT/과학
        event = "nclicks(rig.ranksci)"
    elif eve == "ent":                 #TV연예
        event = "nclicks(rig.rankent)"
    elif eve == "spo":                 #스포츠
        event = "nclicks(rig.rankspo)"
    with open(FILE_NAME_1, 'w') as fh:
        req = urllib.request.Request("http://news.naver.com/main/ranking/popularDay.nhn?mid=etc&sid1=111")                #구글 : https://news.google.com/news/?ned=kr&gl=KR&hl=ko
        data = urllib.request.urlopen(req).read()
        bs = BeautifulSoup(data, 'html.parser')
        l = bs.find_all('a')
        idx = 0
        for s in l:
            prop = s.get('class')	# get class property
            if prop != None and prop[0] == event: # if class property exist, check icon_pic_n
                                #google news class == "nuEeue hzdq5d ME7ew"
                fh.write("http://news.naver.com/"+s.get('href')+'\n')
def refine (text):
    text = re.sub('[/]', '', text)
    text = re.sub('flash 오류를 우회하기 위한 함수 추가', '', text)
    text = re.sub('function _flash_removeCallback', '', text)
    text = re.sub('\[[^1]*\]', '', text)
    text = re.sub('\([^1]*\)', '', text)
    text = re.sub('\{[^1]*\}', '', text)
    return text
def crawler_a ():                   #모아놓은 href에 들어가 본문 가져오기
    with open(FILE_NAME_2, 'w') as fh_2:
        fh_2.write("")
    with open(FILE_NAME_1, 'r') as fh_1:        #href 들어가기 위해
        with open(FILE_NAME_2, mode='a+', encoding='utf8') as fh_2:     #a를 모으기 위해
            for line in fh_1:                   #href.txt를 각 줄마다
                req = requests.get(line.strip('\n'));       #href에 들어가
                #print(line.strip('\n'))   #확인용
                html = req.text
                soup = BeautifulSoup(html, 'html.parser')
                my_titles = soup.select('#articleBodyContents') #본문 selector 설정후
                #time.sleep(1)
                for title in my_titles:         #본문 수집
                    #print(title.text)   #확인용
                    fh_2.write(title.text + '\n')

def get_tags(text, ntags=50):                   #for extrating keyword
    spliter = Twitter()
    nouns = spliter.nouns(text)
    count = collections.Counter(nouns)
    return_list = []
    for n, c in count.most_common(ntags):
        temp = {'tag': n, 'count': c}
        return_list.append(temp)
    return return_list

def keywording():
    noun_count = 40
    open_text_file = open(FILE_NAME_2, mode='r+', encoding='utf8')
    text = open_text_file.read()
    tags = get_tags(text, noun_count)
    open_text_file.close()
    open_output_file = open(FILE_NAME_3, mode='w+', encoding='utf8')
    for tag in tags:
        noun = tag['tag']
        count = tag['count']
        if len(noun) == 1:
            continue
        open_output_file.write('{} {}\n'.format(noun, count))
    open_output_file.close()

crawler_href ("eco")
print ('============================')
crawler_a ()
print ('============================')
keywording()
print ('============================')


'''open_text_file = open("test.txt", mode='r+', encoding='utf8')
text = open_text_file.read()
text = refine(text)
print (text)'''
