import base64
import io
from matplotlib import pyplot as plt
import matplotlib.image as mpimg


def test_file_to_b64_string():
    """ Tests image encoder function

    The test_file_to_b64_string() function tests the ability of the image
    encoder function to encode an input image file into a base64 byte string.

    Args:

    Returns:

    """
    from patient_gui import read_file_as_b64
    b64str = read_file_as_b64("/Users/kaansahingur/Desktop/encode_test.jpg")
    assert b64str[0:20] == "/9j/4AAQSkZJRgABAQAA"
