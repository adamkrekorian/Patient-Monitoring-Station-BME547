import json
import logging
import math
import numpy as np
import pandas as pd
from scipy.signal import find_peaks, butter, lfilter
from scipy.fft import fft, ifft
import matplotlib.pyplot as plt


def load_data(filename):
    """Load ECG data from from .csv file

    Load .csv data to dataframe with time and voltage columns

    Args:
        filename (string): filepath/filename string

    Returns:
        DataFrame: DataFrame of time-voltage values
    """
    df = pd.read_csv(filename, sep=',', names=['time', 'voltage'])
    return df


def check_data(df, filename):
    """Convert ECG data from string to float and check for missing values

    Iterate through rows in the ECG DataFrame. Convert string values to
    float values. If the value is missing or is a non-numeric string
    the row is dropped and an error log is written. If any of the voltage
    values are greater thatn 300 mV or less than -300 mV, a warning log
    is written.

    Args:
        df (DataFrame): DataFrame with ECG data
        filename (string): filepath/filename string

    Returns:
        DataFrame: DataFrame of cleaned time-voltage values
    """
    warn_bool = True
    for i, row in df.iterrows():
        time = row['time']
        voltage = row['voltage']
        t = convert_val(time)
        df.iloc[i].time = t
        v = convert_val(voltage)
        df.iloc[i].voltage = v
        check_time_for_errors(t)
        check_voltage_for_errors(v, filename, warn_bool)
        warn_bool = flag_warning(v, warn_bool)
    df = df.dropna(axis=0)
    df = df.reset_index()
    return df


def convert_val(val):
    """Convert string to float value

    Convert a string to float value. If the string is empty or is a
    non-numeric string the value returned is np.nan.

    Args:
        val (string): time/voltage value to be converted to float

    Returns:
        float: converted time/voltage value
    """
    if val == '':
        val = np.nan
    try:
        temp_val = float(val)
    except Exception:
        temp_val = np.nan
    return temp_val


def log_error(val):
    """Log an error if a value is missing

    Args:
        val (string): Time or Voltage depending on the missing value
    """
    logging.error(val + ' value is missing')


def log_warning(filename):
    """Log an error if a value exceeds the voltage threshold

    Args:
        val (string): filename/filepath of file with voltage outside range
    """
    logging.warning(filename + ': Voltage value exceeds +/-300 mV')


def check_time_for_errors(time):
    """Check if time value is missing

    If the float value is NaN, an error is logged.
    If the float value is not NaN, no error is logged.

    Args:
        time (float): float value to be checked
    """
    if np.isnan(time):
        log_error('time')


def check_voltage_for_errors(voltage, filename, bool_val):
    """Check if voltage value is missing or exceeds range

    If the float value is NaN, an error is logged and True is returned.
    If the float value is not NaN but exceeds the voltage thresholds,
    a warning is logged. Otherwise False is returned

    Args:
        voltage (float): float value to be checked
        filename (string): filename/filepath of ECG file
        bool_val (bool): flag for voltage threshold
    """
    if np.isnan(voltage):
        log_error('voltage')
    if (voltage > 299.99 or voltage < -299.99) and bool_val:
        log_warning(filename)


def flag_warning(voltage, check):
    """Set flag for whether voltage threshold has been exceeded

    Args:
        voltage (float): float value to be checked

    Returns:
        bool: bool of threshold check
    """
    if (voltage < 299.99 and voltage > -299.99) and check:
        return True
    return False


def get_duration(df):
    """Get duration of ECG recording

    Args:
        df (DataFrame): DataFrame with time/voltage data

    Returns:
        float: duration of ECG recording
    """
    start = df.time.iloc[0]
    end = df.time.iloc[-1]
    duration = end - start
    return duration


def get_max(df):
    """Get maximum voltage of ECG recording

    Args:
        df (DataFrame): DataFrame with ECG data

    Returns:
        float: maximum voltage found in ECG recording
    """
    max_val = df['voltage'].max()
    return max_val


def get_min(df):
    """Get minimum voltage of ECG recording

    Args:
        df (DataFrame): DataFrame with ECG data

    Returns:
        float: minimum voltage found in ECG recording
    """
    min_val = df['voltage'].min()
    return min_val


def get_peaks(df, max_val):
    """Get location of beats in ECG recording

    Args:
        df (DataFrame): DataFrame with ECG data
        max_val (float): maximum recorded voltage value in ECG data

    Returns:
        list[int]: indexes of all the peaks in ECG data
    """
    voltages = df.voltage.to_numpy()
    peaks, _ = find_peaks(voltages, prominence=(0.5*max_val),
                          height=(0.5*max_val))
    return peaks


def calc_num_beats(peaks):
    """Calculate the number of beats in ECG recording

    Args:
        peaks (list[int]): list with indexes of peaks of QRS complexes

    Returns:
        int: the number of peaks
    """
    num_beats = len(peaks)
    return num_beats


def calc_bpm(num_beats, duration):
    """Calculate the bpm of the ECG recording

    Args:
        num_beats (int): number of beats in ECG recording
        duration (float): length of time of ECG recording

    Returns:
        float: average bpm of ECG recording
    """
    bpm = num_beats / (duration / 60)
    bpm_round = np.round(bpm, decimals=3)
    return bpm_round


def get_beats(df, peaks):
    """Get the timestamps of the beats in the ECG recording

    Args:
        df (DataFrame): DataFrame with time and voltage data
        peaks (list[int]): indexes of peaks in ECG data

    Returns:
        list[float]: timestamps of beats in ECG recording
    """
    beats = df.iloc[peaks].time
    beats_clean = beats.to_numpy()
    beats_round = np.round(beats_clean, decimals=3)
    beats_out = beats_round.tolist()
    return beats_out


def clean_filename(filename):
    """Remove the .csv part of filename

    Args:
        filename (string): filepath/filename string

    Returns:
        string: filepath/filename with removed .csv
    """
    temp = filename.split('.')
    out = temp[0]
    return out


def calc_fs(df):
    """Calculate the sampling frequency

    Use the time data fro the ECG DataFrame to compute
    the sampling frequency by dividing the number of samples
    by the duration of the ECG recording.

    Args:
        df (DataFrame): DataFrame with ECG data

    Returns:
        float: sampling frequency
    """
    duration = get_duration(df)
    N = len(df.index)
    fs = N / duration
    return fs


def filter_data(df):
    """Filter noise out of ECG data

    Args:
        df (DataFrame): DataFrame with ECG data

    Returns:
        df (DataFrame): cleaned ECG data with noise removed
    """
    data = df.voltage
    fs = calc_fs(df)
    b1, a1 = butter(5, [50], btype='low', analog=False, output='ba', fs=fs)
    data_low = lfilter(b1, a1, data)
    b2, a2 = butter(5, [1], btype='high', analog=False, output='ba', fs=fs)
    data_clean = lfilter(b2, a2, data_low)
    v_out = pd.DataFrame(data=data_clean)
    df_out = df.assign(voltage=v_out)
    return df_out


def prepare_output(df, filename):
    """Assign ecg data to dictionary and output to JSON file

    Take each ECG file and compute duration, min/max, number of beats,
    mean heart rate beats per minute, and the indeces of the beats
    and assign them to dictionary values. Then create a file with the name
    'test_data.json' and input the patient's information.

    Args:
        df (DataFrame): DataFrame with ECG data
        filename (string): filename/filepath of input data
    """
    duration = get_duration(df)
    logging.info('calculating duration')
    max_val = get_max(df)
    logging.info('calculating maximum voltage')
    min_val = get_min(df)
    logging.info('calculating minimum voltage')
    peaks = get_peaks(df, max_val)
    logging.info('calculating peak indexes')
    num_beats = calc_num_beats(peaks)
    logging.info('calculating number of beats')
    bpm = calc_bpm(num_beats, duration)
    logging.info('calculating bpm')
    beats = get_beats(df, peaks)
    logging.info('finding timestamps of beats')
    temp_out = {
            'duration': duration,
            'voltage_extremes': (min_val, max_val),
            'num_beats': num_beats,
            'mean_hr_bpm': bpm,
            'beats': beats,
            }
    filename_clean = clean_filename(filename)
    filename_out = filename_clean + '.json'
    out_file = open(filename_out, 'w')
    json.dump(temp_out, out_file)
    out_file.close()


def main():
    logging.basicConfig(filename="ecg.log", level=logging.INFO)
    filename = input('Enter filename: ')
    logging.info('starting analysis of {}'.format(filename))
    df_in = load_data(filename)
    df_c = check_data(df_in, filename)
    df = filter_data(df_c)
    prepare_output(df, filename)
    logging.info('analysis of {} complete'.format(filename))


if __name__ == '__main__':
    main()
