import pywikibot


# https://www.wikidata.org/w/api.php?action=help&modules=wbcreateclaim&uselang=en
def add_value(site, entity_id, property_id, value):
    request = {
        'action': 'wbcreateclaim',
        'entity': entity_id,
        'snaktype': 'value',
        'property': property_id,
        'value': value,
        'summary': 'test',
        'token': site.tokens['edit'],
        'bot': '1',
    }
    site._simple_request(**request).submit()


def get_site():
    site = pywikibot.Site('test', 'wikidata')
    site.login()
    return site


def main():
    site = get_site()
    add_value(site, 'Q34698', 'P72814', '"test"')


if __name__ == '__main__':
    main()
