import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import requests
from datetime import datetime
import json
import matplotlib.pyplot as plt
import io
import base64
import matplotlib.image as mpimg


def design_window():
    """Initializes the Monitoring Station GUI
    """

    def refresh():
        """Refreshes the Monitoring Station every 30 seconds,
           checking for new patients and new patient data
        """
        global last_pid
        r = requests.get(
            "http://vcm-17475.vm.duke.edu:5000/api/get_patient_ids")
        try:
            data = r.json()
            patient_ids = data["patient_ids"]
            patient_id_combo['values'] = patient_ids
        except ValueError:
            patient_ids = 'No patients in Database'
        r = requests.get("http://vcm-17475.vm.duke.edu:5000"
                         "/api/get_patient_info/{}".format(last_pid))
        try:
            in_data = r.json()
        except ValueError:
            in_data = False
        if in_data is False:
            medical_num_val.config(text="n/a")
            name_val.config(text="patient not found")
            ecg_img_label.configure(image=None)
        else:
            if in_data["datetime"] != last_date:
                hr_val.config(text=in_data["hr"])
                date_val.config(text=in_data["datetime"])
                filename = save_b64_image(in_data["ecg"])
                pil_image = Image.open(filename)
                image_size = pil_image.size
                adj_factor = 0.15
                pil_image = pil_image.resize((int(image_size[0]*adj_factor),
                                              int(image_size[1]*adj_factor)))
                tk_image = ImageTk.PhotoImage(pil_image)
                ecg_img_label.image = tk_image
                ecg_img_label.configure(image=tk_image)
        root.after(30000, refresh)

    def ok_btn_cmd():
        """Loads patient data for selected patient when the ok button
           is clicked.
        """
        global last_pid
        global last_date
        r = requests.get(
            "http://vcm-17475.vm.duke.edu:5000/api/get_patient_info/{}".format(
                patient_id.get()))
        try:
            in_data = r.json()
        except ValueError:
            in_data = False
        if in_data is False:
            medical_num_val.config(text="n/a")
            name_val.config(text="patient not found")
            ecg_img_label.configure(image=None)
        else:
            last_pid = in_data["p_id"]
            last_date = in_data["datetime"]
            medical_num_val.config(text=in_data["p_id"])
            name_val.config(text=in_data["name"])
            hr_val.config(text=in_data["hr"])
            date_val.config(text=in_data["datetime"])
            if in_data["ecg"] == "":
                ecg_img_label.configure(image="")
                ecg_img2_label.configure(image="")
                med_img_label.configure(image="")
            else:
                filename = save_b64_image(in_data["ecg"])
                pil_image = Image.open(filename)
                image_size = pil_image.size
                adj_factor = 0.15
                pil_image = pil_image.resize((int(image_size[0]*adj_factor),
                                              int(image_size[1]*adj_factor)))
                tk_image = ImageTk.PhotoImage(pil_image)
                ecg_img_label.image = tk_image
                ecg_img_label.configure(image=tk_image)
                ecg_img2_label.configure(image="")
                med_img_label.configure(image="")

    def cancel_btn_cmd():
        """Closes the Monitoring Station window
        """
        root.destroy()

    def select_ecg_btn_cmd():
        """Opens a popupwindow to select an ECG for a given patient
        """

        def ok_ecg_btn_cmd():
            """Displays the selected ECG in the main window
            """
            r = requests.get(
                "http://vcm-17475.vm.duke.edu:5000"
                "/api/get_specific_ecg/{}/{}".format(
                    last_pid, ecg_datetime.get()))
            try:
                in_data = r.json()
            except ValueError:
                in_data = False
            if in_data is False:
                print("no ecg data for that patinet/date")
                ecg_img2_label.configure(image=None)
                select_ecg_window.destroy()
            else:
                global ecg_filename
                ecg_filename = save_b64_image(in_data["ecg"])
                pil_image = Image.open(ecg_filename)
                image_size = pil_image.size
                adj_factor = 0.15
                pil_image = pil_image.resize((int(image_size[0]*adj_factor),
                                              int(image_size[1]*adj_factor)))
                tk_image = ImageTk.PhotoImage(pil_image)
                ecg_img2_label.image = tk_image
                ecg_img2_label.configure(image=tk_image)
                select_ecg_window.destroy()
        global last_pid
        r = requests.get(
            "http://vcm-17475.vm.duke.edu:5000"
            "/api/get_ecg_datetimes/{}".format(last_pid))
        try:
            in_data = r.json()
        except ValueError:
            in_data = {"date_times": "No Images Available"}
        select_ecg_window = tk.Toplevel()
        select_ecg_window.wm_title("ECG Selector")
        top_ecg_label = ttk.Label(select_ecg_window,
                                  text="Select an ECG Image",
                                  font=my_font)
        top_ecg_label.grid(column=0, row=0, columnspan=2)

        ecg_datetime = tk.StringVar()
        ecg_datetime_combo = ttk.Combobox(select_ecg_window,
                                          textvariable=ecg_datetime,
                                          width=15)
        ecg_datetime_combo.grid(column=0, row=1)
        ecg_datetime_combo['values'] = in_data["date_times"]
        ecg_datetime_combo.state(['readonly'])

        ok_ecg_btn = ttk.Button(select_ecg_window,
                                text="Okay",
                                command=ok_ecg_btn_cmd)
        ok_ecg_btn.grid(column=0, row=2)

    def download_ecg_btn_cmd():
        global ecg_filename
        img = Image.open(ecg_filename)
        ecg_file = filedialog.asksaveasfile(mode='w', defaultextension=".jpg")
        if ecg_file:
            img.save(ecg_file)

    def select_img_btn_cmd():
        """Opens a popupwindow to select a medical image for a given patient
        """

        def ok_img_btn_cmd():
            """Displays the selected image in the main window
            """
            r = requests.get(
                "http://vcm-17475.vm.duke.edu:5000"
                "/api/get_specific_img/{}/{}".format(
                    last_pid, img_datetime.get()))
            try:
                in_data = r.json()
            except ValueError:
                in_data = False
            if in_data is False:
                print("no image for that patinet/date")
                med_img_label.configure(image=None)
                select_img_window.destroy()
            else:
                global med_filename
                med_filename = save_b64_image(in_data["img"])
                pil_image = Image.open(med_filename)
                image_size = pil_image.size
                adj_factor = 0.3
                pil_image = pil_image.resize((int(image_size[0]*adj_factor),
                                              int(image_size[1]*adj_factor)))
                tk_image = ImageTk.PhotoImage(pil_image)
                med_img_label.image = tk_image
                med_img_label.configure(image=tk_image)
                select_img_window.destroy()

        global last_pid
        r = requests.get(
            "http://vcm-17475.vm.duke.edu:5000"
            "/api/get_img_datetimes/{}".format(last_pid))
        try:
            in_data = r.json()
        except ValueError:
            in_data = {"date_times": "No Images Available"}
        select_img_window = tk.Toplevel()
        select_img_window.wm_title("Image Selector")
        top_img_label = ttk.Label(select_img_window,
                                  text="Select a Medical Image",
                                  font=my_font)
        top_img_label.grid(column=0, row=0, columnspan=2)

        img_datetime = tk.StringVar()
        img_datetime_combo = ttk.Combobox(select_img_window,
                                          textvariable=img_datetime,
                                          width=15)
        img_datetime_combo.grid(column=0, row=1)
        img_datetime_combo['values'] = in_data["date_times"]
        img_datetime_combo.state(['readonly'])

        ok_img_btn = ttk.Button(select_img_window,
                                text="Okay",
                                command=ok_img_btn_cmd)
        ok_img_btn.grid(column=0, row=2)

    def download_img_btn_cmd():
        global med_filename
        img = Image.open(med_filename)
        med_file = filedialog.asksaveasfile(mode='w', defaultextension=".jpg")
        if med_file:
            img.save(med_file)

    r = requests.get("http://vcm-17475.vm.duke.edu:5000/api/get_patient_ids")
    try:
        data = r.json()
        patient_ids = data["patient_ids"]
    except ValueError:
        patient_ids = 'No patients in Database'

    my_font = ("arial", 12)

    root = tk.Tk()
    root.title("Monitor Station GUI")
    root.geometry("900x900+0+0")
    root.columnconfigure(1, weight=3)

    top_label = ttk.Label(root, text="Monitor Station", font=my_font)
    top_label.grid(column=0, row=0, columnspan=2, sticky='w')

    select_patient_label = ttk.Label(root, text="Select Patient:",
                                     font=my_font)
    select_patient_label.grid(column=0, row=1, sticky='w')

    patient_id = tk.StringVar()
    patient_id_combo = ttk.Combobox(root, textvariable=patient_id,
                                    width=10)
    patient_id_combo.grid(column=1, row=1, sticky='w')
    patient_id_combo['values'] = patient_ids
    patient_id_combo.state(['readonly'])

    last_pid = ""
    last_date = ""

    medical_num_label = ttk.Label(root, text="Medical Record Number:",
                                  font=my_font)
    medical_num_label.grid(column=0, row=2, sticky='w')

    medical_num_val = ttk.Label(root, text="", font=my_font)
    medical_num_val.grid(column=1, row=2, sticky='w')

    name_label = ttk.Label(root, text="Patient Name:",
                           font=my_font)
    name_label.grid(column=0, row=3, sticky='w')

    name_val = ttk.Label(root, text="", font=my_font)
    name_val.grid(column=1, row=3, sticky='w')

    hr_label = ttk.Label(root, text="Latest Measured HR:",
                         font=my_font)
    hr_label.grid(column=0, row=4, sticky='w')

    hr_val = ttk.Label(root, text="", font=my_font)
    hr_val.grid(column=1, row=4, sticky='w')

    date_label = ttk.Label(root, text="Date/Time:",
                           font=my_font)
    date_label.grid(column=0, row=5, sticky='w')

    date_val = ttk.Label(root, text="", font=my_font)
    date_val.grid(column=1, row=5, sticky='w')

    ok_btn = ttk.Button(root, text="Okay", command=ok_btn_cmd)
    ok_btn.grid(column=0, row=6)

    cancel_btn = ttk.Button(root, text="Cancel", command=cancel_btn_cmd)
    cancel_btn.grid(column=1, row=6, sticky='w')

    select_ecg_btn = ttk.Button(root, text="Select ECG",
                                command=select_ecg_btn_cmd)
    select_ecg_btn.grid(column=2, row=3)

    download_ecg_btn = ttk.Button(root, text="Download ECG",
                                  command=download_ecg_btn_cmd)
    download_ecg_btn.grid(column=3, row=3)

    select_img_btn = ttk.Button(root, text="Select Image",
                                command=select_img_btn_cmd)
    select_img_btn.grid(column=2, row=7)

    download_img_btn = ttk.Button(root, text="Download Image",
                                  command=download_img_btn_cmd)
    download_img_btn.grid(column=3, row=7)

    ecg_img_label = ttk.Label(root, image=None)
    ecg_img_label.grid(column=2, row=1, rowspan=2)

    ecg_img2_label = ttk.Label(root, image=None)
    ecg_img2_label.grid(column=3, row=1, rowspan=2)
    ecg_filename = ""

    med_img_label = ttk.Label(root, image=None)
    med_img_label.grid(column=2, row=6, columnspan=2, rowspan=1)
    img_filename = ""

    root.after(30000, refresh)
    root.mainloop()
    return


def save_b64_image(base64_string):
    """Decodes a b64-encoded image and saves it locally to disk
       to be displayed in the Monitoring Station GUI

    Args:
        base64_string (str): encoded image string

    Returns:
        (str): filename for decoded image
    """
    image_bytes = base64.b64decode(base64_string)
    with open("temp-img.jpg", "wb") as out_file:
        out_file.write(image_bytes)
    return "temp-img.jpg"


if __name__ == '__main__':
    design_window()
