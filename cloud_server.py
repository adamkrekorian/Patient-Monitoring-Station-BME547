from flask import Flask, jsonify, request
import requests
import json
import logging
from pymodm import connect, MongoModel, fields
from pymodm import errors as pymodm_errors
from mongodb_class import Patient, MedInfo, MedImg
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import uuid


app = Flask(__name__)


def init_db():
    """ Initializes database and connects to MongoDB

    Args:

    Returns:

    """
    logging.basicConfig(filename="patient-monitor.log", filemode='w',
                        level=logging.DEBUG)
    print("Connecting to MongoDB...")
    connect("mongodb+srv://adam-kaan:joshallen@bme547.hqjsx.mongodb.net/"
            "ecg_db?retryWrites=true&w=majority")
    print("Connected")
    logging.info("Connected to database")


def get_id_nums():
    """ Get all medical record numbers in database

    Returns:
        (list): list of medical record numbers
        (int): status code

    """
    try:
        db_item = Patient.objects.all().order_by([("_id", 1)])
    except pymodm_errors.DoesNotExist:
        return False, 400
    out_data = list()
    for entry in db_item:
        out_data.append(entry.patient_id)
    logging.info("Recieved medical record numbers")
    return out_data, 200


def find_correct_patient(patient_id):
    """ Finds patient from patient_id

    Args:
        patient_id (int): unique patient identifier

    Returns:
        (pymodm object): Patient in database with corresponding id

    """
    try:
        db_item = Patient.objects.raw({"_id": patient_id}).first()
    except pymodm_errors.DoesNotExist:
        return False, 400
    return db_item, 200


def get_recent_info(patient_id):
    """ Find most recent medical info for given patient ID

    Args:
        patient_id (int): unique patient identifier

    Returns:
        (pymodm object): most recent HR measurement in database for patient

    """
    try:
        db_item = MedInfo.objects.raw(
            {"patient_id": patient_id}).order_by([("date_time", -1)]).first()
    except pymodm_errors.DoesNotExist:
        return False, 400
    logging.info("Loaded patient information")
    return db_item, 200


def get_patient_ecgs(patient_id):
    """ Get list of ECG entries for given patient ID

    Args:
        patient_id (int): unique patient identifier

    Returns:
        (list[str]): list of ECG datetimes in database for given patient

    """
    try:
        db_item = MedInfo.objects.raw(
            {"patient_id": patient_id}).all().order_by([("date_time", -1)])
    except pymodm_errors.DoesNotExist:
        return False, 400
    out_data = list()
    for entry in db_item:
        x = entry.date_time.strftime("%b %d %Y %H:%M:%S")
        out_data.append(x)
    if out_data == []:
        return False, 400
    logging.info("Recieved patient ECG datetimes")
    return out_data, 200


def get_ecg(patient_id, date_time):
    """ Finds specific ECG data for given patient ID and date/time

    Args:
        patient_id (int): unique patient identifier
        date_time (str): date/time string

    Returns:
        (pymodm object): specific ECG database entry

    """
    try:
        db_item = MedInfo.objects.raw(
            {"patient_id": patient_id, "date_time": date_time}).first()
    except pymodm_errors.DoesNotExist:
        print("ecg not found")
        return False, 400
    out_data = db_item.ecg_data
    logging.info("Loaded specific patient ECG")
    return out_data, 200


def get_patient_imgs(patient_id):
    """ Get list of Image entries for given patient ID

    Args:
        patient_id (int): unique patient identifier

    Returns:
        (list[str]): list of image datetimes in database for given patient

    """
    try:
        db_item = MedImg.objects.raw(
            {"patient_id": patient_id}).all().order_by([("date_time", -1)])
    except pymodm_errors.DoesNotExist:
        return False, 400
    out_data = list()
    for entry in db_item:
        x = entry.date_time.strftime("%b %d %Y %H:%M:%S")
        out_data.append(x)
    if out_data == []:
        return False, 400
    logging.info("Recieved patient image datetimes")
    return out_data, 200


def get_img(patient_id, date_time):
    """ Finds specific image for given patient ID and date/time

    Args:
        patient_id (int): unique patient identifier
        date_time (str): date/time string

    Returns:
        (pymodm object): specific image in database

    """
    try:
        db_item = MedImg.objects.raw(
            {"patient_id": patient_id, "date_time": date_time}).first()
    except pymodm_errors.DoesNotExist:
        print("img not found")
        return False, 400
    out_data = db_item.img_data
    logging.info("Loaded specific medical image")
    return out_data, 200


def validate_data(in_data, expected_keys, expected_types):
    """ Validates the data

    The validate_data function takes in the input data and checks to make
    sure there are no missing values or incorrect data types

    Args:
        in_data (JSON): input data as a JSON/dictionary file
        expected_keys (list): list of expected data keys
        expected_types (list): list of expected data types

    Returns:
        (boolean): data is valid or not
        (int): status code

    """
    for key in expected_keys:
        if key not in in_data.keys():
            return "{} key not found in input".format(key), 400
    for i, data in enumerate(in_data.values()):
        if type(data) is not expected_types[i]:
            return "Incorrect input type for {}".format(data), 400
    return True, 200


def process_patient_data(in_data):
    """ Processes new patient data for database

    This function checks the validity of the data recieved,
    and adds the data to the corresponding collections in
    the database

    Args:
        in_data(JSON): input data file

    Returns:
        (str): status message
        (int): status code

    """
    expected_keys = ["name", "med_num", "heart_rate", "ecg_trace", "med_image"]
    expected_types = [str, int, int, str, str]
    valid_data, status = validate_data(in_data, expected_keys, expected_types)
    if status == 400:
        return valid_data, status
    patient, status = find_correct_patient(in_data["med_num"])
    patient, status = add_patient_to_database(patient, in_data)
    cur_time = datetime.now().replace(microsecond=0)
    medinfo, status = add_medinfo_to_database(in_data, cur_time)
    medimg, status = add_medimg_to_database(in_data, cur_time)
    logging.info("Patient data added to database")
    return "Patient data sucessfully added", 200


def add_patient_to_database(patient, in_data):
    """ Adds the patient to the database

    Add the specified patient informtation to the database.
    Updates the patient name if they did not have a registered
    name beforehand

    Args:
        patient (pymodm object): Patient object
        in_data (JSON): patient information

    Returns:
        (pymodm object): Patient object in database
        (int): server status

    """
    if patient is False:
        patient = Patient(in_data["med_num"], in_data["name"])
        patient.save()
    else:
        if (patient.username == " ") and (in_data["name"] is not " "):
            patient.username = in_data["name"]
            patient.save()
    return patient, 200


def add_medinfo_to_database(in_data, cur_time):
    """ Adds patient HR and ECG data to the database

    Args:
        in_data (JSON): patient information
        cur_time (datetime object): datetime object at time of upload

    Returns:
        (pymodm object): MedInfo object in database
        (int): status code

    """
    if in_data["heart_rate"] is not 0:
        medinfo = MedInfo(uuid.uuid1(),
                          in_data["med_num"],
                          in_data["heart_rate"],
                          in_data["ecg_trace"],
                          cur_time)
        medinfo.save()
        return medinfo, 200
    return False, 400


def add_medimg_to_database(in_data, cur_time):
    """ Adds patient medical image to the database

    Args:
        in_data (JSON): patient information
        cur_time (datetime object): datetime object at time of upload

    Returns:
        (pymodm object): MedImg object in database
        (int): status code

    """
    if in_data["med_image"] is not "":
        medimg = MedImg(uuid.uuid1(),
                        in_data["med_num"],
                        in_data["med_image"],
                        cur_time)
        medimg.save()
        return medimg, 200
    return False, 400


@app.route("/api/get_patient_ids", methods=["GET"])
def get_patient_ids():
    """ Gets a list of patient IDs from database

    Returns:
        (JSON): JSON with patiend IDs
        (int): status code

    """
    numbers, status = get_id_nums()
    out_dict = {"patient_ids": numbers}
    return jsonify(out_dict), status


@app.route("/api/get_patient_info/<patient_id>", methods=["GET"])
def get_patient_info(patient_id):
    """ Gets all the most recently uploaded patient information

    Returns:
        (JSON): JSON with most recent patient data
        (int): status code

    """
    p_id = int(patient_id)
    patient, status = find_correct_patient(p_id)
    if patient is False:
        return False, 400
    medinfo, status = get_recent_info(p_id)
    if medinfo is False:
        hr_out = 0
        ecg_out = ""
        datetime_out = ""
    else:
        hr_out = medinfo.heart_rate
        ecg_out = medinfo.ecg_data
        datetime_out = medinfo.date_time
    out_dict = {"p_id": patient_id,
                "name": patient.username,
                "hr": hr_out,
                "ecg": ecg_out,
                "datetime": datetime_out,
                }
    return jsonify(out_dict), 200


@app.route("/api/get_ecg_datetimes/<patient_id>", methods=["GET"])
def get_ecg_datetimes(patient_id):
    """ Gets a list of ECGS for a given patient from the database

    Returns:
        (JSON): JSON with list of ECG datetimes
        (int): status code

    """
    p_id = int(patient_id)
    data, status = get_patient_ecgs(p_id)
    if data is False:
        return data, status
    out_dict = {"date_times": data}
    return jsonify(out_dict), 200


@app.route("/api/get_specific_ecg/<patient_id>/<date_time>", methods=["GET"])
def get_specific_ecg(patient_id, date_time):
    """ Gets a specific ECG trace for a patient

    Returns:
        (JSON): JSON with encoded image data of ECG trace
        (int): status code

    """
    p_id = int(patient_id)
    date = datetime.strptime(date_time, "%b %d %Y %H:%M:%S")
    data, status = get_ecg(p_id, date)
    if data is False:
        return False, 400
    out_dict = {"ecg": data}
    return jsonify(out_dict), 200


@app.route("/api/add_patient_data/", methods=["POST"])
def add_patient_data():
    """ Makes a post request to add patient data to the database

    Returns:
        (str): status message
        (int): status code

    """
    in_data = request.get_json()
    answer, server_status = process_patient_data(in_data)
    return answer, server_status


@app.route("/api/get_img_datetimes/<patient_id>", methods=["GET"])
def get_img_datetimes(patient_id):
    """ Gets a list of images for a given patient from the database

    Returns:
        (JSON): JSON with list of image datetimes
        (int): status code

    """
    p_id = int(patient_id)
    data, status = get_patient_imgs(p_id)
    if data is False:
        return data, status
    out_dict = {"date_times": data}
    return jsonify(out_dict), 200


@app.route("/api/get_specific_img/<patient_id>/<date_time>", methods=["GET"])
def get_specific_img(patient_id, date_time):
    """ Gets a specific ECG trace for a patient

    Returns:
        (JSON): JSON with encoded image data of ECG trace
        (int): status code

    """
    p_id = int(patient_id)
    date = datetime.strptime(date_time, "%b %d %Y %H:%M:%S")
    data, status = get_img(p_id, date)
    if data is False:
        return False, 400
    out_dict = {"img": data}
    return jsonify(out_dict), 200


if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=5000)
