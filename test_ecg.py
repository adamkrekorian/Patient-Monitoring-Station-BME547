import pytest
import json
import logging
import math
import numpy as np
import pandas as pd
from testfixtures import LogCapture
from scipy.signal import find_peaks
from ecg import filter_data


@pytest.mark.parametrize('value, expected', [
    ('5', 5),
    ('1.2', 1.2),
    ('-5.688', -5.688),
    ('nan', np.nan),
    ('', np.nan),
    ('aldskfj', np.nan),
    ('twenty five', np.nan),
    ])
def test_convert_val(value, expected):
    from ecg import convert_val
    out = convert_val(value)
    if np.isnan(out):
        assert np.isnan(out)
    else:
        assert out == expected


@pytest.mark.parametrize('time, expected', [
    (np.nan, ("root", "ERROR", "time value is missing")),
    ])
def test_check_time_for_errors_log_made(time, expected):
    from ecg import check_time_for_errors
    with LogCapture() as log_c:
        check_time_for_errors(time)
    log_c.check(expected)


@pytest.mark.parametrize('time', [
    (5.0),
    (4.3),
    (-100.3),
    ])
def test_check_time_for_errors_log_not_made(time):
    from ecg import check_time_for_errors
    with LogCapture() as log_c:
        check_time_for_errors(time)
    log_c.check()


@pytest.mark.parametrize('voltage, filename, bool_val, expected', [
    (np.nan, 'test1', True, ("root", "ERROR", "voltage value is missing")),
    (301.0, 'test1', True,
        ("root", "WARNING", "test1: Voltage value exceeds +/-300 mV")),
    (-301.0, 'test1', True,
        ("root", "WARNING", "test1: Voltage value exceeds +/-300 mV")),
    ])
def test_check_voltage_for_errors_log_made(
        voltage, filename, bool_val, expected):
    from ecg import check_voltage_for_errors
    with LogCapture() as log_c:
        check_voltage_for_errors(voltage, filename, bool_val)
    log_c.check(expected)


@pytest.mark.parametrize('voltage, filename, bool_val,', [
    (5, 'test1', True),
    (4.3, 'test1', True),
    (-100.3, 'test1', True),
    (301.0, 'test1', False),
    (299.0, 'test1', True),
    (-301.0, 'test1', False),
    (-269.3, 'test1', True),
    ])
def test_check_voltage_for_errors_log_not_made(voltage, filename, bool_val):
    from ecg import check_voltage_for_errors
    with LogCapture() as log_c:
        check_voltage_for_errors(voltage, filename, bool_val)
    log_c.check()


@pytest.mark.parametrize('value, check, expected', [
    (5, True, True),
    (4.3, True, True),
    (-100.3, False, False),
    (-300.3, True, False),
    (310.3, False, False),
    ])
def test_flag_warning(value, check, expected):
    from ecg import flag_warning
    out = flag_warning(value, check)
    assert out == expected


@pytest.mark.parametrize('df, expected', [
    (pd.DataFrame(
        data={'time': [0, 2], 'voltage': [3, 4]}), 2),
    (pd.DataFrame(
        data={'time': [0, 2, 2.4], 'voltage': [3, 42, 0.3]}), 2.4),
    ])
def test_get_duration(df, expected):
    from ecg import get_duration
    out = get_duration(df)
    assert out == expected


@pytest.mark.parametrize('df, expected', [
    (pd.DataFrame(
        data={'time': [1, 2], 'voltage': [3, 4]}), 4),
    (pd.DataFrame(
        data={'time': [1, 2, 2.4], 'voltage': [3, 42, 0.3]}), 42),
    ])
def test_get_max(df, expected):
    from ecg import get_max
    out = get_max(df)
    assert out == expected


@pytest.mark.parametrize('df, expected', [
    (pd.DataFrame(
        data={'time': [1, 2], 'voltage': [3, 4]}), 3),
    (pd.DataFrame(
        data={'time': [1, 2, 2.4], 'voltage': [3, 42, 0.3]}), 0.3),
    ])
def test_get_min(df, expected):
    from ecg import get_min
    out = get_min(df)
    assert out == expected


@pytest.mark.parametrize('df, max_val, expected', [
    (pd.DataFrame(
        data={'time': [1, 2, 3], 'voltage': [3, 4, 2]}), 4, [1]),
    (pd.DataFrame(
        data={'time': [1, 1.5, 2.4, 2.5, 2.8, 3.5],
              'voltage': [3, 10, 0.3, 9.5, 2.2, 1.5]}), 10, [1, 3]),
    (pd.DataFrame(
        data={'time': [1, 1.5, 2.4, 3.2], 'voltage': [3, 4, 5, 6]}), 6, []),
    ])
def test_get_peaks(df, max_val, expected):
    from ecg import get_peaks
    out = get_peaks(df, max_val)
    comb = zip(out, expected)
    assert all([x == y for x, y in comb])


@pytest.mark.parametrize('peaks, expected', [
    ([1, 4, 6, 20], 4),
    ([], 0),
    ([1, 4, 6, 20, 35], 5),
    ])
def test_calc_num_beats(peaks, expected):
    from ecg import calc_num_beats
    out = calc_num_beats(peaks)
    assert out == expected


@pytest.mark.parametrize('num_beats, duration, expected', [
    (20, 60, 20),
    (20, 120, 10),
    (62, 45.3, 82.119),
    ])
def test_calc_bpm(num_beats, duration, expected):
    from ecg import calc_bpm
    out = calc_bpm(num_beats, duration)
    assert out == expected


@pytest.mark.parametrize('df, peaks, expected', [
    (pd.DataFrame(
        data={'time': [1, 2], 'voltage': [3, 4]}),
        [0, 1],
        [1, 2]),
    (pd.DataFrame(
        data={'time': [0.5, 0.9, 1.4], 'voltage': [3, 4, 6]}),
        [0, 2],
        [0.5, 1.4]),
    (pd.DataFrame(
        data={'time': [0.11, 0.36, 0.78, 1.22],
              'voltage': [1.5, 3.4, 6.7, 2.5]}),
        [1, 3],
        [0.36, 1.22]),
    ])
def test_get_beats(df, peaks, expected):
    from ecg import get_beats
    out = get_beats(df, peaks)
    comb = zip(out, expected)
    assert all([x == y for x, y in comb])


@pytest.mark.parametrize('filename, expected', [
    ('test_data2.csv', 'test_data2'),
    ('test_data11.csv', 'test_data11'),
    ('2.22222', '2'),
    ('a.p.p.l.e', 'a'),
    ])
def test_clean_filename(filename, expected):
    from ecg import clean_filename
    out = clean_filename(filename)
    assert out == expected


@pytest.mark.parametrize('df, expected', [
    (pd.DataFrame(
        data={'time': [0, 2], 'voltage': [3, 4]}),
        2/2),
    (pd.DataFrame(
        data={'time': [0, 0.9, 1.4], 'voltage': [3, 4, 6]}),
        3/1.4),
    (pd.DataFrame(
        data={'time': [0, 0.36, 0.78, 1.22],
              'voltage': [1.5, 3.4, 6.7, 2.5]}),
        4/1.22),
    ])
def test_calc_fs(df, expected):
    from ecg import calc_fs
    out = calc_fs(df)
    assert out == expected


@pytest.mark.parametrize('df, expected', [
    (pd.DataFrame(
        data={'time': np.linspace(0, 20, 10000),
              'voltage': np.sin(np.pi*30*np.linspace(0, 20, 10000)) +
              np.sin(np.pi*100*np.linspace(0, 20, 10000))}),
        filter_data(pd.DataFrame(
            data={'time': np.linspace(0, 20, 10000),
                  'voltage': np.sin(np.pi*30*np.linspace(0, 20, 10000)) +
                  np.sin(np.pi*100*np.linspace(0, 20, 10000))}))),
    (pd.DataFrame(
        data={'time': np.linspace(0, 20, 10000),
              'voltage': np.sin(np.pi*30*np.linspace(0, 20, 10000)) +
              np.sin(np.pi*0.2*np.linspace(0, 20, 10000))}),
        filter_data(pd.DataFrame(
            data={'time': np.linspace(0, 20, 10000),
                  'voltage': np.sin(np.pi*30*np.linspace(0, 20, 10000)) +
                  np.sin(np.pi*0.2*np.linspace(0, 20, 10000))}))),
    ])
def test_filter_data(df, expected):
    from ecg import filter_data
    out = filter_data(df)
    assert out.equals(expected)
