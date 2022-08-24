from dico import Dico


class TlfiIndex(Dico):

    def __init__(self, db):
        super().__init__(db)

    def get_property_id(self):
        raise NotImplementedError()

    def get_lexemes_to_crawl_query(self):
        raise NotImplementedError()

    def get_url(self):
        return 'https://www.cnrtl.fr/{}'

    def infer_id(self, lemma):
        raise NotImplementedError()

    def is_matching(self, content, lemma, lexical_category, gender):
        raise NotImplementedError()

    def get_id_from_redirect(self, r):
        raise NotImplementedError()

    def get_edit_summary(self):
        raise NotImplementedError()
