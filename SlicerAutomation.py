import os
results_dir = "C:/Users/amath/OneDrive - The University of Western Ontario/4415 - Capstone/DTI Processing/DTI1/STD DEV"
volumeNodes = []
segmentationNodes = []
segmentEditorNodes = []
segmentEditorWidgets = []
effects = []
surfaceMeshes = []
addedSegmentIDs = []
normalses = []
for folder in os.listdir(results_dir):
    volumeNodes.append(slicer.util.loadVolume(f"{results_dir}/{folder}/Slice 001.bmp"))

for num, volumeNode in enumerate(volumeNodes, 1):
    # Create segmentation
    segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
    segmentationNode.CreateDefaultDisplayNodes() # only needed for display
    segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(volumeNode)
    addedSegmentID = segmentationNode.GetSegmentation().AddEmptySegment(f"test{num}")
    segmentationNodes.append(segmentationNode)
    addedSegmentIDs.append(addedSegmentID)

# Create segment editor to get access to effects
for num, segmentationNode in enumerate(segmentationNodes):
    segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
    segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
    segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
    segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
    segmentEditorWidget.setSegmentationNode(segmentationNodes[num])
    segmentEditorWidget.setMasterVolumeNode(volumeNodes[num])
    segmentEditorWidgets.append(segmentEditorWidget)
    segmentEditorNodes.append(segmentEditorNode)

# Thresholding
for num, segmentEditorNode in enumerate(segmentEditorNodes):
    segmentEditorWidgets[num].setActiveEffectByName("Threshold")
    effect = segmentEditorWidgets[num].activeEffect()
    effect.setParameter("MinimumThreshold","175")
    effect.setParameter("MaximumThreshold","254")
    effect.self().onApply()
    effects.append(effect)

# Clean up
del segmentEditorWidgets
for segmentEditorNode in segmentEditorNodes:
    slicer.mrmlScene.RemoveNode(segmentEditorNode)

# Make segmentation results visible in 3D
for segmentationNode in segmentationNodes:
    segmentationNode.CreateClosedSurfaceRepresentation()

# Make sure surface mesh cells are consistently oriented
for num, segmentationNode in enumerate(segmentationNodes):
    surfaceMesh = segmentationNode.GetClosedSurfaceInternalRepresentation(addedSegmentID[num])
    normals = vtk.vtkPolyDataNormals()
    normals.AutoOrientNormalsOn()
    normals.ConsistencyOn()
    normals.SetInputData(surfaceMesh)
    normals.Update()
    surfaceMesh = normals.GetOutput()
    surfaceMeshes.append(surfaceMesh)

# Write to OBJ file
for num, surfaceMesh in enumerate(surfaceMeshes, 1):
    writer = vtk.vtkOBJWriter()
    writer.SetInputData(surfaceMesh)
    writer.SetFileName(f"C:/Users/amath/OneDrive - The University of Western Ontario/4415 - Capstone/DTI Processing/DTI1/OBJs/test{num}.obj")
    writer.Update()
    writer.Write()


writer = vtk.vtkSTLWriter()
writer.SetInputData(surfaceMeshes[0])
writer.Update()