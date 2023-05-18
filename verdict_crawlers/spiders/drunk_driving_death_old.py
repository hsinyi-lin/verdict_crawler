import scrapy
import re, json
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from verdict_crawlers.items import VerdictItem
from verdict_crawlers.utils import *


class TheftSpider(scrapy.Spider):
    name = 'drunk_driving_death_old'
    allowed_domains = ['judicial.gov.tw']

    def start_requests(self):

        for year in range(100,107):
            kw = f'{year}年度交訴字 交通工具致人於死罪'
            for page in range(1,26):
                request = scrapy.Request(
                    url=f'https://judgment.judicial.gov.tw/LAW_Mobile_FJUD/FJUD/qryresult.aspx?sys=M&kw={kw}&judtype=JUDBOOK&page={page}', 
                    callback=self.parse
                )
                request.meta['year'] = year
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
                print(tr_tag)
                if '酒駕致死' != title_list[-1] and '公共危險' != title_list[-1] and '過失致死' != title_list[-1] and '不安全駕駛致死' != title_list[-1]:
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
        htmlcontent = td.find('div', class_='text-pre text-pre-in')
        clean_content = ''.join(htmlcontent.text.split())

        # 判決書名稱+編號
        ver_title_idx = clean_content.find('刑事判決')+4
        data['ver_title'] = clean_content[:ver_title_idx]

        data['sub_title'] = clean_content[ver_title_idx: clean_content.find('號')+1]
        
        # 取得主文的位置
        main_title_idx = clean_content.find('主文')+2

        # 取得事實的位置
        incident_idx = clean_content.find('事實一、')+4

        # 取得事實前面的位置(之後用來確定是否真的是寫"事實")
        main_end_idx = clean_content.find('事實一、')-1

        # 如果找不到以上相關位置(表示不存在)
        if main_title_idx < 0 or incident_idx < 0 or main_end_idx < 0:
            return

        # 如果非"事實"而是其他字樣(前面應該要是句號)
        if clean_content[main_end_idx] != '。':
            return

        # 內文沒有起訴
        if '起訴。' not in clean_content:
            return

        data['result'] = clean_content[main_title_idx: main_end_idx+1]

        if data['result'] == '上訴駁回。':
            return

        data['incident'] = clean_content[incident_idx: clean_content.find('二、')]
        
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
        # 儲存法條
        laws = []
        for item in response.json()['list']:
            laws.append(re.split(r'[(（]',item['desc'])[0])
        data['laws'] = ','.join(laws)
    
        data['title'] = call_openai(data['incident'])

        data['title'] = data['title'].replace('45字以內','').replace('案件簡介：', '').replace('案：','')\
                .replace('案件：', '').replace('標題：', '').replace('「', '').replace('」', '')\
                .replace('【', '').replace('】','').replace('一、','').replace('二、','').replace('三、','')\
                .replace('四、','').replace('五、', '').strip()
        
        if len(data['title']) == 0:
            return
        
        item = VerdictItem()

        item['title'] = data['title']
        item['judgement_date'] = roc_to_ad(data['judgement_date'])
        item['year'] = data['year']
        item['crime_id'] = 4
        item['crime_name'] = data['crime_name']
        item['url'] = data['url']
        item['ver_title'] = data['ver_title']
        item['sub_title'] =data['sub_title']
        item['result'] = data['result']
        item['incident'] = data['incident']
        item['laws'] = data['laws']

        yield item
