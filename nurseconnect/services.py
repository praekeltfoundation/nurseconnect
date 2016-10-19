import requests

from nurseconnect import settings


def check_clinic_code(clinic_code):
    url = settings.CLINIC_CODE_API
    response = requests.get(url)
    data = response.json()

    for clinic in data["rows"]:
        if clinic_code == clinic[0]:
            return clinic

    return None


def clinic_code_name(clinic_code):
    url = settings.CLINIC_CODE_API
    response = requests.get(url)
    data = response.json()

    for clinic in data["rows"]:
        if clinic_code == clinic[0]:
            return clinic[2]

    return None
