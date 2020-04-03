import os
import subprocess
from typing import List, Optional

from qtpy import QtWidgets, QtCore, QtGui

import pydicom
import numpy as np
import time

from pydiq.dicom_data import DicomData
from pydiq.dicom_widget import DicomWidget
from pydiq.utils import dicom_files_in_dir, dicom_to_bmp, grid_images_to_folders, standard_deviation


class Viewer(QtWidgets.QMainWindow):
    def __init__(self, path = None):
        # Base window options.
        super(Viewer, self).__init__()
        self.setWindowTitle("SlicerVR - CAPS")
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.resize(900, 600)
        self.file = None
        self._file_name = None

        # Pipeline-specific "constants" (defaults manipulated through options pane).
        self.HEIGHT_IN_PIXELS = 1024
        self.WIDTH_IN_PIXELS = 1024
        self.IMAGE_ROWS = 8
        self.IMAGE_COLS = 8
        self.DESIRED_SERIES = "DTI1"
        self.STD_DEV_ACROSS_N_FRAMES = 10

        self.slicer_dir = r"C:\Users\loush\AppData\Local\NA-MIC\Slicer 4.11.0-2020-04-01"
        self.exportRan = False
        self.stdRan = False
        self.high_hu = 2000
        self.low_hu = -1024
       
        # self.pix_label = TrackingLabel(self)
        self.pix_label = DicomWidget(self)

        # self.color_table = [QtWidgets.qRgb(i, i, i) for i in range(256)]

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidget(self.pix_label)

        # self.setCentralWidget(self.pix_label)
        self.setCentralWidget(scroll_area)

        # self.series_dock = QtWidgets.QDockWidget("Series", self)
        # self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.series_dock)

        self.file_dock = QtWidgets.QDockWidget("Images", self)
        self.file_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.file_dock)

        self.file_list = QtWidgets.QListWidget()
        self.file_list.itemSelectionChanged.connect(self.on_file_item_change)
        self.file_dock.setWidget(self.file_list)

        # self.series_list = QtWidgets.QListWidget()
        # self.studies_list.itemSelectionChanged.connect(self.on_study_item_change)
        # self.series_dock.setWidget(self.series_list)

        self.hu_label = QtWidgets.QLabel("No image")
        self.c_label = QtWidgets.QLabel("")
        self.cw_label = QtWidgets.QLabel("")        
        self.x_label = QtWidgets.QLabel("")
        self.y_label = QtWidgets.QLabel("")
        self.z_label = QtWidgets.QLabel("")
        self.use_fractional_coordinates = True
        self.ij_label = QtWidgets.QLabel("")

        self._zoom_level = 1
        self.mouse_x = -1
        self.mouse_y = -1
       
        self.statusBar().addPermanentWidget(self.cw_label)
        self.statusBar().addPermanentWidget(self.ij_label)
        self.statusBar().addPermanentWidget(self.x_label)
        self.statusBar().addPermanentWidget(self.y_label)
        self.statusBar().addPermanentWidget(self.z_label)
        self.statusBar().addPermanentWidget(self.hu_label)

        self.data = np.ndarray((512, 512), np.int8)
        self.update_cw()

        if os.path.isfile(path):
            self.load_files([path])
        elif os.path.isdir(path):
            self.load_files(dicom_files_in_dir(path))
        self.build_menu()

    def open_directory(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        dialog.setViewMode(QtWidgets.QFileDialog.List)
        dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)
        if dialog.exec_():
            directory = str(dialog.selectedFiles()[0])
            # start_time = time.perf_counter()
            self.load_files(dicom_files_in_dir(directory))
            # end_time = time.perf_counter()
            # print("Loading performance (individual DICOM folders vs. parent folder): ", end_time - start_time)

            # Error handling for incorrect DICOM directories.
            if self.file_list.count() < 1:
                box = QtWidgets.QMessageBox()
                box.setWindowTitle("Error")
                box.setWindowIcon(QtGui.QIcon('icon.png'))
                box.setIcon(QtWidgets.QMessageBox.Critical)
                box.setText("Invalid DICOM directory!")
                msg = box.exec_()

                # Loading dialog.
                # dlg = QtWidgets.QDialog(None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
                # dlg.setWindowTitle("HELLO!")
                # dlg.setWindowIcon(QtGui.QIcon('icon.png'))
                # dlg.exec_()
                # dlg = None


    def export_image(self):
        # file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
        #     self,
        #     "Save file",
        #     os.path.expanduser("~/dicom-export.png"),
        #     "PNG images (*.png)"
        # )
        # if file_name:
        #     self.pix_label._image.save(file_name)

        # box = QtWidgets.QMessageBox()
        # box.setWindowTitle("Exporting")
        # box.setWindowIcon(QtGui.QIcon('icon.png'))
        # box.setIcon(QtWidgets.QMessageBox.Warning)
        # box.setText("Processing...please wait")
        # msg = box.exec_()

        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        dialog.setViewMode(QtWidgets.QFileDialog.List)
        dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)
        if dialog.exec_():
            directory = str(dialog.selectedFiles()[0])

            # Loading dialog.
            dlg = QtWidgets.QDialog(None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
            dlg.setWindowTitle("Working...")
            dlg.setWindowIcon(QtGui.QIcon('icon.png'))
            dlg.resize(200, 150)
            dlg.show()

            # start_time = time.perf_counter()
            dicom_to_bmp(directory, self.DESIRED_SERIES)
            grid_images_to_folders(self.HEIGHT_IN_PIXELS, self.WIDTH_IN_PIXELS, self.IMAGE_ROWS, self.IMAGE_COLS)
            # end_time = time.perf_counter()
            # print("Exporting performance (QMessageBox vs. QDialog): ", end_time - start_time)

            dlg.close()
            box = QtWidgets.QMessageBox()
            box.setWindowTitle("Success")
            box.setWindowIcon(QtGui.QIcon('icon.png'))
            box.setIcon(QtWidgets.QMessageBox.Information)
            box.setText("Export complete!")
            msg = box.exec_()

            # No exceptions to this point == successful export.
            self.exportRan = True


    def run_std_analysis(self):
        if self.exportRan:
            # Loading dialog.
            dlg = QtWidgets.QDialog(None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
            dlg.setWindowTitle("Working...")
            dlg.setWindowIcon(QtGui.QIcon('icon.png'))
            dlg.resize(200, 150)
            dlg.show()

            # start_time = time.perf_counter()
            standard_deviation(self.STD_DEV_ACROSS_N_FRAMES)
            # end_time = time.perf_counter()
            # print("Analysis performance (QMessageBox vs. QDialog): ", end_time - start_time)

            self.stdRan = True
            dlg.close()
            box = QtWidgets.QMessageBox()
            box.setWindowTitle("Success")
            box.setWindowIcon(QtGui.QIcon('icon.png'))
            box.setIcon(QtWidgets.QMessageBox.Information)
            box.setText("Standard deviation analysis complete!")
            msg = box.exec_()
        else:
            box = QtWidgets.QMessageBox()
            box.setWindowTitle("Error")
            box.setWindowIcon(QtGui.QIcon('icon.png'))
            box.setIcon(QtWidgets.QMessageBox.Critical)
            box.setText("Analysis could not be run! Ensure you have exported the parent folder to BMP images.")
            msg = box.exec_()

    def slicer_automation(self):
        if self.stdRan:
            # MUST specify default Slicer dev-build installation directory.
            script_dir = os.getcwd().replace("\\", "/") + "/SlicerAutomation.py"
            self.slicer_dir += "\Slicer.exe"

            # Loading dialog.
            dlg = QtWidgets.QDialog(None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
            dlg.setWindowTitle("Working...")
            dlg.setWindowIcon(QtGui.QIcon('icon.png'))
            dlg.resize(200, 150)
            dlg.show()

            # start_time = time.perf_counter()
            # command = f"\"{self.slicer_dir}\" --no-main-window --python-script {script_dir}"
            # os.system(f'cmd /c "{command}"')
            subprocess.Popen([self.slicer_dir, "--no-main-window", "--python-script", script_dir])
            # end_time = time.perf_counter()
            # print("VR performance ( os vs. subprocess (call) vs. subprocess (Popen) ): ", end_time - start_time)

            # Threading and subprocessing.
            while True:
                time.sleep(5)
                if os.path.isdir(os.getcwd().replace("\\", "/") + "/OBJs/"):
                    break

            dlg.close()
            box = QtWidgets.QMessageBox()
            box.setWindowTitle("Success")
            box.setWindowIcon(QtGui.QIcon('icon.png'))
            box.setIcon(QtWidgets.QMessageBox.Information)
            box.setText("DICOM images successfully made VR-Ready!")
            msg = box.exec_()
        else:
            box = QtWidgets.QMessageBox()
            box.setWindowTitle("Error")
            box.setWindowIcon(QtGui.QIcon('icon.png'))
            box.setIcon(QtWidgets.QMessageBox.Critical)
            box.setText("Preparation could not be complete! Ensure you have ran STD analysis on the BMP images.")
            msg = box.exec_()

    def launch_steam(self):
        # Launch SteamVR with selected model viewer (alternative to Unity).
        box = QtWidgets.QMessageBox()
        box.setWindowTitle("Error")
        box.setWindowIcon(QtGui.QIcon('icon.png'))
        box.setIcon(QtWidgets.QMessageBox.Critical)
        box.setText("SteamVR is not properly configured to load the DICOM object files made. Please reconnect your headset.")
        msg = box.exec_()

    def about_info(self):
        # Display message box of our info and example flow.
        box = QtWidgets.QMessageBox()
        box.setWindowTitle("About")
        box.setWindowIcon(QtGui.QIcon('icon.png'))
        box.setText("SlicerVR - CAPS is a collaborative project developed by the following engineers: \n\nJosh Bainbridge\nAli Chouman\nElliot Littlejohn\nAkhil Nathoo")
        msg = box.exec_()

    def dicom_settings(self):
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle("DICOM Settings")
        dlg.setWindowIcon(QtGui.QIcon('icon.png'))
        form_group_box = QtWidgets.QGroupBox("DICOM Export Settings")

        layout = QtWidgets.QFormLayout()
        btn1 = QtWidgets.QPushButton("Edit")
        btn1.clicked.connect(self.get_height)
        layout.addRow(QtWidgets.QLabel("fMRI Scan Height [pixels]"), btn1)

        btn2 = QtWidgets.QPushButton("Edit")
        btn2.clicked.connect(self.get_width)
        layout.addRow(QtWidgets.QLabel("fMRI Scan Width [pixels]"), btn2)

        btn3 = QtWidgets.QPushButton("Edit")
        btn3.clicked.connect(self.get_image_rows)
        layout.addRow(QtWidgets.QLabel("Number of Rows in fMRI Scan"), btn3)

        btn4 = QtWidgets.QPushButton("Edit")
        btn4.clicked.connect(self.get_image_cols)
        layout.addRow(QtWidgets.QLabel("Number of Columns in fMRI Scan"), btn4)

        btn5 = QtWidgets.QPushButton("Edit")
        btn5.clicked.connect(self.get_desired_series)
        layout.addRow(QtWidgets.QLabel("Desired DICOM Series"), btn5)

        btn6 = QtWidgets.QPushButton("Edit")
        btn6.clicked.connect(self.get_std_frames)
        layout.addRow(QtWidgets.QLabel("Standard deviation across N-frames"), btn6)

        form_group_box.setLayout(layout)
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(form_group_box)
        dlg.setLayout(main_layout)
        dlg.exec_()

    def get_height(self):
        i, ok = QtWidgets.QInputDialog.getInt(self, "Height", "Height [pixels]: ", self.HEIGHT_IN_PIXELS, 0)
        if ok:
            self.HEIGHT_IN_PIXELS = i

    def get_width(self):
        i, ok = QtWidgets.QInputDialog.getInt(self, "Width", "Width [pixels]: ", self.WIDTH_IN_PIXELS, 0)
        if ok:
            self.WIDTH_IN_PIXELS = i

    def get_image_rows(self):
        i, ok = QtWidgets.QInputDialog.getInt(self, "Scan Rows", "Number of Rows in fMRI Scan: ", self.IMAGE_ROWS, 0)
        if ok:
            self.IMAGE_ROWS = i

    def get_image_cols(self):
        i, ok = QtWidgets.QInputDialog.getInt(self, "Scan Columns", "Number of Columns in fMRI Scan: ", self.IMAGE_COLS, 0)
        if ok:
            self.IMAGE_COLS = i

    def get_desired_series(self):
        text, ok = QtWidgets.QInputDialog.getText(self, "Desired Series", "Desired DICOM Series: ", QtWidgets.QLineEdit.Normal, self.DESIRED_SERIES)
        if ok and text != '':
            self.DESIRED_SERIES = text

    def get_std_frames(self):
        i, ok = QtWidgets.QInputDialog.getInt(self, "N-Frame STD", "Standard deviation across N-frames: ", self.STD_DEV_ACROSS_N_FRAMES, 0)
        if ok:
            self.STD_DEV_ACROSS_N_FRAMES = i

    def build_menu(self): 
        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Open DICOM directory', self.open_directory, QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.file_menu.addAction('&Export DICOM parent folder to BMP', self.export_image, QtCore.Qt.CTRL + QtCore.Qt.Key_S)
        self.file_menu.addAction('&Launch SteamVR', self.launch_steam, QtCore.Qt.Key_F5)
        self.file_menu.addAction('&Quit', self.close, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)      

        self.view_menu = QtWidgets.QMenu('&View', self)
        self.view_menu.addAction('Zoom In', self.pix_label.increase_zoom, QtCore.Qt.CTRL + QtCore.Qt.Key_Plus)
        self.view_menu.addAction('Zoom Out', self.pix_label.decrease_zoom, QtCore.Qt.CTRL + QtCore.Qt.Key_Minus)
        self.view_menu.addAction('Zoom 1:1', self.pix_label.reset_zoom, QtCore.Qt.CTRL + QtCore.Qt.Key_0)
        fullscreen = QtWidgets.QAction('&Full Screen', self)
        fullscreen.setCheckable(True)
        fullscreen.setShortcut(QtCore.Qt.Key_F11)
        fullscreen.toggled.connect(self.toggle_full_screen)
        self.view_menu.addAction(fullscreen)

        self.tools_menu = QtWidgets.QMenu("&Tools", self)
        self.tools_menu.addAction('&Run STD Analysis', self.run_std_analysis, QtCore.Qt.Key_F2)
        self.tools_menu.addAction('&Prepare VR-Ready OBJs', self.slicer_automation, QtCore.Qt.Key_F3)
        self.tools_menu.addAction('&DICOM Settings', self.dicom_settings, QtCore.Qt.Key_F7)
        # self.tools_menu.addAction('&Show DICOM structure', self.show_structure, QtCore.Qt.Key_F2)

        self.help_menu = QtWidgets.QMenu("&Help", self)
        self.help_menu.addAction('&About', self.about_info, QtCore.Qt.Key_F6)

        self.menuBar().addMenu(self.file_menu)
        self.menuBar().addMenu(self.view_menu)
        self.menuBar().addMenu(self.tools_menu)
        self.menuBar().addMenu(self.help_menu)

    def show_structure(self):
        if self.file_name:
            f = pydicom.read_file(self.file_name)
            l = QtWidgets.QLabel(str(f))
            l.show()
            print(str(f))

    def toggle_full_screen(self, toggled):
        if toggled:
            self.setWindowState(QtCore.Qt.WindowFullScreen)
        else:
            self.setWindowState(QtCore.Qt.WindowNoState)

    def on_file_item_change(self):
        if not len(self.file_list.selectedItems()):
            self.file_name = None
        else:
            item = self.file_list.selectedItems()[0]
            # print item.text()
            self.file_name = str(item.toolTip())

    def load_files(self, files: List[str]):
        # self.series_list.clear()
        # self.series = {}
        self.file_list.clear()
        self.files = files
        for file_name in self.files:
            item = QtWidgets.QListWidgetItem(os.path.basename(file_name))
            item.setToolTip(file_name)
            self.file_list.addItem(item)
        self.file_list.setMinimumWidth(self.file_list.sizeHintForColumn(0) + 20)
        if self.files:
            self.file_name = self.files[0]

    def loading_dialog(self):
        # Loading dialog.
        dlg = QtWidgets.QDialog(None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        dlg.setWindowTitle("HELLO!")
        dlg.setWindowIcon(QtGui.QIcon('icon.png'))
        return dlg.show()

    def get_coordinates(self, i, j):
        x = self.image_position[0] + self.pixel_spacing[0] * i
        y = self.image_position[1] + self.pixel_spacing[1] * j
        z = self.image_position[2]
        return x, y, z

    @property
    def mouse_ij(self):
        '''Mouse position as voxel index in current DICOM slice.'''
        return self.mouse_y // self.zoom_factor, self.mouse_x // self.zoom_factor

    @property
    def mouse_xyz(self):
        '''Mouse position in DICOM coordinates.'''
        if self.use_fractional_coordinates:
            # TODO: Fix for zoom out
            correction = (self.zoom_factor - 1.) / (2. * self.zoom_factor) # To get center of left top pixel in a zoom grid
            return self.get_coordinates(self.mouse_x / self.zoom_factor - correction, self.mouse_y / self.zoom_factor - correction)
        else:
            return self.get_coordinates(self.mouse_x // self.zoom_factor, self.mouse_y // self.zoom_factor)

    def update_coordinates(self):
        if self.pix_label.data and False:
            x, y, z = self.mouse_xyz
            i, j = self.mouse_ij
            self.z_label.setText("z: %.2f" % z)
            if i >= 0 and j >= 0 and i < self.data.shape[0] and j < self.data.shape[1]:
                self.x_label.setText("x: %.2f" % x)
                self.y_label.setText("y: %.2f" % y)
                self.ij_label.setText("Pos: (%d, %d)" % self.mouse_ij)
                self.hu_label.setText("HU: %d" % int(self.data[i, j]))
                return
            else:
                self.hu_label.setText("HU: ???")     
        else:
            self.hu_label.setText("View image")
        self.ij_label.setText("")
        self.x_label.setText("")
        self.y_label.setText("")

    def update_cw(self):
        # self.cw_label.setText("W: %d C: %d" % (int(self.pix_label.w), int(self.pix_label.c)))
        # self.update_image()
        pass

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, value):
        try:
            self._file_name = value
            data = DicomData.from_files([self._file_name])
            self.pix_label.data = data
            # self.setWindowTitle("pydiq: " + self._file_name)
        except BaseException as exc:
            print(exc)
            self.pix_label.data = None
            # self.setWindowTitle("pydiq: No image")

            # try:
            #     self.image_position = np.array([float(t) for t in self.file.ImagePositionPatient])
            # except:
            #     self.image_position = np.array([1., 1., 1.])
            # self.pixel_spacing = np.array([float(t) for t in self.file.PixelSpacing])


