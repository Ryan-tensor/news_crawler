import requests
from bs4 import BeautifulSoup

req = requests.get('http://news.naver.com/main/ranking/read.nhn?mid=etc&sid1=111&rankingType=popular_day&oid=014&aid=0003935373&date=20180102&type=1&rankingSectionId=101&rankingSeq=5')
html = req.text
soup = BeautifulSoup(html, 'html.parser')
#print(soup)
my_titles = soup.select('#articleBodyContents')
# my_titles는 list 객체

for title in my_titles:
    # Tag안의 텍스트
    #print(title.contents)
    print(title.text)
    #print(title.get_text)
    # Tag의 속성을 가져오기(ex: href속성)
    #print(title.get('href'))
### #wrap > table > tbody > tr > td.content > div > div.ranking_section.ranfir > ol > li.num1 > dl > dt > a
### #wrap > table > tbody > tr > td.content > div > div.ranking_section.ranfir > ol > li.num2 > dl > dt > a
### #wrap > table > tbody > tr > td.content > div > div:nth-child(10) > ol > li.num1 > dl > dt > a
# body > section.main-content > ul:nth-child(7) > li:nth-child(1)
# body > section.main-content > ul:nth-child(7) > li:nth-child(2)
# body > section.main-content > ul:nth-child(7) > ul:nth-child(3)
# body > section.main-content > ul:nth-child(7) > li:nth-child(4)
# body > section.main-content > ul:nth-child(7) > ul:nth-child(5)
# body > section.main-content > ul:nth-child(7)
# body > section.main-content > ul:nth-child(11)

##yDmH0d > c-wiz > div > div.fWwQIb.ChVoCd.rOrCPc.AfWyGd > main > div.KaRWed.XogBlf > div:nth-child(1) > c-wiz > div > c-wiz.PaqQNc.QwxBBf.f2t20b.PBWx0c > div > div > div.v4IxVd > div.M1Uqc.kWyHVd > a
###                                                                                                                                                               div > div.v4IxVd > div.M1Uqc.kWyHVd > a
