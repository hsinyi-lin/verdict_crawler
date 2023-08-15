import mysql.connector
from verdict_crawlers.utils import *


class MySQLPipeline:
    def __init__(self, mysql_settings):
        self.mysql_settings = mysql_settings

    @classmethod
    def from_crawler(cls, crawler):
        mysql_settings = crawler.settings.get('MYSQL_SETTINGS')
        return cls(mysql_settings)

    def open_spider(self, spider):
        self.connection = mysql.connector.connect(**self.mysql_settings)
        self.cursor = self.connection.cursor()

    def close_spider(self, spider):
        self.connection.commit()
        self.connection.close()

    def process_item(self, item, spider):
        query = 'SELECT id FROM verdict WHERE sub_title=%s AND ver_title=%s'
        values = (item['sub_title'], item['ver_title'])
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()

        if result:
            spider.logger.info('Data already exists in database.')
            raise "Data already exists in database."
        
        # 呼叫 OpenAI API
        features = call_openai_find_features(item['incident'], item['crime_id'])
        prison_term = call_openai_prison_term(item['result'], item['crime_id'])

        print(features)
        print(prison_term)
        print('----------------------------------')
        if isinstance(features, bool) or isinstance(prison_term, bool) :
            raise Exception('Features and prison term cannot be extracted.')

        title = call_openai_title(item['incident'])
        incident_lite = call_openai_incident_lite(item['incident'])
        print(incident_lite)

        # 新增判決書資料
        insert_verdict = f'INSERT INTO verdict (title, sub_title, ver_title, judgement_date, crime_id, url, incident, incident_lite, result, laws) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        insert_verdict_values = (title, item['sub_title'], item['ver_title'],item['judgement_date'], item['crime_id'], item['url'],item['incident'], incident_lite, item['result'], item['laws'])
        self.cursor.execute(insert_verdict, insert_verdict_values)
        spider.logger.info('Data added to verdict table.')

        # 新增資料至特徵資料表
        self.cursor.execute(query, values)
        new_id = self.cursor.fetchone()[0]

        print(f'----------{new_id}-START--------')

        if item['crime_id'] == 1:
            insert_features = f'INSERT INTO theft_feature (id, is_money_related, is_abandoned, is_indoor, is_destructive, is_group_crime, is_transportation_used, has_criminal_record, is_income_tool, month) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            insert_feature_values = (new_id, features[0], features[1], features[2], features[3], features[4],features[5], features[6], features[7], prison_term)
            self.cursor.execute(insert_features, insert_feature_values)
        elif item['crime_id'] == 2:
            pass
        elif item['crime_id'] == 3:
            insert_features = f'INSERT INTO robbery_feature (id, is_victim_injured, is_group_crime, is_weapon_used, has_prior_record, is_planned, is_multi_victims, is_due_to_hardship, is_property_damaged, month, prison_year, prison_month) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            insert_feature_values = (new_id, features[0], features[1], features[2], features[3], features[4],features[5], features[6], features[7], prison_term[2], prison_term[0], prison_term[1])
            self.cursor.execute(insert_features, insert_feature_values)
        else:
            pass
        
        # ---------------------------------------------------------------------

        spider.logger.info(f'Data added to features to table with ID: {new_id}')

        crime_list = [None, '竊盜罪', '殺人罪', '強盜罪', '酒駕致死罪']

        print('爬蟲抓取結果.....')
        print(item)

        print(f"此篇為關於「{crime_list[item['crime_id']]}」 相關之判例")
        print('ChatGPT已根據判決書內文，提取以下.....')
        print(f'自動產生標題: {title}')
        print(f'自動產生摘要及將專業用語轉換成大眾敘述: {incident_lite}')

        chinese_list = ['是' if feature else '否' for feature in features]

        if item['crime_id'] == 1:
            print('提取特徵：\n(1)偷竊物是否與金錢相關 (2)是否遺棄贓物 (3)犯罪地點是否在室內 (4)竊盜方法是否具破壞性 (5)是否兩人(含)以上犯罪 (6)是否使用交通工具來輸送贓物 (7)是否有前科 (8)是否竊取之財物為被害人生財工具')
            print('提取結果:', chinese_list)
            print(f'提取判刑年月數：大約會被判刑 {prison_term}個月')
        elif item['crime_id'] == 2:
            pass
        elif item['crime_id'] == 3:
            print('提取特徵：(1)是否導致受害者受傷 (2)是否兩人(含)以上犯案 (3)是否使用刀械 (4)是否擁有前科 (5)是否有計畫犯罪 (6)是否被害人人數超過兩人(含) (7)是否提及犯案人因生活困境而強盜 (8)是否毀損物品或建築')
            print('提取結果:', chinese_list)
            print(f'提取判刑年月數：大約會被判刑 {prison_term[0]} 年又 {prison_term[1]} 個月，總月數 {prison_term[2]} 個月')
        elif item['crime_id'] == 4:
            pass
        
        print(f'----------{new_id}-END----------')

        return item
