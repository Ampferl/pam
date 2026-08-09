import garminconnect
from django.conf import settings


def get_client():
    client = garminconnect.Garmin(settings.GARMIN_EMAIL, settings.GARMIN_PASSWORD)
    try:
        client.login(settings.GARMIN_TOKENSTORE)
    except Exception:
        client.login()
        client.garth.dump(settings.GARMIN_TOKENSTORE)
    return client
