import glob
import lerobert
import mysql.connector
import os
import time


def get_file_path(normalized_lemma, ext='json'):
    return 'data/lerobert/{}.{}'.format(normalized_lemma, ext)


def main():
    db_config = lerobert.load_json_file('conf/general.json')['database']
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    query = 'INSERT INTO `crawl`(`url`, `date`, `status_code`, `headers`, `content`) VALUES(%s, %s, %s, %s, %s)'
    files = glob.glob('data/lerobert/*.json')
    for file in files:
        normalized_lemma = file[14:-5]
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(os.path.getmtime(file)))
        data = ('https://dictionnaire.lerobert.com/definition/{}'.format(normalized_lemma), date, lerobert.file_get_contents(get_file_path(normalized_lemma, 'http')), lerobert.file_get_contents(get_file_path(normalized_lemma, 'json')), lerobert.file_get_contents(get_file_path(normalized_lemma, 'html')))
        cursor.execute(query, data)
        cnx.commit()


if __name__ == '__main__':
    main()
