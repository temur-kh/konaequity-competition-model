import gensim.downloader as api
import pandas as pd
import numpy as np

from src.constants import *


class Vectorizer:
    def __init__(self):
        # downloading a pretrained Word2Vec model
        self.wv = api.load('word2vec-google-news-300')

    def text_to_vector(self, text, normalize=True):
        if pd.isna(text):
            return np.zeros((300,))
        vector = np.mean([self.wv[word] for word in text.split() if word in self.wv], axis=0)
        if np.isnan(vector).any():
            return np.zeros((300,))
        if normalize:
            return vector / np.linalg.norm(vector)
        else:
            return vector

    @staticmethod
    def gs_to_vector(row, normalize=True):
        vector = np.array([2 * row['G' + str(i)] - 1 if not pd.isna(row['G' + str(i)]) else 0.0
                           for i in range(1, 9)])
        if normalize and np.linalg.norm(vector) != 0:
            return vector / np.linalg.norm(vector)
        else:
            return vector

    def apply(self, df: pd.DataFrame, normalize=True):
        df[IND_VECTOR] = df[ALL_INDUSTRIES].apply(lambda s: self.text_to_vector(s, normalize=normalize))
        df[DES_VECTOR] = df[FULL_DESCRIPTION].apply(lambda s: self.text_to_vector(s, normalize=normalize))
        df[GS_VECTOR] = df.apply(lambda row: self.gs_to_vector(row, normalize=normalize), axis=1)
        return df
