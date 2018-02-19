#-*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from selenium import webdriver
import time
import re

NotFound = 'no result'
PERIOD = 1
STATE = 2
LOC = 3
MAXIMUM = 5

class Daummap_crawler:
    def __init__(self, slot_s, slot_e):
        self.binary = 'D:\chromedriver\chromedriver.exe'      # 크롬 드라이버를 다운받은 경로
        self.browser = webdriver.Chrome(self.binary)
        self.slot_s = slot_s
        self.slot_e = slot_e
        self.route_list = []
        self.result_routes = []
        self.fetival_url = "https://search.daum.net/search?w=tot&DA=YZR&t__nil_searchbox=btn&sug=&sugo=&q=%EC%B6%95%EC%A0%9C"
        self.href_list = []
        self.infos = []

    def extract_roadinfo(self):        # 고속도로 분기점 (**IC, **JC) 뽑는 함수
        target_url = "http://map.daum.net/?map_type=TYPE_MAP&map_hybrid=false&sName=" + self.slot_s + \
                     "&eName=" + self.slot_e + "&target=car"
        self.browser.get(target_url)
        time.sleep(5)

        html = self.browser.page_source
        soup = BeautifulSoup(html, "html.parser")
        html = soup.find_all("li", class_="CheckpointItemGroupView")

        road_junctions = []
        for element in html:           # HTML 소스에서 <span> </span> 소스만 뽑기 (no class)
            road_junctions += element.find_all('span', attrs={'class': None})

        for i in range(len(road_junctions)):     # 태그 안의 text만 뽑기
            road_junctions[i] = road_junctions[i].getText()

        if len(road_junctions) == 0: return NotFound     # 태그 안의 text가 하나도 없을 때 NorFound 반환
        return road_junctions

    def extract_junctions(self):               # self.route_list 에 정제된 IC, JC 데이터 저장하는 함수
        content = self.extract_roadinfo()
        extract_IC = re.compile(r'(.*?IC)')
        extract_JC = re.compile(r'(.*?JC)')
        for route in content:
            route = route.split()
            for single_route in route:
                if re.match(extract_IC, single_route) or re.match(extract_JC, single_route):
                    self.route_list.append(single_route)
        self.route_list = list(set(self.route_list))      # self.route_list 에 정제된 IC, JC 데이터 저장

    def find_address(self):      # **IC, **JC 의 근처 관광지로 검색한 결과 반환 (가장 첫번째로 나오는 주소)
        self.extract_junctions()
        result_route, result_name, result_url = [], [], []
        browser = webdriver.Chrome(self.binary)
        browser.get("https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=1&ie=utf8&query=")

        for route in self.route_list:
            # print('\n','for# route: ', route)
            elem = browser.find_element_by_id("nx_query")
            search = route.encode('cp949').decode('cp949') + u'\uADFC\uCC98\uAD00\uAD11\uC9C0'.encode('cp949').decode(
                'cp949')
            elem.clear()
            elem.send_keys(search)
            elem.submit()

            time.sleep(1)
            html = browser.page_source
            soup = BeautifulSoup(html, "html.parser")

            if soup.find('li', id="sp_local_1") is not None:
                get_name = soup.find('dl', class_="info_area").find('a')['title']
                get_loc = soup.find('li', id="sp_local_1")
                get_url = soup.find('dl', class_="info_area").find('a')['href']
                try:
                    get_loc = get_loc.find_all('dd')[1].find('span')['title']
                    result_route.append(get_loc)
                    result_name.append(get_name)
                    result_url.append(get_url)
                except Exception:
                    get_loc = get_loc.find_all('dd')[1].find_all('span')[1]['title']
                    result_route.append(get_loc)
                    result_name.append(get_name)
                    result_url.append(get_url)
            elif soup.find('div', id="sp_local_1") is not None:
                get_loc = soup.find('div', id="sp_local_1").find('dd').getText()
                get_name = soup.find('div', class_="tit_area").find('a')['title']
                get_url = soup.find('div', class_="tit_area").find('a')['href']
                result_route.append(get_loc)
                result_name.append(get_name)
                result_url.append(get_url)
            else: print('else문: 근처 관광지 검색 결과 없음')
        print(result_route, result_name, result_url)

        browser.quit()
        if len(result_route) == 0:
            # print('len(result_route)==0 : ',result_route, len(result_route))
            return NotFound

        # print('result_route element exist:',result_route, len(result_route))
        for loc in result_route:
            loc = loc.split()[0:2]  # 첫 두 요소만 뽑아 route에 저장  ex) 대구 북구, 강원 인제군
            if loc not in self.result_routes:
                self.result_routes.append(loc)
        return self.result_routes


    def find_site(self):  # **IC, **JC 의 근처 관광지로 검색한 결과 반환 (가장 첫번째로 나오는 주소)
        self.extract_junctions()
        result_route = []
        browser = webdriver.Chrome(self.binary)
        all_sights = ''

        for route in self.route_list:

            search = route.encode('cp949').decode('cp949') + u'\uADFC\uCC98\uAD00\uAD11\uC9C0'.encode('cp949').decode(
                'cp949')
            browser.get(
                "https://www.google.co.kr/search?q=" + search + "+관광지&oq=" + search + "+관광지&aqs=chrome..69i57j69i60j0l2.3412j0j7&sourceid=chrome&ie=UTF-8")
            all_sights += search

            time.sleep(1)
            html = browser.page_source
            soup = BeautifulSoup(html, "html.parser")
            sights = soup.findAll('a', {"class": "_B7n"})
            count = 1
            for sight in sights:
                all_sights += str(count) + sight.title.string + "\n"
        return all_sights

    def extract_festivals(self):    # 다음 축제에서 매칭되는 주소의 축제 정보만 가져오는 함수
        self.browser.get(self.fetival_url)
        for route in self.result_routes:    # ex) route == ['서울','중구']
            elem = self.browser.find_element_by_xpath("//label[@title='전체']")
            elem.click()
            time.sleep(1)

            elem = self.browser.find_element_by_id("smok_opt_1844_depth_1")  # 서울, 경기 등 도시 단위 검색
            elem.click()
            time.sleep(1)

            add = route[0]            # 서울, 경기, 부산... (시)
            add_detailed = route[1]   # 인제군, 강남구...   (군구)

            xpath_loc1 = "//label[@title=" + "'" + add + "']"
            elem = self.browser.find_element_by_xpath(xpath_loc1)
            elem.click()
            time.sleep(1)

            while "unfold" in self.browser.page_source:      # 다음 축제에서 펼쳐보기가 있는 경우
                try:  # 다음 축제에서 처음 지역(ex.서울)을 선택한 뒤 펼쳐보기를 누를 수 있는 경우
                    elem = self.browser.find_element_by_xpath("//span[@class='tailBtn']")
                    elem.click()
                    time.sleep(1)
                except Exception:
                    # print("펼쳐보기가 없습니다.")
                    break

            # 도시명(ex.서울) 으로 검색한 결과의 html 소스 가져오기
            html = self.browser.page_source.encode('utf-8').decode('utf-8')
            soup = BeautifulSoup(html, "html.parser")
            festival_list = soup.find_all("li", class_={"item", "item odd", "item odd hide"})
            priority = 1
            for fe in festival_list:
                feature = fe.find_all("span")
                if feature[LOC]["title"] == add + ' ' + add_detailed:        # 시, 군구 까지 같은 경우
                    self.href_list.append("https://search.daum.net/search" + fe.find("a")["href"])  # 해당 축제 url 저장
                    self.infos.append([feature[PERIOD]["title"], feature[STATE]["title"], feature[LOC]["title"]])
                if priority > MAXIMUM: break  # MAXIMUM 보다 많은 경우 for문 종료
                priority += 1

        self.browser.quit()
        if len(self.href_list) == 0:
            return NotFound
        return self.href_list  # self.infos 는 필요할 때 대비하여 리스트에 담아두었으나 현재 버전에서는 리턴해주지 않음


slot_s = "경상남도"       # sds에서 DA로 보낼 slot_s 값 == 출발지
slot_e = "속초"       # sds에서 DA로 보낼 slot_e 값 == 목적지
crawler = Daummap_crawler(slot_s, slot_e)
print(crawler.find_site())
# print(crawler.find_address())                 # ~근처 관광지로 검색하여 시군구까지 뽑아온 결과
# print(crawler.extract_festivals())            # 해당 주소에 해당하는 축제 링크 뽑아온 결과
                                              # 축제이름 등 다른 정보는 self.infos를 반환하면 OK.

