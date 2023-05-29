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

        query = 'SELECT * FROM ver WHERE sub_title=%s AND ver_title=%s'
        values = (item['sub_title'], item['ver_title'])
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()

        if result:
            spider.logger.info('Data already exists in database.')
        else:
            insert_query = f'INSERT INTO ver (title, sub_title, ver_title, judgement_date, crime_id, url, incident, incident_lite, result, laws) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            values = (item['title'], item['sub_title'], item['ver_title'],item['judgement_date'], item['crime_id'], item['url'],item['incident'], item['incident_lite'], item['result'], item['laws'])
            self.cursor.execute(insert_query, values)
            spider.logger.info('Data added to database.')
        
        return item
