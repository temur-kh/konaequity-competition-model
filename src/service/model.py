import os
import pickle
import time
from collections import defaultdict
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

from service.constants import *


class CompetitionModel:
    def __init__(self, n_jobs=4):
        # nearest neighbor models (by industry, description and G values)
        self.ind_neigh_model = NearestNeighbors(n_jobs=n_jobs, metric='cosine')
        self.des_neigh_model = NearestNeighbors(n_jobs=n_jobs, metric='cosine')
        self.gs_neigh_model = NearestNeighbors(n_jobs=n_jobs, metric='cosine')
        self.df: Optional[pd.DataFrame] = None

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

    def find_competitors(self, id, stats, max_k=6, model_weights=(0.4, 0.55, 0.05), radius=None, buffer_size=10000):
        # neighbors by industries
        df_size = len(self.df)
        join_dict = defaultdict(dict)
        start_time = time.time()
        x = np.tile(np.array(self.df[self.df[COMPANY_ID] == id][IND_VECTOR].values[0]), (3, 1))
        weights, ids = self.ind_neigh_model.kneighbors(x, n_neighbors=min(df_size, buffer_size))
        for weight, comp_id in zip(weights[0], ids[0]):
            join_dict[comp_id][IND_DISTANCE] = weight
        stats['IND_NEIGH_MODEL'] += time.time() - start_time

        # neighbors by descriptions
        start_time = time.time()
        x = np.tile(np.array(self.df[self.df[COMPANY_ID] == id][DES_VECTOR].values[0]), (3, 1))
        weights, ids = self.des_neigh_model.kneighbors(x, n_neighbors=min(df_size, buffer_size))
        for weight, comp_id in zip(weights[0], ids[0]):
            join_dict[comp_id][DES_DISTANCE] = weight
        stats['DES_NEIGH_MODEL'] += time.time() - start_time

        # neighbors by G values
        start_time = time.time()
        x = np.tile(np.array(self.df[self.df[COMPANY_ID] == id][GS_VECTOR].values[0]), (3, 1))
        weights, ids = self.gs_neigh_model.kneighbors(x, n_neighbors=min(df_size, buffer_size))
        for weight, comp_id in zip(weights[0], ids[0]):
            join_dict[comp_id][GS_DISTANCE] = weight
        stats['GS_NEIGH_MODEL'] += time.time() - start_time

        # join dataframes
        start_time = time.time()
        join_df = pd.DataFrame.from_dict(join_dict, orient='index')
        join_df.reset_index(level=0, inplace=True)
        join_df.rename({'index': COMPETITOR_IDX}, axis='columns', inplace=True)
        join_df.dropna(subset=[IND_DISTANCE, DES_DISTANCE], inplace=True)
        join_df.fillna(value=0.5, inplace=True)
        stats['JOIN_DF_CREATION'] += time.time() - start_time
        start_time = time.time()
        join_df[TOTAL_DISTANCE] = model_weights[0] * join_df[IND_DISTANCE] \
                                  + model_weights[1] * join_df[DES_DISTANCE] \
                                  + model_weights[2] * join_df[GS_DISTANCE]
        stats['TOTAL_DISTANCE_CALC'] += time.time() - start_time
        start_time = time.time()
        join_df = join_df.sort_values(TOTAL_DISTANCE).reset_index().head(max_k + 1)
        stats['JOIN_DF_SORTING'] += time.time() - start_time

        # result
        start_time = time.time()
        if radius:
            res_df = self.df.iloc[join_df[join_df[TOTAL_DISTANCE] <=
                                          radius][COMPETITOR_IDX], :].reset_index()
        else:
            res_df = self.df.iloc[join_df[COMPETITOR_IDX], :].reset_index()
        stats['DF_ILOC'] += time.time() - start_time
        start_time = time.time()
        res_df[IND_DISTANCE] = join_df[IND_DISTANCE]
        res_df[DES_DISTANCE] = join_df[DES_DISTANCE]
        res_df[GS_DISTANCE] = join_df[GS_DISTANCE]
        res_df[TOTAL_DISTANCE] = join_df[TOTAL_DISTANCE]
        res_df = res_df[res_df[COMPANY_ID] != id].head(max_k)
        stats['RES_DF_COLUMNS'] += time.time() - start_time
        return res_df, stats

    def save(self, dir_path):
        ind_model_path = os.path.join(dir_path, IND_MODEL_FILENAME)
        des_model_path = os.path.join(dir_path, DES_MODEL_FILENAME)
        gs_model_path = os.path.join(dir_path, GS_MODEL_FILENAME)
        df_path = os.path.join(dir_path, VECTOR_DATA_FILENAME)
        pickle.dump(self.ind_neigh_model, open(ind_model_path, 'wb'))
        pickle.dump(self.des_neigh_model, open(des_model_path, 'wb'))
        pickle.dump(self.gs_neigh_model, open(gs_model_path, 'wb'))
        pickle.dump(self.df[VECTOR_DATA_COLUMNS], open(df_path, 'wb'))

    def load(self, dir_path):
        ind_model_path = os.path.join(dir_path, IND_MODEL_FILENAME)
        des_model_path = os.path.join(dir_path, DES_MODEL_FILENAME)
        gs_model_path = os.path.join(dir_path, GS_MODEL_FILENAME)
        df_path = os.path.join(dir_path, VECTOR_DATA_FILENAME)
        self.ind_neigh_model = pickle.load(open(ind_model_path, 'rb'))
        self.des_neigh_model = pickle.load(open(des_model_path, 'rb'))
        self.gs_neigh_model = pickle.load(open(gs_model_path, 'rb'))
        self.df = pickle.load(open(df_path, 'rb'))
