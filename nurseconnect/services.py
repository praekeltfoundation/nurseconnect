import logging
import requests

from django.conf import settings

logger = logging.getLogger("nurseconnect.services")


def get_clinic_code(clinic_code):
    url = settings.CLINIC_CODE_API
    response = requests.get(url)
    data = response.json()
    logger.info("Obtained clinic code data from API")

    if data and ("rows" in data):
        for clinic in data["rows"]:
            if clinic_code == clinic[0]:
                return clinic

    return None
