import os
from pathlib import Path

import keyboard

import helper as h
from Logger import Log
from azurlane.al_stage import Stage
import argparse
import sys
from rescale import Scaler
from azurlane.Button import Button


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
parser.add_argument('-tgi',
                    '--test_gui_img',
                    help="include if you want to test if parameters are good",
                    action="store_true")
parser.add_argument('-tpb',
                    '--test_pybot',
                    help="include to run pybot without generating scalable GUI.",
                    action="store_true")
parser.add_argument('--ship_path',
                    help="Path to images of ship to enhance",
                    type=lambda x: Path(x).absolute(),
                    default="./ships_to_enhance")

""" Default Arguments """
parser.add_argument('--log_dir',
                    type=lambda x: Path(x).absolute(),
                    default=os.getcwd() + "/log")
args = parser.parse_args()

""" Initializing Logging Properties """
logs = Log(log_path=args.log_dir)
log = logs.get_logger()


def main():
    # generate scaled images and initialize pyautogui to use one set of scaled image
    sc = Scaler(args.gui_path, args.ship_path, log)
    if not args.test_pybot:
        sc.down_scale(args.num_gui_gen, scale_percent=args.gui_scale)
    gui_path = sc.init_img_path()

    assert gui_path is not None, "Unable to find suitable GUI images for pybot. " \
                                 "Please edit --num_gui_gen and --gui_scale so that pybot " \
                                 "is able to identify gui buttons on emulator"

    # Initialize Back Button by using location of Secretary Image
    back_coords = init_btn(gui_path / "secretary_image.png")
    # Get Battle Button coords from Main Screen
    battle_coords = init_btn(gui_path / "battle.png")

    al_stg = Stage(gui_path, back_coords, battle_coords, log)

    if not args.test_gui_img:  # if true means only want to run scaler
        log.info(f"{h.trace()} Press Keyboard 'q' to Quit ...")
        while keyboard.is_pressed('q') is False:
            al_stg.run()


def init_btn(img_path, num_retry=10):
    retry = 0
    while retry < num_retry + 1:
        back_btn = Button(img_path)
        if back_btn.exist():
            log.info(f"{h.trace()} Found Button Location of Secretary Image.")
            return back_btn.get_coords()

        retry += 1
        log.debug(f"{h.trace()} Retry ({retry}/3) to find secretary_image")

    log.error(f"{h.trace()} Unable to find suitable GUI images for pybot. Please edit --num_gui_gen and --gui_scale "
              f"so that pybot is able to identify gui buttons on emulator")
    sys.exit()


if __name__ == '__main__':
    main()
