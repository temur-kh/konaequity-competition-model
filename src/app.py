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
    model = CompetitionModel()
    model.fit(df)
    print('Model fitting completed:', time.time() - start)
    start = time.time()
    model.save('./')
    print('Model saving completed:', time.time() - start)


def update_fields(thread_id, model, start, end):
    print(f'Thread: {thread_id} has started')
    start_time = time.time()
    batch_input_list = []
    for cnt, id in enumerate(model.df[COMPANY_ID].values[start:end]):
        res_df = model.find_competitors(id=id, max_k=6)
        competitors = res_df.to_dict('records')
        properties = {}
        for i, comp in enumerate(competitors):
            if not pd.isna(comp[COMPANY_ID]):
                properties[f'competitor_{i + 1}_id'] = str(comp[COMPANY_ID])
            if not pd.isna(comp[COMPANY_DOMAIN_NAME]):
                properties[f'competitor_{i + 1}_domain_name'] = comp[COMPANY_DOMAIN_NAME]
            if not pd.isna(comp[TOTAL_DISTANCE]):
                properties[f'competitor_{i + 1}_distance'] = str(round(comp[TOTAL_DISTANCE], 2))
        batch_input = SimplePublicObjectBatchInput(id=str(id), properties=properties)
        batch_input_list.append(batch_input)
        if len(batch_input_list) == 100:
            batch_inputs = BatchInputSimplePublicObjectBatchInput(batch_input_list)
            hubspot = create_client()
            hubspot.crm.companies.batch_api.update(batch_inputs)
            batch_input_list = []
            print(f'Thread: {thread_id}, Breakpoint: {start + cnt}, Time: {time.time() - start_time}')
            start_time = time.time()

    if len(batch_input_list):
        hubspot = create_client()
        batch_inputs = BatchInputSimplePublicObjectBatchInput(batch_input_list)
        hubspot.crm.companies.batch_api.update(batch_inputs)
        print(f'Thread: {thread_id}, Breakpoint: {end - 1}, Time: {time.time() - start_time}')


if __name__ == '__main__':
    create_client('code')
    build_models()
    model = CompetitionModel()
    model.load('./')
    update_fields(0, model, start=0, end=1150000)
    # step = 143750
    # threads = []
    # thread_info = [(step*8-10000, step*8-7500), (step*8-7500, step*8-5000), (step*8-5000, step*8-2500), (step*8-2500, step*8)]
    # for i in range(3):
    #     thread = threading.Thread(target=update_fields, args=(i, model, thread_info[i][0], thread_info[i][1]))
    #     thread.start()
    #     threads.append(thread)
    # update_fields(3, model, start=thread_info[3][0], end=thread_info[3][1])
    # for thread in threads:
    #     thread.join()
    print('Application completed!')
