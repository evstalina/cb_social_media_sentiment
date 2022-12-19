import re
import nltk
nltk.download("stopwords")
import pandas as pd

from nltk.corpus import stopwords
from pymorphy2 import MorphAnalyzer
from nltk.stem.snowball import SnowballStemmer
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures

STOPWORDS = stopwords.words("russian")

    

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

class BigramFilter:
    def __init__(self, path_voc=None):
        self.morph_analyzer = MorphAnalyzer()
        if path_voc is not None:
            self.bigramms = self._load_voc()
    
    def train(self, text1, text2):
        text1, text2 = self._process(text1), self._process(text2)
        bigramm1 = nltk.FreqDist(nltk.bigrams(text1))
        bigramm2 = nltk.FreqDist(nltk.bigrams(text2))
        bigramm1_df = self._bigramm_to_df(bigramm1.most_common())
        bigramm2_df = self._bigramm_to_df(bigramm2.most_common())
        self.bigramms = self._intersection(bigramm1_df, bigramm2_df)

    def _bigramm_to_df(self, bigramm):
        return pd.DataFrame([
            {"bigramm": i[0][0]+"_"+i[0][1], "freq": i[1]}
            for i in bigramm])

    def save_voc(self, path_save):
        self.bigramms.to_csv(path_save)#("bigramms.csv")

    def match(self, text):
        s = []
        for t in text.split("."):
            s += self._process(t)
        bigramm = self._bigramm_to_df(nltk.FreqDist(nltk.bigrams(s)).most_common())
        return 0

    def _process(self, t):
        s = []
        for t in line.split("."):
            t = t.lower()
            t = re.sub(r'[^а-яё ]+', ' ', t)
            t = t.replace("  ", " ")
            s += [self.morph_analyzer.parse(word)[0].normal_form for word in t.split() if word not in STOPWORDS]
        return s

    def _process_file(self, path):
        s = []
        with open(path, "r") as rdr:
            for line in rdr:
                s += self._process(line)
        return s
    
    def _intersection(self, bigramm1, bigramm2):
        return pd.merge(bigramm1, bigramm2, how="inner", on=["bigramm"])

    def _load_voc(self, path_voc):
        self.bigrams = pd.read_csv(path_voc)
