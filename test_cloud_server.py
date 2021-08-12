import pytest
from flask import Flask, jsonify, request
from pymodm import connect, MongoModel, fields
from pymodm import errors as pymodm_errors
from cloud_server import init_db
from testfixtures import LogCapture
import json
import logging
from datetime import datetime
import numpy as np
from mongodb_class import Patient, MedInfo, MedImg
import uuid


def add_test_patient():
    """Adds a test patient to the database
    """
    Patient(1, "Test").save()
    MedInfo(uuid.uuid1(),
            1,
            60,
            "Test",
            cur_time).save()
    MedImg(uuid.uuid1(),
           1,
           "Test",
           cur_time).save()
    Patient(2, " ").save()
    MedInfo(uuid.uuid1(),
            2,
            60,
            "Test",
            cur_time).save()
    MedImg(uuid.uuid1(),
           2,
           "Test",
           cur_time).save()


def delete_test_patient():
    """Deletes test patient data from database
    """
    try:
        Patient.objects.raw(
            {"username": "Test"}).delete()
    except KeyError or pymodm_errors.DoesNotExist or \
            mongodb_class.DoesNotExist:
        pass
    try:
        MedInfo.objects.raw(
            {"ecg_data": "Test"}).delete()
    except KeyError or pymodm_errors.DoesNotExist or \
            mongodb_class.DoesNotExist:
        pass
    try:
        MedImg.objects.raw(
            {"img_data": "Test"}).delete()
    except KeyError or pymodm_errors.DoesNotExist or \
            mongodb_class.DoesNotExist:
        pass


init_db()
cur_time = datetime(2020, 11, 15, 20, 23, 17)
add_test_patient()


@pytest.mark.parametrize('expected', [
    (1),
    ])
def test_get_id_nums(expected):
    """Test the function to get the list of all
       medical record numbers in database

    Args:
        expected (int): First expected medical nubmer in db
    """
    from cloud_server import get_id_nums
    output, status = get_id_nums()
    answer = output[0]
    assert answer == expected


@pytest.mark.parametrize('patient_id, expected', [
    (1, "Test"),
    (101, False),
    ])
def test_find_correct_patient(patient_id, expected):
    """For a given patient ID, find the patient object in database

    Args:
        patient_id (int): patient ID
        expected (str): Name of found patient
    """
    from cloud_server import find_correct_patient
    output, status = find_correct_patient(patient_id)
    if output is not False:
        answer = output.username
    else:
        answer = output
    assert answer == expected


@pytest.mark.parametrize('patient_id, expected', [
    (1, 60),
    (101, False),
    ])
def test_get_recent_info(patient_id, expected):
    """Get most recent patient information for a given patient ID

    Args:
        patient_id (int): patient ID
        expected (int): most recent heart rate of given patient
    """
    from cloud_server import get_recent_info
    output, status = get_recent_info(patient_id)
    if output is not False:
        answer = output.heart_rate
    else:
        answer = output
    assert answer == expected


@pytest.mark.parametrize('patient_id, expected', [
    (1, cur_time.strftime("%b %d %Y %H:%M:%S")),
    (101, False),
    ])
def test_get_patient_ecgs(patient_id, expected):
    """Get a list of ECGs for a given patient

    Args:
        patient_id (int): patient ID
        expected (str): string of datetime of most recent ECG
    """
    from cloud_server import get_patient_ecgs
    output, status = get_patient_ecgs(patient_id)
    if output is not False:
        answer = output[0]
    else:
        answer = output
    assert answer == expected


@pytest.mark.parametrize('patient_id, date_time, expected', [
    (1, cur_time, "Test"),
    (1, cur_time.replace(day=2), False),
    (101, cur_time, False),
    ])
def test_get_ecg(patient_id, date_time, expected):
    """Get the specific ECG for a given patient and date/time

    Args:
        patient_id (int): patient ID
        date_time (datetime object): datetime of selected ECG
        expected (str): encoded ECG trace string
    """
    from cloud_server import get_ecg
    answer, status = get_ecg(patient_id, date_time)
    assert answer == expected


@pytest.mark.parametrize('in_data, expected_keys, expected_types, expected', [
    ({"name": "Test",
      "med_num": 1,
      "heart_rate": 60,
      "ecg_trace": "Test",
      "med_image": "Test",
      },
     ["name", "med_num", "heart_rate", "ecg_trace", "med_image"],
     [str, int, int, str, str], 200),
    ({"name": "Test",
      "mel_num": 1,
      "heart_rate": 60,
      "ecg_trace": "Test",
      "med_image": "Test",
      },
     ["name", "med_num", "heart_rate", "ecg_trace", "med_image"],
     [str, int, int, str, str], 400),
    ({"name": "Test",
      "mel_num": 1,
      "heart_rate": 60,
      "ecg_trace": 4,
      "med_image": "Test",
      },
     ["name", "med_num", "heart_rate", "ecg_trace", "med_image"],
     [str, int, int, str, str], 400),
    ({"name": "Test",
      "med_num": 1,
      "heart_rate": 60,
      "ecg_trace": "Test",
      "med_image": 4,
      },
     ["name", "med_num", "heart_rate", "ecg_trace", "med_image"],
     [str, int, int, str, str], 400),
    ])
def test_validate_data(in_data, expected_keys, expected_types, expected):
    """Validates input data from patient station GUI

    Args:
        in_data (JSON): JSON of patient data
        expected_keys (list[str]): expected dict keys
        expected_types (list[type]): expect dict value types
        expected (int): expected server status after validation
    """
    from cloud_server import validate_data
    validator, status = validate_data(in_data, expected_keys, expected_types)
    assert status == expected


@pytest.mark.parametrize('patient, in_data', [
    (False,
     {"name": "Test",
      "med_num": 102,
      "heart_rate": 60,
      "ecg_trace": "Test",
      "med_image": "Test",
      }),
    (Patient(2, " "),
     {"name": "Test",
      "med_num": 2,
      "heart_rate": 62,
      "ecg_trace": "Test",
      "med_image": "Test",
      }),
    (Patient(1, "Test"),
     {"name": " ",
      "med_num": 1,
      "heart_rate": 61,
      "ecg_trace": "Test",
      "med_image": "Test",
      }),
    ])
def test_add_patient_to_database(patient, in_data):
    """Takes a JSON and adds the patient to the database

    Args:
        patient (Patient object): Patient object if patient already exists
        in_data (JSON): patient data from patient station GUI
    """
    from cloud_server import add_patient_to_database
    output, status = add_patient_to_database(patient, in_data)
    answer = output.patient_id
    Patient.objects.raw({"username": output.username}).first().delete()
    assert answer == in_data["med_num"]


@pytest.mark.parametrize('in_data, cur_time, expected', [
    ({"name": "Test",
      "med_num": 1,
      "heart_rate": 50,
      "ecg_trace": "Test",
      "med_image": "Test",
      }, datetime.now().replace(microsecond=0), "Test"),
    ({"name": "Test",
      "med_num": 1,
      "heart_rate": 0,
      "ecg_trace": "",
      "med_image": "",
      }, datetime.now().replace(microsecond=0), False),
    ({"name": " ",
      "med_num": 1,
      "heart_rate": 60,
      "ecg_trace": "Test",
      "med_image": "",
      }, datetime.now().replace(microsecond=0), "Test"),
    ])
def test_add_medinfo_to_database(in_data, cur_time, expected):
    """Adds ECG data to database for given patient

    Args:
        in_data (JSON): patient data including ECG data
        cur_time (datetime object): the date/time at upload
        expected (str): encoded ECG string for given patient
    """
    from cloud_server import add_medinfo_to_database
    output, status = add_medinfo_to_database(in_data, cur_time)
    if output is False:
        answer = output
    else:
        answer = output.ecg_data
        MedInfo.objects.raw(
            {"patient_id": in_data["med_num"],
             "date_time": cur_time}).first().delete()
    assert answer == expected


@pytest.mark.parametrize('in_data, cur_time, expected', [
    ({"name": "Test",
      "med_num": 1,
      "heart_rate": 60,
      "ecg_trace": "Test",
      "med_image": "Test",
      }, datetime.now().replace(microsecond=0), "Test"),
    ({"name": "Test",
      "med_num": 2,
      "heart_rate": 0,
      "ecg_trace": "",
      "med_image": "",
      }, datetime.now().replace(microsecond=0), False),
    ({"name": "",
      "med_num": 2,
      "heart_rate": 0,
      "ecg_trace": "",
      "med_image": "Test",
      }, datetime.now().replace(microsecond=0), "Test"),
    ])
def test_add_medimg_to_database(in_data, cur_time, expected):
    """Adds medical image to database for given patient

    Args:
        in_data (JSON): patient data including encoded medical image
        cur_time (datetime object): the date/time at upload
        expected (str): encoded medical image string for given patient
    """
    from cloud_server import add_medimg_to_database
    output, status = add_medimg_to_database(in_data, cur_time)
    if output is False:
        answer = output
    else:
        answer = output.img_data
        MedImg.objects.raw(
            {"patient_id": in_data["med_num"],
             "date_time": cur_time}).first().delete()
    assert answer == expected


@pytest.mark.parametrize('patient_id, expected', [
    (1, ('root', 'INFO', 'Loaded patient information')),
    ])
def test_get_recent_info_log_made(patient_id, expected):
    """Check if a log is made when patient data is loaded

    Args:
        patient_id (int): patient ID
        expected (log): expected log to be made
    """
    from cloud_server import get_recent_info
    with LogCapture() as log_c:
        get_recent_info(patient_id)
    log_c.check(expected)


@pytest.mark.parametrize('patient_id', [
    (-6),
    ])
def test_get_recent_info_log_made(patient_id):
    """Check if a log is made when patient data is loaded

    Args:
        patient_id (int): patient ID
    """
    from cloud_server import get_recent_info
    with LogCapture() as log_c:
        get_recent_info(patient_id)
    log_c.check()


@pytest.mark.parametrize('in_data, expected', [
    ({"name": "Test",
      "med_num": 5,
      "heart_rate": 94,
      "ecg_trace": "Test",
      "med_image": "Test",
      }, ('root', 'INFO', 'Patient data added to database')),
    ])
def test_process_patient_data_log_made(in_data, expected):
    """Check if a log is made when data uploaded from patient GUI is processed

    Args:
        in_data (JSON): uploaded patient data
        expected (log): expected log to be made
    """
    from cloud_server import process_patient_data
    with LogCapture() as log_c:
        process_patient_data(in_data)
    log_c.check(expected)


@pytest.mark.parametrize('in_data', [
    ({"name": "Test",
      "med_num": 1,
      "heart_rate": 60,
      "ecg_trice": "Test",
      "med_image": "Test",
      }),
    ({"name": "Test",
      "med_num": 1,
      "heart_rate": 60,
      "ecg_trace": 60,
      "med_image": "Test",
      }),
    ({"name": "Test",
      "med_num": 1,
      "heart_rate": 60,
      "ec_trace": "Test",
      "med_image": "Test",
      }),
    ])
def test_process_patient_data_log_not_made(in_data):
    """Check if a log is not made when data uploaded from patient
       GUI is processed and determined to be invalid

    Args:
        in_data (JSON): uploaded patient data
    """
    from cloud_server import process_patient_data
    with LogCapture() as log_c:
        process_patient_data(in_data)
        delete_test_patient()
    log_c.check()
