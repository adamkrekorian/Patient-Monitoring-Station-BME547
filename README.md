# BME 547 Final Project
Adam Krekorian and Kaan Sahingur

Finalized November 16, 2020


## Purpose
The purpose of the BME 547 Final Project was to deploy a functional patient monitoring system. The designed system utilizes a patient-side client, a monitoring-station client, and a server/databse. The patient-side client allows for patient information to be entered and uploaded. The monitoring-station client allows for uploaded patient information to be viewed or downloaded. The sever/databse allows for storage of the patient data that is uploaded and retrieved. 


## Demo Video
Demo video of the deployed system can be found at: 
https://urldefense.com/v3/__https://duke.zoom.us/rec/share/EZDojod5jBeYgzaWbXxaNn4T_xU6PBb0luXlK9WO-_7Q86iRGajVkQXX7ADpiJCP.VTbPjwO_wHNPM90e__;!!OToaGQ!7ys_pwq6rnfxGNj1fEdzif5oZWXmbhIAjbzr4j4q4E3vKNhV6C2_bJKG3Ls28Bo$


## Components
The patient monitoring system consists of three main elements: Patient-side GUI, Monitoring station-side GUI, and Cloud Server


#### Patient-side GUI
The Patient-side graphical user interface is responsible for uploading new patients into the patient monitoring system's database. It allows for the user to enter medical information for patients. The patient-side GUI is launched from the patient_gui.py file. It creates a window in which patient information can be entered. The user is able to enter a patient name or patient medical record. In addition, the user can select a medical image or ECG data file from the local computer. The selected medical image will be displayed on the GUI. From the selected ECG data file, a trace of the ECG and corresponding heart rate will be calculated. Both of these will also be displayed. The user will be able to update any of this information in the GUI and upload it to the server. In order for an upload to successfully occur, a patient medical record number must be entered. This is to ensure that each upload is properly assigned to a specified patient. Any of the other data fields may or may not be left blank, depending on the user's intent.

In order to enter a patient name in the GUI, the name must be typed into the blank text box to the right of the "Name:" label. This input will be taken as a string. To enter a patient medical record number, the number must be typed into the blank text box to the right of the "Medical Record Number:" label. This input must be an integer, since the medical record number is a number. An error will occur if a string or non-numeric input is entered. In order to select a medical image file or ECG file, the "Select Medical Image" and "Select ECG Data" buttons can be used. Both of these will allow for a local file to be selected. Once selected, these images and heart rate for the ecg will automatically be displayed. The images will be displayed under their corresponding buttons, and the calculated heart rate will be displayed under the "ECG Heart Rate" label.

To upload the entered information to the server, the "Upload" button must be selected. The upload will only occur if a medical record number is input. The session can be ended by selecting the "Close" button. This will terminate the client and close the GUI window. 


#### Monitoring Station-side GUI
The Monitor-side GUI is responsible for displaying patient data from the database, including medical record numbers, the pateint's name, ECG data, and medical images. The monitor-side GUI is launched from the monitor_gui.py file. 

This creates a window in which patient information can be dispalyed by selecting a medical record number. After selecting a medical record number from the corresponding dropdown box, the user may press the "Okay" button to display the information stored in the database for that patient. The GUI will display the patients name and ID. If the patient has ECG data, the most recent heart rate measurement, the corresponding ECG trace, and the date and time on which said data was uploaded will be displayed as well. A new patient can be selected and displayed by selecting a new medical record number from the dropdown box and selecting "Okay" once again.

From here the user can select the "Select ECG" button to launch a pop-up menu with a dropdown box that lists all the dates of previous ECG measurements. The user can select a date and select the "Okay" button in the pop-up menu. This will display the corresponding ECG trace in the main window. The user may then select the "Download ECG" button to launch a dialog where the user can select the directory and input the filename to save the ECG trace locally. No extension is required, the image will automatically be saved as a .jpg.

The user may also select the "Select Image" button to launch a pop-up menu with a dropdown box that lists all the dates of previously uploaded medical images. The user can select a date and select the "Okay" button in the pop-up menu. This will display the corresponding medical image in the main window. The user may then select the "Download Image" button to launch a dialog where the user can select the directory and input the filename to save the medical image locally. No extension is required, the image will automatically be saved as a .jpg.

The user can exit the program by selecting the "Cancel" button at any time.

### Cloud Server
The cloud server allows for storage of the patient data that is uploaded and retrieved. It was built using a MongoDB database that allows for each access and connection. The server is set up in cloud_server.py. It receives uploaded patient information from the patient-side client and sends requested information to the monitoring station-side client.


## Performance
The final performance of the final project meets all of the specifications outlined in the assignment description.


## License 
MIT License

Copyright (c) [2020] [KaanSahingur,AdamKrekorian]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
