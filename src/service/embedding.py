import gensim.downloader as api
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA

from service.constants import *


class Vectorizer:
    def __init__(self, coords_path=GPS_COORDS_PATH):
        # downloading a pretrained Word2Vec model
        self.wv = api.load('word2vec-google-news-300')
        coords_df = pd.read_csv(coords_path)
        self.coords = {}
        for index, row in coords_df.iterrows():
            self.coords[row[ADDRESS]] = (row[LATITUDE], row[LONGITUDE])

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

    def coords_to_vector(self, row):
        address = ''
        if not pd.isna(row[COUNTRY_REGION]):
            address += row[COUNTRY_REGION]
        if not pd.isna(row[STATE_REGION]):
            address += ', ' + row[STATE_REGION]
        if address in self.coords:
            return np.array(self.coords[address])
        elif row[COUNTRY_REGION] in self.coords:
            return np.array(self.coords[row[COUNTRY_REGION]])
        else:
            return np.array(self.coords[DEFAULT_COUNTRY])

    def apply(self, df: pd.DataFrame, normalize=True):
        df[IND_VECTOR] = df[ALL_INDUSTRIES].apply(lambda s: self.text_to_vector(s, normalize=normalize))
        df[DES_VECTOR] = df[FULL_DESCRIPTION].apply(lambda s: self.text_to_vector(s, normalize=normalize))
        df[GS_VECTOR] = df.apply(lambda row: self.gs_to_vector(row, normalize=normalize), axis=1)
        df[GPS_VECTOR] = df.apply(lambda row: self.coords_to_vector(row), axis=1)

        pca = PCA(n_components=IND_VECTOR_SIZE)
        vecs = pca.fit_transform(np.vstack(df[IND_VECTOR].values))
        df[IND_VECTOR] = [np.array(vec) for vec in vecs]
        pca = PCA(n_components=DES_VECTOR_SIZE)
        vecs = pca.fit_transform(np.vstack(df[DES_VECTOR].values))
        df[DES_VECTOR] = [np.array(vec) for vec in vecs]
        pca = PCA(n_components=GS_VECTOR_SIZE)
        vecs = pca.fit_transform(np.vstack(df[GS_VECTOR].values))
        df[GS_VECTOR] = [np.array(vec) for vec in vecs]
        return df
