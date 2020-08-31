IND_VECTOR = 'Industries Vector'
DES_VECTOR = 'Description Vector'
GS_VECTOR = 'Gs Vector'
GPS_VECTOR = 'GPS Vector'

IND_VECTOR_SIZE = 140
DES_VECTOR_SIZE = 240
GS_VECTOR_SIZE = 6

IND_N_TREES = 100
DES_N_TREES = 100

COMPANY_ID = 'Company ID'
COMPETITOR_IDX = 'Competitor Index'

IND_DISTANCE = 'Industry Distance'
DES_DISTANCE = 'Description Distance'
GS_DISTANCE = 'Gs Distance'
GPS_DISTANCE = 'GPS Distance'
TOTAL_DISTANCE = 'Total Distance'

COUNTRY_REGION = 'Country/Region'
STATE_REGION = 'State/Region'
CITY = 'City'
DESCRIPTION = 'Description'
LONGER_DESCRIPTION = 'Longer Description'
LINKEDIN_BIO = 'LinkedIn Bio'
INDUSTRY = 'Industry'
CATEGORIES = 'Categories'
LINKEDIN_INDUSTRIES = 'Linkedin industries'
GOOGLE_PLACES_INDUSTRY = 'Google places industry'
COMPANY_DOMAIN_NAME = 'Company Domain Name'

FULL_DESCRIPTION = 'Full Description'
ALL_INDUSTRIES = 'All Industries'

LATITUDE = 'Latitude'
LONGITUDE = 'Longitude'
ADDRESS = 'Address'

USEFUL_COLUMNS = [
    'Company ID',
    'Company Domain Name', 'Country/Region', 'State/Region',
    'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8',
    'LinkedIn Bio', 'Description', 'Longer Description',
    'Google places industry', 'Categories', 'Linkedin industries', 'Industry',
]

VECTOR_DATA_COLUMNS = [
    COMPANY_ID,
    COMPANY_DOMAIN_NAME, ALL_INDUSTRIES,
    IND_VECTOR, DES_VECTOR, GS_VECTOR, GPS_VECTOR
]

# COLUMN_TO_NAME_DICT = {
#     'Company ID': 'id',
#     'Country/Region': 'country',
#     'G1': 'g1', 'G2': 'g2', 'G3': 'g3', 'G4': 'g4', 'G5': 'g5', 'G6': 'g6', 'G7': 'g7', 'G8': 'g8',
#     'LinkedIn Bio': 'linkedinbio', 'Description': 'description',
#     'Google places industry': 'google_places_industry', 'Categories': 'categories',
#     'Linkedin industries': 'linkedin_industries', 'Industry': 'industry'
# }
#
# NAME_TO_COLUMN_DICT = {
#     'id': 'Company ID',
#     'country': 'Country/Region',
#     'g1': 'G1', 'g2': 'G2', 'g3': 'G3', 'g4': 'G4', 'g5': 'G5', 'g6': 'G6', 'g7': 'G7', 'g8': 'G8',
#     'linkedinbio': 'LinkedIn Bio', 'description': 'Description',
#     'google_places_industry': 'Google places industry', 'categories': 'Categories',
#     'linkedin_industries': 'Linkedin industries', 'industry': 'Industry'
# }

DATASET_PATH = './all-companies.csv'
GPS_COORDS_PATH = './gps-coordinates.csv'
LOCATION_INDEPENDENT_INDS_PATH = './location_independent_linkedin_industries.csv'

IND_MODEL_FILENAME = 'neigh-model-by-industries.pkl'
DES_MODEL_FILENAME = 'neigh-model-by-description.pkl'
VECTOR_DATA_FILENAME = 'processed-dataset.pkl'

STATS_DICT = {
    'IND_NEIGH_MODEL': 0,
    'DES_NEIGH_MODEL': 0,
    'GS_NEIGH_MODEL': 0,
    'JOIN_DF_CREATION': 0,
    'TOTAL_DISTANCE_CALC': 0,
    'JOIN_DF_SORTING': 0,
    'DF_ILOC': 0,
    'RES_DF_COLUMNS': 0
}

DEFAULT_COUNTRY = 'United States'
