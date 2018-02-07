import sys
from bs4 import BeautifulSoup
import urllib.request

def crawler_href (word):
    word = "https://search.naver.com/search.naver?where=news&sm=tab_jum&query=" + urllib.parse.quote(word, safe='')
    req = urllib.request.Request(word)
    data = urllib.request.urlopen(req).read()
    bs = BeautifulSoup(data, 'html.parser')
    l = bs.find_all('a')
    idx = 0
    for s in l:
        try:
            prop = s.get('class')	# get class property
            if prop != None and prop[0] == "": # if class property exist, check icon_pic_n
                print("%s : %s" % (s.get('href'), s.get_text()))
        except UnicodeEncodeError:
            print("Errror : %d" % (idx))
        finally: idx += 1
word = input("위 키워드 중  더 알아보고 싶은 키워드를 입력해주세요")
#crawler_href (word)
print(urllib.parse.quote(word, safe=''))