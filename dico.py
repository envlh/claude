import json
import time
import urllib.parse
import utils


class Dico:

    def __init__(self, db):
        self._db = db

    def fetch_lexemes_to_crawl(self):
        query = self.get_lexemes_to_crawl_query()
        url = 'https://query.wikidata.org/sparql?{}'.format(urllib.parse.urlencode({'query': query, 'format': 'json'}))
        return json.loads(utils.fetch_url(url).content)['results']['bindings']

    def crawl_url(self, url):
        print(url)
        r = utils.fetch_url(url)
        status_code = r.status_code
        headers = json.dumps(dict(r.headers), ensure_ascii=False)
        content = r.text
        self._db.save_crawl(url, status_code, headers, content)
        time.sleep(10)
        return {'status_code': status_code, 'headers': headers, 'content': content}

    def get_or_fetch_by_id(self, inferred_id):
        url = self.get_url().format(inferred_id)
        cache = self._db.get_url(url)
        if cache is not None:
            return cache
        return self.crawl_url(url)

    def process(self, lexeme):
        lemma = lexeme['lemma']['value']
        lexical_category = lexeme['lexicalCategoryLabel']['value']
        gender = None
        if 'genderLabel' in lexeme:
            gender = lexeme['genderLabel']['value']
        inferred_id = self.infer_id(lemma)
        success = False
        if len(inferred_id) >= 1:
            r = self.get_or_fetch_by_id(inferred_id)
            if r['status_code'] == 200 and self.is_matching(r['content'], lemma, lexical_category, gender):
                success = True
            elif r['status_code'] == 301 or r['status_code'] == 302:
                redirect_id = self.get_id_from_redirect(r)
                if redirect_id is not None:
                    r_redirect = self.get_or_fetch_by_id(redirect_id)
                    if r_redirect['status_code'] == 200 and self.is_matching(r_redirect['content'], lemma, lexical_category, gender):
                        success = True
                    # print('{} → {} ({})'.format(inferred_id, redirect_id, success))
                    if success:
                        inferred_id = redirect_id
        return success, inferred_id

    def get_property_id(self):
        raise NotImplementedError()

    def get_lexemes_to_crawl_query(self):
        raise NotImplementedError()

    def get_url(self):
        raise NotImplementedError()

    def infer_id(self, lemma):
        raise NotImplementedError()

    def is_matching(self, content, lemma, lexical_category, gender):
        raise NotImplementedError()

    def get_id_from_redirect(self, r):
        raise NotImplementedError()

    def get_edit_summary(self):
        raise NotImplementedError()
