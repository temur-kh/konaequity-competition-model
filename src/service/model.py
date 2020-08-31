import os
import pickle
from collections import defaultdict
from typing import Optional

import pandas as pd
from annoy import AnnoyIndex

from service.constants import *
from service.utils import *


class CompetitionModel:
    def __init__(self):
        # nearest neighbor models (by industry, description, G values amd GPS coords)
        self.ind_neigh_model = AnnoyIndex(f=IND_VECTOR_SIZE, metric='angular')
        self.ind_neigh_model.set_seed(2019)
        self.des_neigh_model = AnnoyIndex(f=DES_VECTOR_SIZE, metric='angular')
        self.des_neigh_model.set_seed(2019)

        self.df: Optional[pd.DataFrame] = None
        self.loc_inds = set(pd.read_csv(LOCATION_INDEPENDENT_INDS_PATH)[INDUSTRY].apply(str.lower).values)

    def fit(self, df: pd.DataFrame):
        self.df = df
        # fitting a model for Industries field
        values = df[IND_VECTOR].values
        for i in range(len(values)):
            self.ind_neigh_model.add_item(i, values[i])
        self.ind_neigh_model.build(IND_N_TREES)
        # fitting a model for Description field
        values = df[DES_VECTOR].values
        for i in range(len(values)):
            self.des_neigh_model.add_item(i, values[i])
        self.des_neigh_model.build(DES_N_TREES)

    def find_competitors(self, id, max_k=6):
        x = self.df[self.df[COMPANY_ID] == id][ALL_INDUSTRIES].values[0]
        if any(ind in x for ind in self.loc_inds):
            return self._find_competitors(id, max_k=max_k, model_weights=(0.35, 0.5, 0.05, 0.1))
        else:
            return self._find_competitors(id, max_k=max_k, model_weights=(0.2, 0.5, 0.04, 0.26))

    def _find_competitors(self, id, max_k=6, model_weights=(0.2, 0.5, 0.04, 0.26), radius=None, buffer_size=10000):
        # neighbors by industries
        n = min(len(self.df), buffer_size)
        search_n = n // 50
        join_dict = defaultdict(dict)
        x = np.array(self.df[self.df[COMPANY_ID] == id][IND_VECTOR].values[0])
        ids, weights = self.ind_neigh_model.get_nns_by_vector(x, n=n,
                                                              search_k=search_n * IND_N_TREES,
                                                              include_distances=True)
        for weight, comp_id in zip(weights, ids):
            join_dict[comp_id][IND_DISTANCE] = weight

        # neighbors by descriptions
        x = np.array(self.df[self.df[COMPANY_ID] == id][DES_VECTOR].values[0])
        ids, weights = self.des_neigh_model.get_nns_by_vector(x, n=n,
                                                              search_k=search_n * DES_N_TREES,
                                                              include_distances=True)
        for weight, comp_id in zip(weights, ids):
            join_dict[comp_id][DES_DISTANCE] = weight

        # join dataframes
        join_df = pd.DataFrame.from_dict(join_dict, orient='index')
        join_df.reset_index(level=0, inplace=True)
        join_df.rename({'index': COMPETITOR_IDX}, axis='columns', inplace=True)
        join_df.dropna(subset=[IND_DISTANCE, DES_DISTANCE], inplace=True)

        # add gps and Gs distances
        x = np.array(self.df[self.df[COMPANY_ID] == id][GPS_VECTOR].values[0])
        join_df = join_df[join_df[DES_DISTANCE] > 0.05]
        join_df[GPS_DISTANCE] = join_df[COMPETITOR_IDX].apply(
            lambda idx: get_gps_distance(x, self.df.iloc[idx][GPS_VECTOR]))
        x = np.array(self.df[self.df[COMPANY_ID] == id][GS_VECTOR].values[0])
        join_df[GS_DISTANCE] = join_df[COMPETITOR_IDX].apply(
            lambda idx: get_gs_distance(x, self.df.iloc[idx][GS_VECTOR]))

        # total distance and sorting
        join_df[TOTAL_DISTANCE] = model_weights[0] * join_df[IND_DISTANCE] \
                                  + model_weights[1] * join_df[DES_DISTANCE] \
                                  + model_weights[2] * join_df[GS_DISTANCE] \
                                  + model_weights[3] * join_df[GPS_DISTANCE]
        join_df = join_df.sort_values(TOTAL_DISTANCE).reset_index().head(max_k + 1)

        # result
        if radius:
            res_df = self.df.iloc[join_df[join_df[TOTAL_DISTANCE] <=
                                          radius][COMPETITOR_IDX], :].reset_index()
        else:
            res_df = self.df.iloc[join_df[COMPETITOR_IDX], :].reset_index()
        res_df[IND_DISTANCE] = join_df[IND_DISTANCE]
        res_df[DES_DISTANCE] = join_df[DES_DISTANCE]
        res_df[GS_DISTANCE] = join_df[GS_DISTANCE]
        res_df[GPS_DISTANCE] = join_df[GPS_DISTANCE]
        res_df[TOTAL_DISTANCE] = join_df[TOTAL_DISTANCE]
        res_df = res_df[res_df[COMPANY_ID] != id].head(max_k)
        return res_df

    def save(self, dir_path):
        ind_model_path = os.path.join(dir_path, IND_MODEL_FILENAME)
        des_model_path = os.path.join(dir_path, DES_MODEL_FILENAME)

        df_path = os.path.join(dir_path, VECTOR_DATA_FILENAME)
        self.ind_neigh_model.save(ind_model_path)
        self.des_neigh_model.save(des_model_path)
        pickle.dump(self.df[VECTOR_DATA_COLUMNS], open(df_path, 'wb'))

    def load(self, dir_path):
        ind_model_path = os.path.join(dir_path, IND_MODEL_FILENAME)
        des_model_path = os.path.join(dir_path, DES_MODEL_FILENAME)
        df_path = os.path.join(dir_path, VECTOR_DATA_FILENAME)
        self.ind_neigh_model.load(ind_model_path)
        self.des_neigh_model.load(des_model_path)
        self.df = pickle.load(open(df_path, 'rb'))
        self.df[ALL_INDUSTRIES] = self.df[ALL_INDUSTRIES].apply(lambda x: str(x).lower() if not pd.isna(x) else '')
