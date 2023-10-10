import scrapy
import re, json
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from verdict_crawlers.items import VerdictItem
from verdict_crawlers.utils import *


class TheftSpider(scrapy.Spider):
    name = 'drunk_driving_death'
    allowed_domains = ['judicial.gov.tw']

    def start_requests(self):

        # tw_area = [
        #     '臺北', '士林', '新北', '宜蘭', 
        #     '基隆', '桃園',  '新竹', '苗栗', 
        #     '臺中', '彰化', '南投', '雲林',
        #     '嘉義', '台南', '高雄', '橋頭',
        #     '花蓮', '臺東', '屏東', '澎湖',
        #     '金門', '連江'
        # ]


        # kw = f'酒駕致死 {year}年度'
        # kw = f'杜宥賢犯不能安全駕駛動力交通工具因而致人於死罪，處有期徒刑肆年陸月。'
        kw = f'不能安全駕駛動力交通工具 酒精 死亡'
        # kw = f'不能安全駕駛動力交通工具 酒精 死亡 {current_roc_year()}年度交訴'
        for page in range(1,5):
            request = scrapy.Request(

                url=f'https://judgment.judicial.gov.tw/LAW_Mobile_FJUD/FJUD/qryresult.aspx?sys=M&kw={kw}&judtype=JUDBOOK&page={page}', 
                callback=self.parse
            )
            yield request


    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        tab_pane = soup.find('div', class_='container-fluid').find('div', class_='tab-pane active')
        table = tab_pane.find('table', class_='table int-table')
        tr_tags = tab_pane.find_all('tr')

        if len(tr_tags) > 0:
            data_base_url = 'https://judgment.judicial.gov.tw/LAW_Mobile_FJUD/FJUD/data.aspx?'
            for tr_tag in tr_tags:
                data = dict()
                # print(tr_tag.text)
                title_list = re.split(r'[,\s]+',tr_tag.getText().strip())
                if '酒駕致死' not in title_list[-1] and '公共危險' not in title_list[-1] and '過失致死' not in title_list[-1] and '不安全駕駛致死' not in title_list[-1] and '肇事' not in title_list[-1]:
                    continue

                # 標題、日期、年度、犯罪類型
                data['title'] = tr_tag.find('a', id='hlTitle').getText(strip=True)
                data['judgement_date'] = title_list[-2]
                data['year'] = title_list[2]
                data['crime_name'] = title_list[-1]

                # # 取得當前標籤位置，並拿出連結
                href = tr_tag.find_all('td')[2].find('a', id='hlTitle').get('href')
                url = data_base_url + href
                data['url'] = url

                # 請求連結
                request = scrapy.Request(
                    url=url, 
                    callback=self.parse_verdict
                )
                request.meta['data'] = data

                yield request

    def parse_verdict(self, response):
        data = response.meta['data']
        d_soup = BeautifulSoup(response.text, 'lxml')
        
        # 解析判決書格式
        text_pre = d_soup.find('div', class_='col-td text-pre')
        td = d_soup.find('table').find('tr').find('td')
        htmlcontent = td.find('div', class_='htmlcontent')

        # 判決書標題
        ver_title = htmlcontent.find('div')
        data['ver_title'] = ver_title.getText(strip=True)
        

        # 判決書編號+名稱
        data['sub_title'] = ver_title.find_next_sibling('div').getText(strip=True)

        # 尋找並取得主文
        contents = htmlcontent.find_all()
        notEdit = htmlcontent.find_all('div', class_='notEdit')

        clean_main_title = ''.join(notEdit[0].text.split())
        clean_incident_title = ''.join(notEdit[1].text.split())

        if clean_main_title != '主文':
            return
        if clean_incident_title != '事實' and clean_incident_title != '犯罪事實':
            return

        # 主文合併
        txt = ''
        for i in range(contents.index(notEdit[0])+1, contents.index(notEdit[1])):
            txt += ''.join(contents[i].text.split()) + '\n'
        txt = re.split('犯罪事實及理由|一、本案犯罪事實及證據|犯罪事實與理由', txt)[0]

        data['result'] = ''.join(txt.split(' ')).strip()

        if data['result'] == '上訴駁回。':
            return

        # 取得主文標題跟犯罪經過標題
        incident = notEdit[1]
        investigate = htmlcontent.find('div', text=re.compile('起訴。'))
        # investigate = htmlcontent.find('div', text=re.compile('偵辦。'))

        # 標題中間有空格，要合併
        clean_main_title = ''.join(notEdit[0].text.split())
        clean_incident_title = ''.join(notEdit[1].text.split())

        # 檢查是不是主文標題跟事實或犯罪事實標題
        if clean_main_title != '主文' and ('犯罪事實' not in clean_incident_title or '事實' not in clean_incident_title):
            return

        # 取得犯罪事實或事實位置
        incident_idx = contents.index(incident)
        investigate_idx = contents.index(investigate)

        # 取得事實內容
        res = ''
        for i in range(incident_idx+1, investigate_idx):
            if i == incident_idx+1:
                res += ''.join(contents[i].text[2:].strip()) + '\n'
            else:
                res += ''.join(contents[i].text.strip()) + '\n'
        
        data['incident'] = ''.join(res.split(' ')).strip()
        
        # 檢查是否有酒精跟死亡在事實中
        if '酒精' not in data['incident'] or '死亡' not in data['incident']:
            return
        
        # 解析法條的ajax 連結以取得資料，取得id
        parsed_url = urlparse(data['url'])
        captured_value = parse_qs(parsed_url.query)['id'][0]

        request = scrapy.Request(
                    url=f'https://judgment.judicial.gov.tw/LAW_Mobile_FJUD/controls/GetJudRelatedLaw.ashx?pkid={captured_value}',
                    callback=self.parse_law
                )
        request.meta['data'] = data

        yield request

    def parse_law(self, response):
        data = response.meta['data']

        # 2023.08、部分判例沒有相關法條
        laws_result = None

        try:
            laws = []
            for item in response.json()['list']:
                laws.append(re.split(r'[(（]',item['desc'])[0])
            laws_result = ','.join(laws)
        except:
            laws_result = None

        # -------- 將資料移入Scrapy Item --------
    
        item = VerdictItem()

        # item['title'] = data['title']
        item['judgement_date'] = roc_to_ad(data['judgement_date'])
        item['year'] = data['year']
        item['crime_id'] = 4
        item['crime_name'] = data['crime_name']
        item['url'] = data['url']
        item['ver_title'] = data['ver_title']
        item['sub_title'] =data['sub_title']
        item['result'] = data['result']
        item['incident'] = data['incident']
        item['laws'] = laws_result

        # print(item)
        yield item
