from datetime import datetime
import mysql.connector


class DB:

    def __init__(self, conf):
        self._cnx = mysql.connector.connect(**conf)
        self._cursor = self._cnx.cursor(buffered=True)

    def save_crawl(self, url, status_code, headers, content):
        data = (url, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), status_code, headers, content)
        self._cursor.execute('INSERT INTO `crawl`(`url`, `date`, `status_code`, `headers`, `content`) VALUES(%s, %s, %s, %s, %s)', data)
        self._cnx.commit()

    def get_url(self, url):
        self._cursor.execute('SELECT `status_code`, `headers`, `content` FROM `crawl` WHERE `url` = %s ORDER BY `date` DESC LIMIT 1', (url,))
        if self._cursor.rowcount == 1:
            row = self._cursor.fetchone()
            return {'status_code': row[0], 'headers': row[1], 'content': row[2]}
        return None

    def save_history(self, entity_id, property_id, value):
        data = (entity_id, property_id, value, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self._cursor.execute('INSERT INTO `history`(`entity`, `property`, `value`, `date`) VALUES(%s, %s, %s, %s)', data)
        self._cnx.commit()

    def exists_history(self, entity_id, property_id):
        self._cursor.execute('SELECT COUNT(*) AS `count` FROM `history` WHERE `entity` = %s AND `property` = %s', (entity_id, property_id))
        row = self._cursor.fetchone()
        return row[0] >= 1
