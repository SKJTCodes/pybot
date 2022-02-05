import datetime as dt
import inspect
import operator
import os
import time
from datetime import timedelta
from pathlib import Path


def timer(start=None):
    if start is None:
        return time.time()
    else:
        return round(time.time() - start, 2)


def getparentfname(suffix=True):
    """
    get file name of the parent function that initiates current function
    :return : parent file path
    """
    path = Path(inspect.stack()[-1][1])
    return path.stem if suffix is False else path


def trace(offset=0, lvl=1):
    offset += 1
    return f"{os.path.basename(inspect.stack()[offset].filename)}:{inspect.stack()[offset].lineno}: {inspect.stack()[offset].function}()" if lvl > 0 else ""


def getuser():
    for name in ('LOGNAME', 'USER', 'LNAME', 'USERNAME'):
        user = os.environ.get(name)
        if user:
            return user


def date_delta(date=None, in_fmt="%Y%m%d", fmt="%Y%m%d", ret_type="str", **kwargs):
    """
    :param date: a datetime object or string
    :param in_fmt: if date is a string provide an in_fmt
    :param fmt: out format, '%Y%m%d', '%H%M%S', '%Y%m%d-%H%M.%S'
    :param ret_type: if str return string value, if date return date value
    :param kwargs:
    :return:
    """
    # convert string to datetime
    if date is None:
        date = dt.datetime.today()
    if type(date) is str:
        date = dt.datetime.strptime(date, in_fmt)
    # else don't need convert anything

    op = {"add": operator.add, "sub": operator.sub}

    if bool(kwargs):  # if there are kwargs
        key = list(kwargs)[0]
        n_date = op[key](date, timedelta(kwargs[key]))
    else:
        n_date = date

    return n_date.strftime(fmt) if ret_type == "str" else n_date


def getusername():
    if os.name == 'nt':
        import pywintypes
        import win32api
        try:
            username = win32api.GetUserNameEx(3)
        except pywintypes.error:
            user = os.environ.get('USERNAME')
            username = f"System Process - {user}"
    else:
        username = user = os.environ.get("USER")
    return username
