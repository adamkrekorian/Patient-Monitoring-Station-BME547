import pytest
import base64
import io
import os
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import filecmp


@pytest.mark.parametrize('filename', [
    ("images/acl1.jpg"),
    ("images/acl2.jpg"),
    ("images/upj1.jpg"),
    ("images/upj1.jpg"),
    ])
def test_save_b64_image(filename):
    """ Tests image decoder function

    The test_save_b64_image() function tests the ability of the image
    decoder function to decode an an encoded string back into an image file

    Args:
        filename (str): filepath to test image

    """
    from monitor_gui import save_b64_image
    from patient_gui import read_file_as_b64
    b64str = read_file_as_b64(filename)
    out_file = save_b64_image(b64str)
    answer = filecmp.cmp(filename,
                         out_file)
    os.remove(out_file)
    assert answer is True
