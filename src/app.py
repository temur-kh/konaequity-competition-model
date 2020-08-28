import time
import threading

import pandas as pd
from hubspot.crm.companies import BatchInputSimplePublicObjectBatchInput, SimplePublicObjectBatchInput

from service import Preprocessor, Vectorizer, CompetitionModel
from service.constants import *
from helpers.hubspot import create_client

pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None


def build_models():
    start = time.time()
    df = pd.read_csv(DATASET_PATH)
    df = Preprocessor().apply(df)
    print('Preprocessing completed:', time.time() - start)
    start = time.time()
    df = Vectorizer().apply(df)
    print('Vectorization completed:', time.time() - start)
    start = time.time()
    model = CompetitionModel(n_jobs=1)
    model.fit(df)
    print('Model fitting completed:', time.time() - start)
    start = time.time()
    model.save('./')
    print('Model saving completed:', time.time() - start)


def update_fields(thread_id, start, end):
    start_time = time.time()
    model = CompetitionModel(n_jobs=1)
    model.load('./')
    print(f'Thread: {thread_id}, Model loading completed:', time.time() - start_time)
    start_time = time.time()
    batch_input_list = []
    stats = STATS_DICT
    for cnt, id in enumerate(model.df[COMPANY_ID].values[start:end]):
        res_df, stats = model.find_competitors(id=id, max_k=6, stats=stats)
        competitors = res_df.to_dict('records')
        properties = {}
        for i, comp in enumerate(competitors):
            if not pd.isna(comp[COMPANY_ID]):
                properties[f'competitor_{i+1}_id'] = str(comp[COMPANY_ID])
            if not pd.isna(comp[COMPANY_DOMAIN_NAME]):
                properties[f'competitor_{i+1}_domain_name'] = comp[COMPANY_DOMAIN_NAME]
            if not pd.isna(comp[TOTAL_DISTANCE]):
                properties[f'competitor_{i+1}_distance'] = str(round(comp[TOTAL_DISTANCE], 2))
        batch_input = SimplePublicObjectBatchInput(id=str(id), properties=properties)
        batch_input_list.append(batch_input)
        if len(batch_input_list) == 100:
            # batch_inputs = BatchInputSimplePublicObjectBatchInput(batch_input_list)
            # hubspot = create_client()
            # hubspot.crm.companies.batch_api.update(batch_inputs)
            batch_input_list = []
            print(f'Thread: {thread_id}, Breakpoint: {start+cnt}, Time: {time.time()-start_time}')
            print(stats)
            stats = STATS_DICT
            start_time = time.time()

    if len(batch_input_list):
        # hubspot = create_client()
        # batch_inputs = BatchInputSimplePublicObjectBatchInput(batch_input_list)
        # hubspot.crm.companies.batch_api.update(batch_inputs)
        print(f'Thread: {thread_id}, Breakpoint: {end-1}, Time: {time.time()-start_time}')


if __name__ == '__main__':
    # create_client('83ddd090-a3c0-41ae-8464-9fa00cded9c9')
    build_models()
    update_fields(0, start=0, end=300000)
    # threads = []
    # for i in range(1, 2):
    #     thread = threading.Thread(target=update_fields, args=(i, 0, 300000))
    #     thread.start()
    #     threads.append(thread)
    # for thread in threads:
    #     thread.join()
    print('Application completed!')
