import logging
import pathlib
from pathlib import Path
import time
from typing import Union, Set

import helper as h
from azurlane.Button import Button

"""
Weakness of pyautogui
script looks for exact pixel location when using locateOnScreen. Images does not scale.
Pyautogui scans for the exact image pixel by pixel from the window screen. So, you cannot expect it to execute 
while resizing the UI.
"""


class Stage:
    def __init__(self,
                 gui_path: Union[pathlib.PurePath, str],
                 back_coords: Set,
                 battle_coords: Set,
                 log: logging) -> None:
        self.gui_path = Path(gui_path) if isinstance(gui_path, str) else gui_path
        self.log = log

        self.back_btn = Button(coords=back_coords)
        self.battle_btn = Button(coords=battle_coords)

    def run(self):
        # click on stage 12
        stage_12 = Button(self.gui_path / "stage_12.png")
        if stage_12.exist():
            self.log.info(f"{h.trace()} Clicked Stage 12 ...")
            stage_12.click_win32()

        # click on go
        rounded_go = Button(self.gui_path / "go.png")
        if rounded_go.exist():
            self.log.info(f"{h.trace()} Clicked Go ...")
            rounded_go.click_win32()

        self._enhance()  # run auto enhance ships to clear dock space

        # after boss is killed click Continue to go next round
        cont_btn = Button(self.gui_path / "continue.png")
        if cont_btn.exist():
            self.log.info(f"{h.trace()} Clicked Continue ...")
            cont_btn.click_win32()

    def _enhance(self, retries=5):
        # Click enhance when Dock is full
        enhance_btn = Button(self.gui_path / "enhance2.png")
        if enhance_btn.exist():
            self.log.info(f"{h.trace()} Clicked Enhance from Prompt ...")
            enhance_btn.click_win32()

            ships = [x for x in self.gui_path.iterdir() if "ship" in x.name]

            for ship in ships:
                self.log.info(f"{h.trace()} Enhancing {ship.name}")
                retry, clicked = 0, False
                while retry < retries + 1:
                    ship_btn = Button(ship)
                    if ship_btn.exist():
                        self.log.info(f"{h.trace()} Clicked Ship1 ...")
                        ship_btn.click_win32()
                        clicked = True
                        break
                    else:
                        retry += 1
                        self.log.debug(f"{h.trace()} Retrying ({retry}/{retries}) Find {ship.name} btn")

                if not clicked:
                    continue

                # iteratively enhance until unable to
                while True:
                    fill_btn = Button(self.gui_path / "fill.png", confidence=0.7)
                    if fill_btn.exist():
                        self.log.info(f"{h.trace()} Clicked Fill Btn ...")
                        fill_btn.click_win32()

                    not_enough = Button(self.gui_path / "not_enough.png")
                    if not_enough.exist():
                        self.log.info(f"{h.trace()} Not Enough to enhance ...")
                        self.log.info(f"{h.trace()} Click Back Button ...")
                        self.back_btn.click_win32()
                        break

                    enhance2_btn = Button(self.gui_path / "enhance.png")
                    if enhance2_btn.exist():
                        self.log.info(f"{h.trace()} Clicked Enhance Gold ...")
                        enhance2_btn.click_win32()

                    # Continue to disassemble Gear
                    cont_btn = Button(self.gui_path / "confirm.png")
                    if cont_btn.exist():
                        self.log.info(f"{h.trace()} Clicked Confirm ...")
                        cont_btn.click_win32()

                    dis_btn = Button(self.gui_path / "disassemble.png")
                    if dis_btn.exist():
                        self.log.info(f"{h.trace()} Click Disassemble ...")
                        dis_btn.click_win32()

                    tap_cont = Button(self.gui_path / "ttc.png")
                    if tap_cont.exist():
                        self.log.info(f"{h.trace()} Click Tap to continue ...")
                        tap_cont.click_win32()

            self.log.info(f"Done with enhancing.")
            self.log.info(f"{h.trace()} Click Back Button ...")
            self.back_btn.click_win32()
            time.sleep(3)
            # click screen to continue farming

            retry = 0
            while retry < retries + 1:
                as_btn = Button(self.gui_path / 'auto-search.png')
                if as_btn.exist():
                    self.log.info(f"{h.trace()} Click auto-search to Continue Farming ...")
                    as_btn.click_win32()
                    break
                else:
                    retry += 1
                    self.log.debug(f"{h.trace()} Retrying ({retry}/{retries}) Find Auto-search btn")








