import os
import shutil
INPUT_PATH = "C:/Users/amath/OneDrive - The University of Western Ontario/4415 - Capstone/DTI Processing/DTI1/STD DEV"
OUTPUT_PATH = "C:/Users/amath/OneDrive - The University of Western Ontario/4415 - Capstone/DTI Processing/DTI1/"
MIN_THRES = 175
MAX_THRES = 255 

volumeNodes = []
for folder in os.listdir(INPUT_PATH):
    volumeNodes.append(slicer.util.loadVolume(f"{INPUT_PATH}/{folder}/Slice 001.bmp"))

try:
    os.mkdir(os.path.join(OUTPUT_PATH, "OBJs"))
except FileExistsError:
    shutil.rmtree(os.path.join(OUTPUT_PATH, "OBJs"))
    os.mkdir(os.path.join(OUTPUT_PATH, "OBJs"))

for num, volumeNode in enumerate(volumeNodes):
    # Create segmentation
    segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
    segmentationNode.CreateDefaultDisplayNodes() # only needed for display
    segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(volumeNode)
    addedSegmentID = segmentationNode.GetSegmentation().AddEmptySegment(f"test{num}")
    # Create segment editor to get access to effects
    segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
    segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
    segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
    segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
    segmentEditorWidget.setSegmentationNode(segmentationNode)
    segmentEditorWidget.setMasterVolumeNode(volumeNode)
    # Thresholding
    segmentEditorWidget.setActiveEffectByName("Threshold")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("MinimumThreshold", str(MIN_THRES))
    effect.setParameter("MaximumThreshold", str(MAX_THRES))
    effect.self().onApply()
    # Clean up
    segmentEditorWidget = None
    slicer.mrmlScene.RemoveNode(segmentEditorNode)
    # Make segmentation results visible in 3D
    segmentationNode.CreateClosedSurfaceRepresentation()
    # Make sure surface mesh cells are consistently oriented
    surfaceMesh = segmentationNode.GetClosedSurfaceInternalRepresentation(addedSegmentID)
    normals = vtk.vtkPolyDataNormals()
    normals.AutoOrientNormalsOn()
    normals.ConsistencyOn()
    normals.SetInputData(surfaceMesh)
    normals.Update()
    surfaceMesh = normals.GetOutput()
    # Write to OBJ file
    filename = os.path.join(OUTPUT_PATH, "OBJs", f"Frame {str(num + 1).zfill(3)}.obj")
    writer = vtk.vtkOBJWriter()
    writer.SetInputData(surfaceMesh)
    writer.SetFileName(filename)
    writer.Update()