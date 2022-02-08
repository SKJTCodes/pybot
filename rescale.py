import imghdr
import logging
import pathlib
from pathlib import Path
from typing import Union, List
from tqdm import tqdm
import cv2
import shutil

import helper as h
from azurlane.Button import Button


class Scaler:
    def __init__(self,
                 src_path: Union[pathlib.PurePath, str],
                 ship_path: Union[pathlib.PurePath, str],
                 secretary_path: Union[pathlib.PurePath, str],
                 log: logging,
                 dst_path: Union[pathlib.PurePath, str] = None):
        self.log = log

        self.secretary_path = Path(secretary_path) if isinstance(secretary_path, str) else secretary_path
        self.src_path = Path(src_path) if isinstance(src_path, str) else src_path
        self.ship_path = Path(ship_path) if isinstance(ship_path, str) else ship_path
        assert self.secretary_path.is_dir(), f"{self.secretary_path} not Found."
        assert self.src_path.is_dir(), f"{self.src_path} not Found."
        assert self.ship_path.is_dir(), f"{self.ship_path} not Found."

        if dst_path is None:
            self.dst_path = self.src_path
        else:
            self.dst_path = Path(dst_path) if isinstance(dst_path, str) else dst_path

    def down_scale(self, num_to_gen, scale_percent=0.1):
        """
        down scale image sets
        :param num_to_gen: number of sets to generate
        :param scale_percent: down scale percentage
        """
        assert (num_to_gen * scale_percent) <= 0.99, f"Please change num_to_gen or scale_percent. " \
                                                     f"Incompatible combination. Check: {scale_percent * num_to_gen}"
        scale = 1 - scale_percent

        paths = self._get_img_paths()
        for i in tqdm(range(num_to_gen), total=num_to_gen, desc="Down Scaling GUI"):
            for img_path in paths:
                if imghdr.what(str(img_path)) is None:
                    continue

                scale = round(scale, 2)

                # scale down images
                img = cv2.imread(str(img_path), 1)
                scaled_img = cv2.resize(img, (0, 0), fx=scale, fy=scale)

                # create folder to store images
                dst = self.dst_path / f"{str(scale).replace('.', '_')}"
                dst.mkdir(parents=True, exist_ok=True)

                cv2.imwrite(str(dst / img_path.name), scaled_img)

            scale -= scale_percent

        # create a folder for original images
        ori_dst = self.dst_path / "1_0"
        ori_dst.mkdir(parents=True, exist_ok=True)
        for image_path in paths:
            if imghdr.what(image_path) is None:
                continue

            shutil.copy(image_path, ori_dst / image_path.name)

    def init_img_path(self):
        """
        compare scaled images/ original with BlueStack GUI and find which scaled image best fit
        GUI
        :return: selected image set path
        """
        # get list of image names
        img_names = []
        for folder in self.dst_path.iterdir():
            if folder.is_dir():
                for file in folder.iterdir():
                    if file.is_dir():
                        continue
                    img_names.append(file.name)
                break

        self.log.info(f"{h.trace()} List of Scaled Images: {img_names}")
        # check with all scaled image
        gone_through = []
        with tqdm(img_names, total=len(img_names), desc="Finding GUI Image Set") as pbar:
            for img_name in pbar:
                paths = self._sort_paths([x for x in self.dst_path.iterdir() if x.is_dir()])

                for scale_path in paths:
                    if not scale_path.is_dir():
                        continue

                    img_path = scale_path / img_name
                    btn = Button(img_path)
                    if btn.exist():
                        pbar.update(len(img_names) - len(gone_through))
                        pbar.close()
                        self.log.info(f"{h.trace()} Found Match: {img_path}")
                        return scale_path

                gone_through.append(img_name)

    @staticmethod
    def _sort_paths(path_list):
        data = {}
        for x in path_list:
            data.update({float(x.name.replace("_", ".")): x})

        ret_list = []
        for x in sorted(data.keys(), reverse=True):
            ret_list.append(data[x])

        return ret_list

    def _get_img_paths(self) -> List[pathlib.PurePath]:
        gui_paths = [x for x in self.src_path.iterdir() if x.is_file()]
        enhance_paths = [x for x in self.ship_path.iterdir()]
        sec_paths = [x for x in self.secretary_path.iterdir()]
        paths = gui_paths + enhance_paths + sec_paths
        return paths
