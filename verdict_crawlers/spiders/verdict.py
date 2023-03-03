import scrapy
import re, json
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

class VerdictSpider(scrapy.Spider):
    name = 'verdict'
    allowed_domains = ['judicial.gov.tw']

    def start_requests(self):
        tw_area = [
            '臺北', '士林', '新北', '宜蘭', 
            '基隆', '桃園',  '新竹', '苗栗', 
            '臺中', '彰化', '南投'
        ]
        
        for area in tw_area:
            for year in range(107, 112):
                kw = f'{area}地方法院刑事簡易判決 {year}年度簡字第 竊盜罪'
                for page in range(1,26):
                    yield scrapy.Request(
                        url=f'https://judgment.judicial.gov.tw/LAW_Mobile_FJUD/FJUD/qryresult.aspx?kw={kw}&judtype=JUDBOOK&page={page}', 
                        callback=self.parse
                    )


    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        tab_pane = soup.find('div', class_='container-fluid').find('div', class_='tab-pane active')
        table = tab_pane.find('table', class_='table int-table')
        tr_tags = tab_pane.find_all('tr')

        if len(tr_tags) > 0:
            data_base_url = 'https://judgment.judicial.gov.tw/LAW_Mobile_FJUD/FJUD/data.aspx?'
            for tr_tag in tr_tags:
                data = dict()

                title_list = re.split(r'[,\s]+',tr_tag.getText().strip())
                if title_list[-1] != '竊盜' or title_list[3] != '簡':
                    continue

                # 標題、日期、年度、犯罪類型
                data['title'] = tr_tag.find('a', id='hlTitle').getText(strip=True)
                data['date'] = title_list[-2]
                data['year'] = title_list[2]
                data['crime_type'] = title_list[-1]

                # # 取得當前標籤位置，並拿出連結
                href = tr_tag.find_all('td')[2].find('a', id='hlTitle').get('href')
                url = data_base_url + href
                data['url'] = url

                # 請求連結
                request = scrapy.Request(
                    url=url, 
                    callback=self.parse_paper
                )
                request.meta['data'] = data

                yield request

    def parse_paper(self, response):
        data = response.meta['data']
        d_soup = BeautifulSoup(response.text, 'lxml')
        
        # 當跑大量資料因部分格式不一致而直接跳出換下一筆
        try:
            # 解析判決書格式
            text_pre = d_soup.find('div', class_='col-td text-pre')
            td = d_soup.find('table').find('tr').find('td')
            htmlcontent = td.find('div', class_='htmlcontent')

            # 判決書標題
            ver_title = htmlcontent.find('div')
            data['ver_title'] = ver_title.getText(strip=True)
            

            # 判決書編號+名稱
            data['ver_no'] = ver_title.find_next_sibling('div').getText(strip=True)

            # 尋找並取得主文
            contents = htmlcontent.find_all()
            notEdit = htmlcontent.find_all('div', class_='notEdit')
            
            # if len(notEdit) < 2:
            #     continue

            # 主文合併
            txt = ''
            for i in range(contents.index(notEdit[0])+1, contents.index(notEdit[1])):
                txt += contents[i].text + '\n'
            data['verdict'] = txt.strip()
            # print(txt)
            

            # 取得犯罪事實標籤
            incident = htmlcontent.find('div', text=re.compile('\s犯罪事實'))

            # 如果沒有犯罪事實就跳下一個判決書
            # if isinstance(incident, type(None)):
            #     continue
            
            # 取得犯罪事實第一段
            data['incident'] = incident.find_next_sibling('div').text[2:]
        #     # 解析法條的ajax 連結以取得資料，取得id
            parsed_url = urlparse(data['url'])
            captured_value = parse_qs(parsed_url.query)['id'][0]

            request = scrapy.Request(
                        url=f'https://judgment.judicial.gov.tw/LAW_Mobile_FJUD/controls/GetJudRelatedLaw.ashx?pkid={captured_value}',
                        callback=self.parse_law
                    )
            request.meta['data'] = data

            yield request
        except:
            pass

    def parse_law(self, response):
        data = response.meta['data']
        # 儲存法條
        laws = []
        for item in response.json()['list']:
            laws.append(re.split(r'[(（]',item['desc'])[0])
        data['laws'] = laws
        yield data
