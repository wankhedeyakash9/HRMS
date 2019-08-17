import os
import string
import random


def get_img_name():
    lst = os.listdir('static')
    filename = None

    for file in lst:
        if file.endswith(".jpg"):
            filename = file
            break
    return filename


def get_random_img_name():
    """Generate random string of length 10"""
    letters = string.ascii_lowercase
    return './static/'+''.join(random.choice(letters) for i in range(10))+'.jpg'


def image_exist():
    name = get_img_name()
    if name and name.endswith(".jpg"):
        return True
    return False
