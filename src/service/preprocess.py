import numpy as np
import pandas as pd
import nltk
from nltk.corpus import stopwords

from service.constants import *

nltk.download('punkt')
nltk.download("stopwords")

stop_words = stopwords.words("english")


class Preprocessor:
    # join descriptions to form a single one if possible
    @staticmethod
    def join_descriptions(row):
        if not pd.isna(row[DESCRIPTION]):
            return row[DESCRIPTION]
        elif not pd.isna(row[LINKEDIN_BIO]):
            return row[LINKEDIN_BIO]
        else:
            return np.nan

    # join industry defining columns to form a single one if possible
    @staticmethod
    def join_industries(row):
        text = ''
        if not pd.isna(row[INDUSTRY]):
            text += row[INDUSTRY] + ' '
        if not pd.isna(row[CATEGORIES]):
            text += row[CATEGORIES] + ' '
        if not pd.isna(row[LINKEDIN_INDUSTRIES]):
            text += row[LINKEDIN_INDUSTRIES] + ' '
        if not pd.isna(row[GOOGLE_PLACES_INDUSTRY]):
            text += row[GOOGLE_PLACES_INDUSTRY]
        if text != '':
            return text.strip()
        else:
            return np.nan

    @staticmethod
    def text_preprocess(text):
        if pd.isna(text):
            return np.nan
        tokenized = nltk.word_tokenize(text)
        tokenized = [word for word in tokenized if word.isalpha() and word not in stop_words]
        return ' '.join(tokenized)

    def apply(self, df):
        df = df[USEFUL_COLUMNS]
        df[COUNTRY_REGION].fillna('United States', inplace=True)

        df[ALL_INDUSTRIES] = df.apply(lambda row: self.join_industries(row), axis=1)
        df[FULL_DESCRIPTION] = df.apply(lambda row: self.join_descriptions(row), axis=1)

        df[ALL_INDUSTRIES] = df[ALL_INDUSTRIES].apply(lambda s: self.text_preprocess(s))
        df[FULL_DESCRIPTION] = df[FULL_DESCRIPTION].apply(lambda s: self.text_preprocess(s))
        return df
