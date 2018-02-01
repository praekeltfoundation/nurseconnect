import logging
import requests

from django.conf import settings

logger = logging.getLogger("nurseconnect.services")


def get_clinic_code(clinic_code):
    if settings.FAKE_CLINIC_CODE_VALIDATION and settings.DEBUG:
        return [0, 1, "fake_clinic_name"]

    try:
        response = requests.get(
            settings.CLINIC_CODE_API,
            params={"criteria": "value:{}".format(clinic_code)})
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
            if len(data["rows"]) >= 1:
                return data["rows"][0]
            else:
                return None
        else:
            logger.error(
                "Returned data in unexpected format: {}".format(
                    data if data is not None else "None"))
            return None
    else:
        logger.error("Error: Status code {}".format(response.status_code))
    return None
