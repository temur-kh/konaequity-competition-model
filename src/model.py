import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

from src.constants import *


class CompetitionModel:
    def __init__(self, n_jobs=4):
        # nearest neighbor models (by industry, description and G values)
        self.ind_neigh_model = NearestNeighbors(n_jobs=n_jobs, metric='cosine')
        self.des_neigh_model = NearestNeighbors(n_jobs=n_jobs, metric='cosine')
        self.gs_neigh_model = NearestNeighbors(n_jobs=n_jobs, metric='cosine')
        self.df = None

    def fit(self, df: pd.DataFrame):
        self.df = df
        # fitting a model for Industries field
        train_data = np.vstack(df[IND_VECTOR].values)
        self.ind_neigh_model.fit(train_data)
        # fitting a model for Description field
        train_data = np.vstack(df[DES_VECTOR].values)
        self.des_neigh_model.fit(train_data)
        # fitting a model for Gs field
        train_data = np.vstack(df[GS_VECTOR].values)
        self.gs_neigh_model.fit(train_data)

    def find_competitors(self, id, max_k=6, model_weights=(0.4, 0.5, 0.1), radius=None, buffer_size=10000):
        # neighbors by industries
        x = np.vstack(self.df[self.df[COMPANY_ID] == id][IND_VECTOR].values)
        weights, ids = self.ind_neigh_model.kneighbors(x, n_neighbors=buffer_size)
        ind_df = pd.DataFrame({COMPANY_ID: ids[0], IND_DISTANCE: weights[0]})

        # neighbors by descriptions
        x = np.vstack(self.df[self.df[COMPANY_ID] == id][DES_VECTOR].values)
        weights, ids = self.des_neigh_model.kneighbors(x, n_neighbors=buffer_size)
        des_df = pd.DataFrame({COMPANY_ID: ids[0], DES_DISTANCE: weights[0]})

        # neighbors by G values
        x = np.vstack(self.df[self.df[COMPANY_ID] == id][GS_VECTOR].values)
        weights, ids = self.gs_neigh_model.kneighbors(x, n_neighbors=buffer_size)
        g_df = pd.DataFrame({COMPANY_ID: ids[0], GS_DISTANCE: weights[0]})

        # join dataframes
        join_df = ind_df.merge(des_df.merge(g_df, on=COMPANY_ID, how='outer'),
                               on=COMPANY_ID, how='outer')
        join_df.dropna(inplace=True)
        join_df[TOTAL_DISTANCE] = model_weights[0] * join_df[IND_DISTANCE] \
                                  + model_weights[1] * join_df[DES_DISTANCE] \
                                  + model_weights[2] * join_df[GS_DISTANCE]
        join_df = join_df.sort_values(TOTAL_DISTANCE).reset_index()

        # result
        if radius:
            res_df = self.df.iloc[join_df[join_df[TOTAL_DISTANCE] <=
                                          radius].head(max_k)[COMPANY_ID], :].reset_index()
        else:
            res_df = self.df.iloc[join_df.head(max_k)[COMPANY_ID], :].reset_index()
        res_df[IND_DISTANCE] = join_df[IND_DISTANCE]
        res_df[DES_DISTANCE] = join_df[DES_DISTANCE]
        res_df[GS_DISTANCE] = join_df[GS_DISTANCE]
        res_df[TOTAL_DISTANCE] = join_df[TOTAL_DISTANCE]
        return res_df
