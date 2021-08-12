import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
from ecg import *
import matplotlib.image as mpimg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import base64
import io
import requests
from matplotlib import pyplot as plt

# Global Variables
image_b64 = ''
ecg_b64 = ''
heart_rate = 0


def design_window():
    """ Creates patient station GUI

    The design_window() function creates the patient-side GUI client so that
    patient information can be entered and uploaded into the server.

    Args:

    Returns:

    """

    def upload_btn_cmd():
        """ Uploads new patient to the server

        The upload_btn_cmd() function uploads the entered patient information
        to the server. It runs when the "Upload" button is selected on the
        patient-side GUI. It uploads the entered information for each patient,
        such as name, medical record number, heart rate, ecg trace, and medical
        image. The upload only occurs if a medical record number is input.

        Args:

        Returns:

        """
        name_output = name.get()
        if name_output == '':
            name_output = ' '

        try:
            med_output = med_num.get()
        except tk.TclError:
            med_output = 0
            print("Incorrect input: medical record number must be integer")
            return

        global heart_rate
        hr_output = heart_rate

        global ecg_b64
        trace_output = ecg_b64

        global image_b64
        image_output = image_b64

        if(med_output == 0):
            print("Medical record number is required for upload")
            return

        new_patient = {"name": name_output,
                       "med_num": med_output,
                       "heart_rate": hr_output,
                       "ecg_trace": trace_output,
                       "med_image": image_output}

        print(hr_output)

        r = requests.post(
            "http://vcm-17475.vm.duke.edu:5000/api/add_patient_data/",
            json=new_patient)

        if r.status_code == 200:
            print("Successfully uploaded patient info!")

        if r.status_code == 400:
            print("Unsuccessful upload")

    def close_btn_cmd():
        """ Terminates the patient-side GUI client

        The close_btn_cmd() is run when the "Close" button is selected on the
        patient-side GUI. It ends the GUI client by calling root.destroy()

        Args:

        Returns:

        """
        root.destroy()

    def image_cmd():
        """ Allows for a medical image to be selected

        The image_cmd() function is run when the "Select Medical Image" button
        is selected on the patient-side GUI. It allows for an image file to be
        selected. This image is displayed on the patient-side once selected. In
        addition, the selected image file is encoded into base64 encoded bytes
        so that it can easily be uploaded to the server.

        Args:

        Returns:

        """
        image_filename = filedialog.askopenfilename()
        pil_image = Image.open(image_filename)
        image_size = pil_image.size
        adj_factor = 0.3
        pil_image = pil_image.resize((int(image_size[0]*adj_factor),
                                      int(image_size[1]*adj_factor)))
        tk_image = ImageTk.PhotoImage(pil_image)
        image_label.image = tk_image
        image_label.configure(image=tk_image)
        image_label.grid(column=2, row=2)

        global image_b64
        image_b64 = read_file_as_b64(image_filename)

    def ecg_cmd():
        """ Allows for an ECG data file to be selected

        The ecg_cmd() is run when the "Select ECG Data" button is selected on
        the patient-side GUI. It allows for an ECG data file to be selected.
        A trace of the selected ECG data is displayed on the patient-side. In
        addition, the heart rate calculated from that ECG trace is displayed
        on the patient-side. Also, the created ECG trace is encoded into base64
        encoded bytes so that it can easily be uploaded to the server.

        Args:

        Returns:

        """
        ecg_filename = filedialog.askopenfilename()
        bpm, time, voltage = calculate_ecg_data(ecg_filename)

        global heart_rate
        heart_rate = int(bpm)

        ecg_hr.configure(text="{}".format(heart_rate))
        ecg_hr.grid(column=1, row=4)

        plt.clf()
        plt.plot(time, voltage)
        plt.xlabel('Time [s]')
        plt.ylabel('Voltage [mV]')
        plt.title('ECG Trace')
        plt.savefig('trace.jpg', dpi=300, bbox_ineches='tight')

        pil_image = Image.open('trace.jpg')
        image_size = pil_image.size
        adj_factor = 0.15
        pil_image = pil_image.resize((int(image_size[0]*adj_factor),
                                      int(image_size[1]*adj_factor)))
        tk_image = ImageTk.PhotoImage(pil_image)
        ecg_label.image = tk_image
        ecg_label.configure(image=tk_image)
        ecg_label.grid(column=1, row=2)

        global ecg_b64
        ecg_b64 = read_file_as_b64("trace.jpg")

    my_font = ("arial", 14)
    underlined_font = ("arial 14 underline")
    bold_font = ("arial 28 bold")

    root = tk.Tk()
    root.title("Patient-side GUI")
    root.geometry("1000x360+0+100")
    root.columnconfigure(1, weight=3)

    top_label = ttk.Label(root, text="Patient Station", font=bold_font)
    top_label.grid(column=0, row=0, columnspan=4)

    name_label = ttk.Label(root, text="Name:", font=my_font)
    name_label.grid(column=0, row=1, sticky='w')

    name = tk.StringVar()
    name_entry = ttk.Entry(root, textvariable=name, font=my_font)
    name_entry.grid(column=1, row=1, sticky='w')

    med_label = ttk.Label(root, text="Medical Record Number:", font=my_font)
    med_label.grid(column=0, row=2, sticky='w')

    med_num = tk.IntVar()
    med_entry = ttk.Entry(root, textvariable=med_num, font=my_font)
    med_entry.grid(column=1, row=2, sticky='w')

    hr_label = ttk.Label(root, text="ECG Heart Rate", font=underlined_font)
    hr_label.grid(column=1, row=3)

    upload_btn = ttk.Button(root, text="Upload", command=upload_btn_cmd)
    upload_btn.grid(column=0, row=4)

    close_btn = ttk.Button(root, text="Close", command=close_btn_cmd)
    close_btn.grid(column=0, row=5)

    img_btn = ttk.Button(root, text="Select Medical Image", command=image_cmd)
    img_btn.grid(column=2, row=1)
    image_label = ttk.Label(root, image=None)

    ecg_btn = ttk.Button(root, text="Select ECG Data", command=ecg_cmd)
    ecg_btn.grid(column=1, row=1)
    ecg_label = ttk.Label(root, image=None)
    ecg_hr = ttk.Label(root, text='', font=my_font)

    root.mainloop()
    return


def read_file_as_b64(image_path):
    """ Encodes input image file into base64 encoded bytes

    The read_file_as_b64() function encodes the input image file into base64
    encoded bytes. It reads in the binary bytes from the input image file and
    saves them into a string variable. This allows for easy transmission from
    the patient-side GUI to the server.

    Args:
        (string): Name of image file to be encoded

    Returns:
        (string): Encoded base64 string of image file

    """
    with open(image_path, "rb") as image_file:
        b64_bytes = base64.b64encode(image_file.read())
    b64_string = str(b64_bytes, encoding='utf-8')
    return b64_string


def calculate_ecg_data(filename):
    """ Calculates heart rate from input ECG file

    The calculate_ecg_data() function takes in an ECG data file as the input.
    From this input, it calculates several pieces of information, such as heart
    rate, from the data file. It utilizes the code imported from ecg.py and
    returns the calculated heart rate to store and the time/voltage values to
    plot the ECG trace.

    Args:
        (string): Name of ECG data file

    Returns:
        (float): Calculated eart rate from ECG file
        (array): Time data from ECG file
        (array): Voltage data from ECG file

    """
    df_in = load_data(filename)
    df_c = check_data(df_in, filename)
    df = filter_data(df_c)
    time = df.time
    voltage = df.voltage
    duration = get_duration(df)
    max_val = get_max(df)
    min_val = get_min(df)
    peaks = get_peaks(df, max_val)
    num_beats = calc_num_beats(peaks)
    bpm = calc_bpm(num_beats, duration)
    beats = get_beats(df, peaks)
    return bpm, time, voltage


if __name__ == '__main__':
    design_window()
