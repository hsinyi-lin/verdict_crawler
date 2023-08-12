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
            return
        
        # 呼叫 OpenAI API
        features, prison_term = None, None
        
        features = call_openai_find_features(item['incident'])
        prison_term = call_openai_prison_term(item['result'])
        
        if features is False or prison_term is False:
            return

        title = call_openai_title(item['incident'])
        incident_lite = call_openai_incident_lite(item['incident'])

        # 新增判決書資料
        insert_verdict = f'INSERT INTO verdict (title, sub_title, ver_title, judgement_date, crime_id, url, incident, incident_lite, result, laws) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        insert_verdict_values = (title, item['sub_title'], item['ver_title'],item['judgement_date'], item['crime_id'], item['url'],item['incident'], incident_lite, item['result'], item['laws'])
        self.cursor.execute(insert_verdict, insert_verdict_values)
        spider.logger.info('Data added to verdict table.')

        # 新增資料至特徵資料表
        self.cursor.execute(query, values)
        new_id = self.cursor.fetchone()[0]

        print(f'----------{new_id}--------')

        if item['crime_id'] == 1:
            insert_features = f'INSERT INTO theft_feature (id, is_money_related, is_abandoned, is_indoor, is_destructive, is_group_crime, is_transportation_used, has_criminal_record, is_income_tool, month) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            insert_feature_values = (new_id, features[0], features[1], features[2], features[3], features[4],features[5], features[6], features[7], prison_term)
            self.cursor.execute(insert_features, insert_feature_values)
        elif item['crime_id'] == 2:
            pass
        elif item['crime_id'] == 3:
            pass
        else:
            pass
        spider.logger.info(f'Data added to features to table with ID: {new_id}')

        return item
