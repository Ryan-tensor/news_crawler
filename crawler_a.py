from bs4 import BeautifulSoup
import urllib.request
def crawler_href ():
    req = urllib.request.Request("http://news.naver.com/main/ranking/popularDay.nhn?mid=etc&sid1=111");
    data = urllib.request.urlopen(req).read()
    bs = BeautifulSoup(data, 'html.parser')
    l = bs.find_all('a')
    idx = 0
    print("===============================================")
    for s in l:
        try:
            prop = s.get('class')	# get class property
            if prop != None and prop[0] == "nclicks(rig.ranksci)" and prop[0] != "lPV2Xe": # if class property exist, check icon_pic_n
                                           #nuEeue hzdq5d ME7ew
                print("%s : %s" % (s.get('href'), s.get_text()))
        except UnicodeEncodeError:
            print("Errror : %d" % (idx))
        finally: idx += 1
crawler_href ()