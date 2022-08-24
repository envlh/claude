import re
import string
import utils

from db import DB
from tlfi_index import TlfiIndex


def main():
    configuration = utils.load_json_file('conf/general.json')
    db = DB(configuration['database'])
    dico = TlfiIndex(db)
    tlfi_letters = set()
    for letter in list(string.ascii_uppercase):
        page = 'portailindex/LEXI/TLFI/{}'.format(letter)
        while page is not None:
            r = dico.get_or_fetch_by_id(page)
            # form
            matches = re.findall(re.compile('<td><a href="/definition/(.*?)" title="Définition de (.*?)">(.*?)</a></td>', re.DOTALL), r['content'])
            if matches is not None:
                for match in matches:
                    for l in match[0]:
                        tlfi_letters.add(l)
            # next page
            match = re.search(re.compile('<a href="/(portailindex/[A-Z0-9/]+)"><img src="/images/portail/right.gif" title="Page suivante" border="0" width="32" height="32" alt="" /></a>', re.DOTALL), r['content'])
            if match is not None:
                page = match.group(1)
            else:
                page = None
    letters = list(tlfi_letters)
    letters.sort()
    for letter in letters:
        print(letter, end='')
    print()


if __name__ == '__main__':
    main()
