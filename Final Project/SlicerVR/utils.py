import os
import shutil
import imageio
import pydicom
import numpy as np
import time
import pydicom
from os.path import join
from numpy import uint8
from typing import List, Tuple

def get_id(path: str) -> Tuple[str, str]:
    f = pydicom.read_file(path, stop_before_pixels=True)
    return f.StudyInstanceUID, f.SeriesInstanceUID


def is_dicom_file(path: str) -> bool:
    """Fast way to check whether file is DICOM."""
    if not os.path.isfile(path):
        return False
    try:
        with open(path, "rb") as f:
            return f.read(132).decode("ASCII")[-4:] == "DICM"
    except:
        return False


def dicom_files_in_dir(directory: str = ".") -> List[str]:
    """Full paths of all DICOM files in the directory."""
    directory = os.path.expanduser(directory)
    candidates = [os.path.join(directory, f) for f in sorted(os.listdir(directory))]
    return [f for f in candidates if is_dicom_file(f)]


def dicom_to_bmp(dicomdir_path, desired_series):
    for root, _, files in os.walk(dicomdir_path):
        for file in files:
            if file == "dicomdir":
                dataset = pydicom.dcmread(join(root, file))
                break

    image_records = None

    patient_record = dataset.patient_records[0]
    study = patient_record.children[0]
    all_series = study.children
    for series in all_series:
        if series.SeriesDescription == desired_series:
            image_records = series.children
            break

    if image_records is None:
        raise IOError

    image_filenames = [join(dicomdir_path, *image_rec.ReferencedFileID)
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


def grid_images_to_folders(height_in_pixels, width_in_pixels, image_rows, image_cols):

    istep = height_in_pixels//image_rows
    jstep = width_in_pixels//image_cols

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
                for i in range(0, height_in_pixels, istep):
                    for j in range(0, width_in_pixels, jstep):
                        imageio.imwrite(join(os.getcwd(), "Split BMPs",
                                             f"Frame {str(frame_number).zfill(3)}",
                                             f"Slice {str(slice_number).zfill(3)}.bmp"),
                                        sub_im[i:i+istep, j:j+jstep])
                        slice_number += 1
    shutil.rmtree("Grid BMPs")


def standard_deviation(std_dev_across_n_frames):
    frames = []

    for root, folders, _ in os.walk("Split BMPs"):
        for folder in folders:
            if folder.startswith("Frame"):
                frames.append(join(root, folder))

    output_frame_count = len(frames) // std_dev_across_n_frames

    try:
        os.mkdir("STD DEV")
    except FileExistsError:
        shutil.rmtree("STD DEV")
        os.mkdir("STD DEV")

    for window in range(1, output_frame_count + 1):
        window_images = []
        for frame in frames[std_dev_across_n_frames * (window - 1): std_dev_across_n_frames * window]:
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
