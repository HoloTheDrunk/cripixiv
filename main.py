import json
import re
import requests
import time
import random
import xmltodict
import os
import shutil
from PIL import Image
import numpy as np

from logger import Logger
log = Logger("main").log

class Config:
    def __init__(self, data: dict[str, str | int]) -> None:
        self.first_page_link: str = data["first_page_link"]
        self.first_page_index: int = data["first_page_index"]
        self.last_page_index: int = data["last_page_index"]
        self.cookie: str = data["cookie"]

def get_cell_coords(img: np.ndarray, pos: tuple[int, int], res: int = 4) -> tuple[tuple[int, int], tuple[int, int]]:
    height, width, _ = img.shape
    slice_height, slice_width = height // res, width // res
    start_y, start_x = pos[1] * slice_height, pos[0] * slice_width
    off_y = start_y + slice_height if start_y + slice_height < height else height
    off_x = start_x + slice_width if start_x + slice_width < width else width

    return ((start_y, off_y), (start_x, off_x))

def get_cell_coords_by_index(img: np.ndarray, index: int, res: int = 4) -> tuple[tuple[int, int], tuple[int, int]]:
    y: int = index // res
    x: int = index % res

    r = get_cell_coords(img, (x, y), res=res)

    return r

def main() -> None:
    config: Config
    with open("config.json") as file:
        config = Config(json.load(file))

    matches = re.match(
        fr"(.*mode=)([0-9]+)(&file=)({str(config.first_page_index).zfill(4)})(\.xml)(.*)",
        config.first_page_link
    )

    head, mode, middle, index, ext, tail = (
        matches.group(1), int(matches.group(2)),
        matches.group(3), int(matches.group(4)),
        matches.group(5), matches.group(6)
    )

    # Get info about scrambling order of every image
    image_info: list[list[int]] = []
    for page in range(index, config.last_page_index + 1):
        log(f"Getting info for page {page}...", newline=False)

        response = requests.get(f"{head}{mode}{middle}{str(page).zfill(4)}{ext}{tail}",
                                cookies={"Cookie": config.cookie})

        if response.status_code != 200:
            log("ERROR: Failed to fetch image info")
            log(response.text)
            return

        image_info.append(
            xmltodict.parse(response.text)["Page"]["Scramble"]
                     .split(',')
        )

        log(f"Getting info for page {page}... ✓", erase=True, newline=False)
        time.sleep(1. + random.random())

    # Get images and save them locally, keep paths
    image_paths: list[str] = []
    for page in range(index, config.last_page_index + 1):
        log(f"Getting data for page {page}...", newline=False)

        response = requests.get(f"{head}1{middle}{str(page).zfill(4) + '_0000'}.bin{tail}",
                                cookies={"Cookie": config.cookie}, stream=True)

        if response.status_code != 200:
            log("ERROR: Failed to fetch image info")
            log(response.text)
            return

        image_paths.append(f"images/scrambled/{page}.jpeg")
        with open(image_paths[-1], "wb") as file:
            shutil.copyfileobj(response.raw, file)

        log(f"Getting data for page {page}... ✓", erase=True, newline=False)
        time.sleep(1. + random.random())

    # Create new image with cells in order
    for i, path in enumerate(image_paths):
        log(f"Solving image {path}")

        with Image.open(path) as base_image:
            img = np.asarray(base_image).copy()
            res = np.zeros(shape=img.shape, dtype='uint8')

            for j, cell in enumerate(map(int, image_info[i])):
                # Source cell
                s = get_cell_coords_by_index(img, cell)

                # Destination cell
                d = get_cell_coords_by_index(res, j)

                # Copy source cell to destination cell
                res[d[0][0] : d[0][1], d[1][0] : d[1][1]] = img[s[0][0] : s[0][1], s[1][0] : s[1][1]]

            Image.fromarray(res).save(path.replace("scrambled", "fixed"))

    log("Done, fixed images output in ./images/fixed")

if __name__ == "__main__":
    if not os.path.exists('images'):
        os.makedirs('images')

    if not os.path.exists('images/scrambled'):
        os.makedirs('images/scrambled')

    if not os.path.exists('images/fixed'):
        os.makedirs('images/fixed')

    main()
