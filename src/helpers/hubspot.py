from hubspot import HubSpot
from .oauth import refresh_and_get_access_token, authorize_and_get_access_token, is_authorized


def create_client(code=None):
    if is_authorized():
        return HubSpot(access_token=refresh_and_get_access_token())
    elif code:
        return HubSpot(access_token=authorize_and_get_access_token(code))
    return HubSpot()
