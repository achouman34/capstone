import os
import shutil
from os.path import join
import imageio
import pydicom
from numpy import uint8
import numpy as np
import time

HEIGHT_IN_PIXELS = 1024
WIDTH_IN_PIXELS = 1024
IMAGE_ROWS = 8
IMAGE_COLS = 8

DICOMDIR_PATH = "C:/Users/amath/OneDrive - The University of Western Ontario/4415 - Capstone/S27"
DESIRED_SERIES = "DTI1"
STD_DEV_ACROSS_N_FRAMES = 10


def dicom_to_bmp():
    for root, _, files in os.walk(DICOMDIR_PATH):
        for file in files:
            if file == "dicomdir":
                dataset = pydicom.dcmread(join(root, file))
                break

    image_records = None

    patient_record = dataset.patient_records[0]
    study = patient_record.children[0]
    all_series = study.children
    for series in all_series:
        if series.SeriesDescription == DESIRED_SERIES:
            image_records = series.children
            break

    if image_records is None:
        raise IOError

    image_filenames = [join(DICOMDIR_PATH, *image_rec.ReferencedFileID)
                       for image_rec in image_records]
    images = [pydicom.dcmread(image_filename)
              for image_filename in image_filenames]

    try:
        os.mkdir("Grid BMPs")
    except FileExistsError:
        shutil.rmtree("Grid BMPs")
        os.mkdir("Grid BMPs")

    for frame_num, image in enumerate(images, 1):
        imageio.imwrite(join("Grid BMPs", f"Frame {str(frame_num).zfill(3)}.bmp"),
                        uint8(image.pixel_array))


def grid_images_to_folders():

    istep = HEIGHT_IN_PIXELS//IMAGE_ROWS
    jstep = WIDTH_IN_PIXELS//IMAGE_COLS

    try:
        os.mkdir("Split BMPs")
    except FileExistsError:
        shutil.rmtree("Split BMPs")
        os.mkdir("Split BMPs")
    frame_number = 0
    for root, _, files in os.walk("Grid BMPs"):
        for file in files:
            if file.endswith(".bmp"):
                frame_number += 1
                sub_im = imageio.imread(join(root, file))

                os.mkdir(f"Split BMPs/Frame {str(frame_number).zfill(3)}")
                slice_number = 1
                for i in range(0, HEIGHT_IN_PIXELS, istep):
                    for j in range(0, WIDTH_IN_PIXELS, jstep):
                        imageio.imwrite(join(os.getcwd(), "Split BMPs",
                                             f"Frame {str(frame_number).zfill(3)}",
                                             f"Slice {str(slice_number).zfill(3)}.bmp"),
                                        sub_im[i:i+istep, j:j+jstep])
                        slice_number += 1
    shutil.rmtree("Grid BMPs")


def standard_deviation():
    frames = []

    for root, folders, _ in os.walk("Split BMPs"):
        for folder in folders:
            if folder.startswith("Frame"):
                frames.append(join(root, folder))

    output_frame_count = len(frames) // STD_DEV_ACROSS_N_FRAMES

    try:
        os.mkdir("STD DEV")
    except FileExistsError:
        shutil.rmtree("STD DEV")
        os.mkdir("STD DEV")

    for window in range(1, output_frame_count + 1):
        window_images = []
        for frame in frames[STD_DEV_ACROSS_N_FRAMES * (window - 1): STD_DEV_ACROSS_N_FRAMES * window]:
            frame_images = []
            for root, _, slices in os.walk(frame):
                for slic in slices:
                    if slic.endswith(".bmp"):
                        frame_images.append(imageio.imread(join(root, slic)))
            window_images.append(frame_images)

        window_images = np.array(window_images)
        output_images = np.empty(window_images.shape[1:])

        os.mkdir(join("STD DEV", f"Frame {str(window).zfill(3)}"))

        for slice_number in range(output_images.shape[0]):
            for y in range(output_images.shape[1]):
                for x in range(output_images.shape[2]):
                    output_images[slice_number, y, x] = np.std(
                        window_images[:, slice_number, y, x])

        output_images *= 255.0/output_images.max()
        output_images = uint8(output_images)

        for slice_number in range(output_images.shape[0]):
            imageio.imwrite(join("STD DEV", f"Frame {str(window).zfill(3)}",
                                 f"Slice {str(slice_number + 1).zfill(3)}.bmp"), output_images[slice_number])

    shutil.rmtree("Split BMPs")


def main():
    start_time = time.perf_counter()

    dicom_to_bmp()
    grid_images_to_folders()
    standard_deviation()

    end_time = time.perf_counter()
    print(end_time-start_time)


if __name__ == "__main__":
    main()
