import time
from hubspot import HubSpot

TOKENS_KEY = "tokens"

session = {}


def save_tokens(tokens_response):
    tokens = {
        "access_token": tokens_response.access_token,
        "refresh_token": tokens_response.refresh_token,
        "expires_in": tokens_response.expires_in,
        "expires_at": time.time() + tokens_response.expires_in * 0.95,
    }
    session[TOKENS_KEY] = tokens

    return tokens


def is_authorized():
    return TOKENS_KEY in session


def get_redirect_uri():
    return 'https://webhook.site/04fa0395-70de-4a6c-b460-188427746700'


def authorize_and_get_access_token(code):
    tokens = HubSpot().auth.oauth.default_api.create_token(
        grant_type='authorization_code',
        code=code,
        redirect_uri=get_redirect_uri(),
        client_id='c885f5ca-1b64-4db0-8e16-20cba5731920',
        client_secret='dd52cc93-be2c-4f2d-8a32-715270178715'
    )
    print(tokens)
    tokens = save_tokens(tokens)
    return tokens['access_token']


def refresh_and_get_access_token():
    if TOKENS_KEY not in session:
        raise Exception("No refresh token is specified")
    tokens = session[TOKENS_KEY]
    if time.time() > tokens["expires_at"]:
        tokens = HubSpot().auth.oauth.default_api.create_token(
            grant_type="refresh_token",
            redirect_uri=get_redirect_uri(),
            refresh_token=tokens["refresh_token"],
            client_id='c885f5ca-1b64-4db0-8e16-20cba5731920',
            client_secret='dd52cc93-be2c-4f2d-8a32-715270178715',
        )
        tokens = save_tokens(tokens)

    return tokens["access_token"]
