import pathlib
import time
from typing import Union, Set

import pyautogui
import win32api
import win32con


class Button:
    def __init__(self,
                 img_path: Union[str, pathlib.PurePath] = "",
                 coords: Set = (),
                 confidence: float = 0.8,
                 grayscale: bool = True) -> None:

        assert img_path != "" or len(coords) != 0, "Either img_path or coords must have value"

        # init path object
        img_path = img_path if isinstance(img_path, str) else str(img_path)

        # locate button on monitor
        if img_path != "":
            find_ui = pyautogui.locateOnScreen(img_path, confidence=confidence, grayscale=grayscale)

            self.is_exist = False if find_ui is None else True
            self.left, self.top, self.width, self.height = find_ui if find_ui is not None else (0, 0, 0, 0)
        else:
            self.is_exist = True
            self.left, self.top, self.width, self.height = coords

    def click_gui(self, delay=1):
        x = int(self.left + (self.width / 2))
        y = int(self.top + (self.height / 2))
        pyautogui.click(x=x, y=y)
        time.sleep(delay)

    def click_win32(self, delay=1):
        x = int(self.left + (self.width / 2))
        y = int(self.top + (self.height / 2))
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
        time.sleep(delay)

    def exist(self):
        return self.is_exist

    def get_coords(self):
        return self.left, self.top, self.width, self.height

