import scrapy
import re, json, time, datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from verdict_crawlers.items import TheftItem
from verdict_crawlers.utils import *



class TheftSpider(scrapy.Spider):
    name = 'theft'
    allowed_domains = ['judicial.gov.tw']

    def start_requests(self):
        tw_area = [
           '臺北', '士林', '新北', '宜蘭', 
           '基隆', '桃園',  '新竹', '苗栗', 
           '臺中', '彰化', '南投', '雲林',
           '嘉義', '台南', '高雄', '橋頭',
           '花蓮', '臺東', '屏東', '澎湖',
           '金門', '連江'
        ]
        
        currentDateTime = datetime.datetime.now()
        date = currentDateTime.date()

        current_roc_year = date.year - 1911

        for area in tw_area:
            kw = f'{area}地方法院刑事簡易判決 {current_roc_year}年度簡字第 竊盜罪'
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

        # print(tr_tags)
        if len(tr_tags) > 0:
            data_base_url = 'https://judgment.judicial.gov.tw/LAW_Mobile_FJUD/FJUD/data.aspx?'
            for tr_tag in tr_tags:
                data = dict()

                title_list = re.split(r'[,\s]+',tr_tag.getText().strip())
                if title_list[-1] != '竊盜' or title_list[3] != '簡':
                    continue

                print(title_list)

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
        
        print(data['ver_title'])

        # 判決書編號+名稱
        data['sub_title'] = ver_title.find_next_sibling('div').getText(strip=True)

        # 尋找並取得主文
        contents = htmlcontent.find_all()
        notEdit = htmlcontent.find_all('div', class_='notEdit')

        # 主文合併
        txt = ''
        for i in range(contents.index(notEdit[0])+1, contents.index(notEdit[1])):
            txt += ''.join(contents[i].text.split()) + '\n'
        txt = re.split('犯罪事實及理由|一、本案犯罪事實及證據|犯罪事實與理由', txt)[0]

        data['result'] = ''.join(txt.split(' ')).strip()

        incident = htmlcontent.find('div', text=re.compile('　　　　犯罪事實'))
        investigate = htmlcontent.find('div', text=re.compile('偵辦'))

        incident_idx = contents.index(incident)
        investigate_idx = contents.index(investigate)

        res = ''
        for i in range(incident_idx+1, investigate_idx):
            if i == incident_idx+1:
                res += ''.join(contents[i].text[2:].strip()) + '\n'
            else:
                res += ''.join(contents[i].text.strip()) + '\n'
        
        data['incident'] = ''.join(res.split(' ')).strip()
        print(data['incident'])

        # 解析法條的ajax 連結以取得資料，取得id
        # parsed_url = urlparse(data['url'])
        # captured_value = parse_qs(parsed_url.query)['id'][0]

        # request = scrapy.Request(
        #             url=f'https://judgment.judicial.gov.tw/LAW_Mobile_FJUD/controls/GetJudRelatedLaw.ashx?pkid={captured_value}',
        #             callback=self.parse_law
        #         )
        # request.meta['data'] = data

        # yield request

        # data = response.meta['data']
        # print(data)

        # 儲存法條
        # laws = []
        # for item in response.json()['list']:
        #     print(data)
        #     laws.append(re.split(r'[(（]',item['desc'])[0])
        # data['laws'] = ','.join(laws)
        # print(data)

        # print(data['laws'])


        data['laws'] = None
        # 使用 OpenAI API
        data['features'] = call_openai_find_features(data['incident'])
        time.sleep(30)

        data['prison_term'] = call_openai_prison_term(data['result'])
        time.sleep(30)

        if data['features'] == False or data['prison_term'] == False:
            return

        data['title'] = call_openai_title(data['incident'])
        time.sleep(30)

        data['incident_lite'] = call_openai_incident_lite(data['incident'])
        time.sleep(30)
        
        # 將資料移入Scrapy Item
    
        item = TheftItem()

        item['title'] = data['title']
        item['judgement_date'] = roc_to_ad(data['judgement_date'])
        item['year'] = data['year']
        item['crime_id'] = 1
        item['crime_name'] = data['crime_name']
        item['url'] = data['url']
        item['ver_title'] = data['ver_title']
        item['sub_title'] =data['sub_title']
        item['result'] = data['result']
        item['incident'] = data['incident']
        item['incident_lite'] = data['incident_lite']
        item['laws'] = data['laws']

        item['is_money_related'], item['is_abandoned'], item['is_indoor'], item['is_destructive'], \
            item['is_group_crime'], item['is_transportation_used'], item['has_criminal_record'], \
                item['is_income_tool'] = data['features']

        item['month'] = data['prison_term']

        yield item
