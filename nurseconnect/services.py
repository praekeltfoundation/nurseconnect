import logging
import requests

from django.conf import settings

logger = logging.getLogger("nurseconnect.services")


def get_clinic_code(clinic_code):
    url = settings.CLINIC_CODE_API
    try:
        response = requests.get(url)
    except requests.RequestException as e:
        logger.error("Error: {}".format(e))
        return None

    if response.status_code == 200:
        try:
            data = response.json()
            logger.info("Obtained clinic code data from API")
        except ValueError as e:
            logger.error("JSON Error: {}".format(e))
            return None

        if data and ("rows" in data):
            for clinic in data["rows"]:
                if clinic_code == clinic[0]:
                    return clinic
    else:
        logger.error("Error: Status code {}".format(response.status_code))
    return None
