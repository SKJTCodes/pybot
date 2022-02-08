import argparse
import os
import pathlib
import sys
from pathlib import Path
from typing import Union, Set, List

from pynput import keyboard
from tqdm import tqdm

import helper as h
from Logger import Log
from azurlane.Button import Button
from azurlane.al_stage import Stage
from rescale import Scaler
from azurlane.enhance import Enhance

""" Initializing Script Parameters """
parser = argparse.ArgumentParser(description="Automate Mobile Game (Azur Lane)")

""" Project Arguments """
parser.add_argument('--gui_scale',
                    help="GUI Images, scale percentage between each --num_gui_gen",
                    type=float,
                    default=0.05)
parser.add_argument('--num_gui_gen',
                    help="Specify number of sets of GUI image to generate",
                    type=int,
                    default=15)
parser.add_argument('--gui_path',
                    help="GUI Image Path",
                    type=lambda x: Path(x).absolute(),
                    default="./azurlane/GUI")
parser.add_argument('--ship_path',
                    help="Path to images of ship to enhance",
                    type=lambda x: Path(x).absolute(),
                    default="./ships_to_enhance")
parser.add_argument('--secretary_path',
                    help="Path to images of secretaries",
                    type=lambda x: Path(x).absolute(),
                    default="./secretaries")
parser.add_argument('-tgi',
                    '--test_gui_img',
                    help="include if you want to test if parameters are good",
                    action="store_true")
parser.add_argument('-tpb',
                    '--test_pybot',
                    help="include to run pybot without generating scalable GUI.",
                    action="store_true")

""" Default Arguments """
parser.add_argument('--log_dir',
                    type=lambda x: Path(x).absolute(),
                    default=os.getcwd() + "/log")
args = parser.parse_args()

""" Initializing Logging Properties """
logs = Log(log_path=args.log_dir)
log = logs.get_logger()

""" Condition to end Script """
esc_condition = (keyboard.Key.ctrl_l, keyboard.KeyCode(char="q"))
pressed_input = set()  # when input are pressed, it will be inserted here


def main():
    # generate scaled images and initialize pyautogui to use one set of scaled image
    sc = Scaler(args.gui_path, args.ship_path, args.secretary_path, log)
    if not args.test_pybot:
        sc.down_scale(args.num_gui_gen, scale_percent=args.gui_scale)
    gui_path = sc.init_img_path()

    assert gui_path is not None, "Unable to find suitable GUI images for pybot. " \
                                 "Please edit --num_gui_gen and --gui_scale so that pybot " \
                                 "is able to identify gui buttons on emulator"

    # Initialize Back Button by using location of Secretary Image
    sec_paths = [x for x in gui_path.iterdir() if 'secretary' in x.stem]
    back_coords = init_btn(sec_paths, confidence=0.7, desc="Locating Secretary")
    # Get Battle Button coords from Main Screen
    battle_coords = init_btn(gui_path / "battle.png", desc="Locating Battle Btn")

    al_stg = Stage(gui_path, back_coords, battle_coords, log)

    if not args.test_gui_img:  # if true means only want to run scaler
        log.info(f"{h.trace()} Press Keyboard 'ctrl-l' release then 'q' to Quit ...")

        with keyboard.Listener(on_press=on_press) as listener:
            while True:
                al_stg.run(listener)
                if not listener.running:
                    log.info(f"{h.trace()} Force Ending Process")
                    break


def on_press(key):
    log.info(f"{h.trace()} Pressed {key}")
    if key in esc_condition:
        pressed_input.add(key)
        if all(k in pressed_input for k in esc_condition):
            return False


def init_btn(img_paths: Union[List[pathlib.PurePath], str, pathlib.PurePath],
             num_retry=10,
             confidence=0.8,
             desc=None) -> Set:
    img_paths = img_paths if isinstance(img_paths, list) else [Path(img_paths)]
    pbar = tqdm(enumerate(img_paths), total=len(img_paths), desc=desc)
    for idx, img_path in pbar:
        retry = 0
        while retry < num_retry + 1:
            back_btn = Button(img_path, confidence=confidence)
            if back_btn.exist():
                pbar.update(len(img_paths) - idx)
                pbar.close()

                log.info(f"{h.trace()} Found Button Location of {img_path.name}.")

                return back_btn.get_coords()

            retry += 1
            log.debug(f"{h.trace()} Retry ({retry}/{num_retry}) to find {img_path.name}")
    log.error(f"{h.trace()} Unable to find suitable GUI images for pybot. Please edit --num_gui_gen and --gui_scale "
              f"so that pybot is able to identify gui buttons on emulator")
    sys.exit()


if __name__ == '__main__':
    main()
