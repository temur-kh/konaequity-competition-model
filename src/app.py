# from flask import Flask
#
# import routes
#
# # TODO: create API for the application and route requests to specific methods
# # TODO: integrate Hubspot API
#
# app = Flask(__name__)
#
# app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
#
# app.register_blueprint(routes.companies, url_prefix='/companies')
#
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", debug=True)


from hubspot import HubSpot
from hubspot.auth.oauth import ApiException
from hubspot.crm.companies import BatchInputSimplePublicObjectBatchInput, SimplePublicObjectBatchInput

import time
import pickle
import tqdm
import pandas as pd

from service import Preprocessor, Vectorizer, CompetitionModel
from service.constants import *

pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None


hubspot = HubSpot()

try:
    tokens = hubspot.auth.oauth.default_api.create_token(
        grant_type='authorization_code',
        code='b2771e60-6cd3-4939-b4e7-e8b8e62b0237',
        redirect_uri='https://webhook.site/04fa0395-70de-4a6c-b460-188427746700',
        client_id='c885f5ca-1b64-4db0-8e16-20cba5731920',
        client_secret='dd52cc93-be2c-4f2d-8a32-715270178715'
    )
    print(tokens)
except ApiException as e:
    print("Exception when creating contact: %s\n" % e)

hubspot.access_token = tokens.access_token

all_start = time.time()

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

start = time.time()
model = CompetitionModel(n_jobs=1)
model.load('./')
print('Model loading completed:', time.time() - start)
start = time.time()
batch_input_list = []
for id in tqdm.tqdm(model.df[COMPANY_ID].values):
    res_df: pd.DataFrame = model.find_competitors(id=id, max_k=3)
    competitors = res_df.to_dict('records')
    properties = {}
    for i, comp in enumerate(competitors):
        if not pd.isna(comp[COMPANY_ID]):
            properties[f'competitor_{i+1}'] = str(comp[COMPANY_ID])
        if not pd.isna(comp[COMPANY_DOMAIN_NAME]):
            properties[f'competitor_{i+1}_domain_name'] = comp[COMPANY_DOMAIN_NAME]
        if not pd.isna(comp[TOTAL_DISTANCE]):
            properties[f'competitor_{i+1}_distance'] = str(round(comp[TOTAL_DISTANCE], 2))
    batch_input = SimplePublicObjectBatchInput(id=str(id), properties=properties)
    batch_input_list.append(batch_input)
    if len(batch_input_list) == 100:
        batch_inputs = BatchInputSimplePublicObjectBatchInput(batch_input_list)
        hubspot.crm.companies.batch_api.update(batch_inputs)
        batch_input_list = []

if len(batch_input_list):
    batch_inputs = BatchInputSimplePublicObjectBatchInput(batch_input_list)
    hubspot.crm.companies.batch_api.update(batch_inputs)

print('Compeititors construction completed:', time.time() - start)
print('Application completed:', time.time() - all_start)
