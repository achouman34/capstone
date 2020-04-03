# ECE 4415 Capstone Project
Josh Bainbridge, Ali Chouman, Elliot Littlejohn, Akhil Nathoo

## Installation and Usage
1. Ensure you have Slicer 4.11.0 installed at the default directory (i.e. C:\Users\...\AppData\Local\NA-MIC\Slicer 4.11.0-2020-04-01)
2. Clone/download "Final Project" which contains the application "SlicerVR" (clone "S27" if you wish to test with sample scans)
3. Run Slicer.exe
4. To view individual DICOM series images, click on "File->Open DICOM directory" and select the individual series folder.
5. In "Tools->DICOM Settings", configure the necessary scan parameters before exporting (important to select the desired DICOM series).
6. Click on "File->Export DICOM parent folder to BMP" and select the DICOM folder containing "DICOMDIR". It will search for the desired DICOM series and save in the folder "Split BMPs" in the executable directory.
7. Navigate to "Tools->Run STD Analysis" to perform a standard deviation analysis across frames (3 required, use sample folder "S27").
8. Finally, "Tools->Prepare VR-Ready OBJs" will render the 3D model object files of the brain scans to viewed in VR.
9. "File->Launch SteamVR" will allow you to display the rendered objects provided you have connected a controller-compatible headset, such as Oculus Rift or HTC Vive, and a 3D model viewer application installed in your Steam library. Alternatively, the open-source ALVR (https://github.com/polygraphene/ALVR) was experimented with and can successfully emulate the Oculus headset with a Samsung Gear VR.
