import re
import utils

from db import DB
from academie_index import AcademieIndex


def main():
    configuration = utils.load_json_file('conf/general.json')
    db = DB(configuration['database'])
    dico = AcademieIndex(db)
    todo = set()
    todo.add('A9A0001')
    done = set()
    while len(todo) >= 1:
        todo_id = todo.pop()
        done.add(todo_id)
        r = dico.get_or_fetch_by_id(todo_id)
        found_ids = re.findall('/article/(A[1-9][A-Z][0-9]{4}[A-Z0-9-]*)"', r['content'])
        for found_id in found_ids:
            if found_id not in done:
                todo.add(found_id)
        if len(done) % 100 == 0:
            print('done: {}, todo: {}'.format(len(done), len(todo)))


if __name__ == '__main__':
    main()
