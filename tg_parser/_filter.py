import re
import pandas as pd

from pymorphy2 import MorphAnalyzer
from nltk.stem.snowball import SnowballStemmer


class SimpleFilter:
    def __init__(self, path_words):
        self.morph_analyzer = MorphAnalyzer()
        self.stemmer = SnowballStemmer("russian") 
        df = pd.read_csv(path_words)
        self.filter_words = {l: df[df["level"] == l]["words"].apply(lambda x: self.morph_analyzer.parse(x)[0].normal_form).values for l in df["level"].unique()}
    
    def match(self, text):
        if not self._is_valid(text):
            return False
        
        text = self._stem_text(text)
        for level in self.filter_words.keys():
            if not self._search(level, text):
                return False
        return True

    def _search(self, level, text):
        for w in self.filter_words[level]:
            if w in text:
                return True | (level) > 0
        return False | (level) < 0

    def _is_valid(self, text):
        if type(text) is not str:
            return False

        return len(text) > 2


    def _stem_text(self, text):
        text = text.lower()
        text = re.sub(r'[^a-zа-яё ]+', ' ', text)
        text = text.replace("  ", " ")
        text = text.replace("банк россии", "цб")
        text = text.replace("центральный банк", "цб")
        return [self.morph_analyzer.parse(word)[0].normal_form for word in text.split()]
