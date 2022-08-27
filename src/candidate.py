class Candidate:

    def __init__(self, parsed_id, lemma, lexical_category, genders):
        self.parsed_id = parsed_id
        self.lemma = lemma
        self.lexical_category = lexical_category
        self.genders = genders

    def __repr__(self):
        return '{{id={}, lemma={}, lexical_category={}, genders={{{}}}}}'.format(self.parsed_id, self.lemma, self.lexical_category, ', '.join(self.genders))
