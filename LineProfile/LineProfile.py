import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# LineProfile
#

class LineProfile(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Line Profile"
    self.parent.categories = ["Quantification"]
    self.parent.dependencies = []
    parent.contributors = ["Andras Lasso (PerkLab)"]
    self.parent.helpText = """
This module computes intensity profile of a volume along a ruler line.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Andras Lasso (PerkLab)  and was partially funded by CCO ACRU.
""" # replace with organization, grant and thanks.

#
# LineProfileWidget
#

class LineProfileWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
    #
    self.inputVolumeSelector = slicer.qMRMLNodeComboBox()
    self.inputVolumeSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.inputVolumeSelector.selectNodeUponCreation = True
    self.inputVolumeSelector.addEnabled = False
    self.inputVolumeSelector.removeEnabled = False
    self.inputVolumeSelector.noneEnabled = False
    self.inputVolumeSelector.showHidden = False
    self.inputVolumeSelector.setMRMLScene(slicer.mrmlScene)
    self.inputVolumeSelector.setToolTip("Pick the input to the algorithm which will be sampled along the line.")
    parametersFormLayout.addRow("Input Volume: ", self.inputVolumeSelector)
    
    #
    # input ruler selector
    #
    self.inputRulerSelector = slicer.qMRMLNodeComboBox()
    self.inputRulerSelector.nodeTypes = ["vtkMRMLAnnotationRulerNode"]
    self.inputRulerSelector.selectNodeUponCreation = True
    self.inputRulerSelector.addEnabled = False
    self.inputRulerSelector.removeEnabled = False
    self.inputRulerSelector.noneEnabled = False
    self.inputRulerSelector.showHidden = False
    self.inputRulerSelector.setMRMLScene( slicer.mrmlScene )
    self.inputRulerSelector.setToolTip("Pick the ruler that defines the sampling line.")
    parametersFormLayout.addRow("Input ruler: ", self.inputRulerSelector)

    #
    # output volume selector
    #
    self.outputTableSelector = slicer.qMRMLNodeComboBox()
    self.outputTableSelector.nodeTypes = ["vtkMRMLTableNode"]
    self.outputTableSelector.addEnabled = True
    self.outputTableSelector.removeEnabled = True
    self.outputTableSelector.noneEnabled = False
    self.outputTableSelector.showHidden = False
    self.outputTableSelector.setMRMLScene( slicer.mrmlScene )
    self.outputTableSelector.setToolTip( "Pick the output table to the algorithm." )
    parametersFormLayout.addRow("Output table: ", self.outputTableSelector)

    #
    # output plot selector
    #
    self.outputPlotSelector = slicer.qMRMLNodeComboBox()
    self.outputPlotSelector.nodeTypes = ["vtkMRMLPlotSeriesNode"]
    self.outputPlotSelector.addEnabled = True
    self.outputPlotSelector.removeEnabled = True
    self.outputPlotSelector.noneEnabled = True
    self.outputPlotSelector.showHidden = False
    self.outputPlotSelector.setMRMLScene( slicer.mrmlScene )
    self.outputPlotSelector.setToolTip( "Pick the output plot series to the algorithm." )
    parametersFormLayout.addRow("Output plot series: ", self.outputPlotSelector)

    #
    # scale factor for screen shots
    #
    self.lineResolutionSliderWidget = ctk.ctkSliderWidget()
    self.lineResolutionSliderWidget.singleStep = 1
    self.lineResolutionSliderWidget.minimum = 2
    self.lineResolutionSliderWidget.maximum = 1000
    self.lineResolutionSliderWidget.value = 100
    self.lineResolutionSliderWidget.setToolTip("Number of points to sample along the line.")
    parametersFormLayout.addRow("Line resolution", self.lineResolutionSliderWidget)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)
    self.onSelect()

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.inputVolumeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.inputRulerSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.outputTableSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputVolumeSelector.currentNode() and self.inputRulerSelector.currentNode() and self.outputTableSelector.currentNode()

  def onApplyButton(self):
    logic = LineProfileLogic()
    lineResolution = int(self.lineResolutionSliderWidget.value)    
    logic.run(self.inputVolumeSelector.currentNode(), self.inputRulerSelector.currentNode(),
              self.outputTableSelector.currentNode(), lineResolution, self.outputPlotSelector.currentNode())

#
# LineProfileLogic
#

class LineProfileLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self):
    self.plotChartNode = None
    pass

  def run(self, inputVolume, inputRuler, outputTable, lineResolution=100, outputPlotSeries = None):
    """
    Run the actual algorithm
    """
    
    self.updateOutputTable(inputVolume, inputRuler, outputTable, lineResolution)
    if outputPlotSeries:
      self.updateChart(outputPlotSeries, outputTable)

    return True
    
  def getArrayFromTable(self, outputTable, arrayName):
    distanceArray = outputTable.GetTable().GetColumnByName(arrayName)
    if distanceArray:
      return distanceArray
    newArray = vtk.vtkDoubleArray()
    newArray.SetName(arrayName)
    outputTable.GetTable().AddColumn(newArray)
    return newArray

  def updateOutputTable(self, inputVolume, inputRuler, outputTable, lineResolution):
    import math

    rulerStartPoint_Ruler = [0,0,0]
    rulerEndPoint_Ruler = [0,0,0]
    inputRuler.GetPosition1(rulerStartPoint_Ruler)
    inputRuler.GetPosition2(rulerEndPoint_Ruler)
    rulerStartPoint_Ruler1 = [rulerStartPoint_Ruler[0], rulerStartPoint_Ruler[1], rulerStartPoint_Ruler[2], 1.0]
    rulerEndPoint_Ruler1 = [rulerEndPoint_Ruler[0], rulerEndPoint_Ruler[1], rulerEndPoint_Ruler[2], 1.0]
    
    rulerToRAS = vtk.vtkMatrix4x4()
    rulerTransformNode = inputRuler.GetParentTransformNode()
    if rulerTransformNode:
      if rulerTransformNode.IsTransformToWorldLinear():
        rulerToRAS.DeepCopy(rulerTransformNode.GetMatrixTransformToParent())
      else:
        print ("Cannot handle non-linear transforms - ignoring transform of the input ruler")

    rulerStartPoint_RAS1 = [0,0,0,1]
    rulerEndPoint_RAS1 = [0,0,0,1]
    rulerToRAS.MultiplyPoint(rulerStartPoint_Ruler1,rulerStartPoint_RAS1)
    rulerToRAS.MultiplyPoint(rulerEndPoint_Ruler1,rulerEndPoint_RAS1)        
    
    rulerLengthMm=math.sqrt(vtk.vtkMath.Distance2BetweenPoints(rulerStartPoint_RAS1[0:3],rulerEndPoint_RAS1[0:3]))

    # Need to get the start/end point of the line in the IJK coordinate system
    # as VTK filters cannot take into account direction cosines        
    rasToIJK = vtk.vtkMatrix4x4()
    parentToIJK = vtk.vtkMatrix4x4()
    rasToParent = vtk.vtkMatrix4x4()
    inputVolume.GetRASToIJKMatrix(parentToIJK)
    transformNode = inputVolume.GetParentTransformNode()
    if transformNode:
      if transformNode.IsTransformToWorldLinear():
        rasToParent.DeepCopy(transformNode.GetMatrixTransformToParent())
        rasToParent.Invert()
      else:
        print ("Cannot handle non-linear transforms - ignoring transform of the input volume")
    vtk.vtkMatrix4x4.Multiply4x4(parentToIJK, rasToParent, rasToIJK)
    
    rulerStartPoint_IJK1 = [0,0,0,1]
    rulerEndPoint_IJK1 = [0,0,0,1]
    rasToIJK.MultiplyPoint(rulerStartPoint_RAS1,rulerStartPoint_IJK1)
    rasToIJK.MultiplyPoint(rulerEndPoint_RAS1,rulerEndPoint_IJK1) 
    
    lineSource=vtk.vtkLineSource()
    lineSource.SetPoint1(rulerStartPoint_IJK1[0],rulerStartPoint_IJK1[1],rulerStartPoint_IJK1[2])
    lineSource.SetPoint2(rulerEndPoint_IJK1[0], rulerEndPoint_IJK1[1], rulerEndPoint_IJK1[2])
    lineSource.SetResolution(lineResolution-1)

    probeFilter=vtk.vtkProbeFilter()
    probeFilter.SetInputConnection(lineSource.GetOutputPort())
    if vtk.VTK_MAJOR_VERSION <= 5:
      probeFilter.SetSource(inputVolume.GetImageData())
    else:
      probeFilter.SetSourceData(inputVolume.GetImageData())
    probeFilter.Update()

    probedPoints=probeFilter.GetOutput()

    # Create arrays of data  
    distanceArray = self.getArrayFromTable(outputTable, DISTANCE_ARRAY_NAME)
    intensityArray = self.getArrayFromTable(outputTable, INTENSITY_ARRAY_NAME)
    outputTable.GetTable().SetNumberOfRows(probedPoints.GetNumberOfPoints())
    x = xrange(0, probedPoints.GetNumberOfPoints())
    xStep = rulerLengthMm/(probedPoints.GetNumberOfPoints()-1)
    probedPointScalars = probedPoints.GetPointData().GetScalars()
    for i in range(len(x)):
      distanceArray.SetValue(i, x[i]*xStep)
      intensityArray.SetValue(i, probedPointScalars.GetTuple(i)[0])

    probedPoints.GetPointData().GetScalars().Modified()

  def updateChart(self, outputPlotSeries, outputTable):

    # Create plot
    outputPlotSeries.SetAndObserveTableNodeID(outputTable.GetID())
    outputPlotSeries.SetXColumnName(DISTANCE_ARRAY_NAME)
    outputPlotSeries.SetYColumnName(INTENSITY_ARRAY_NAME)
    outputPlotSeries.SetPlotType(slicer.vtkMRMLPlotSeriesNode.PlotTypeScatter)
    outputPlotSeries.SetMarkerStyle(slicer.vtkMRMLPlotSeriesNode.MarkerStyleNone)
    outputPlotSeries.SetColor(0, 0.6, 1.0)

    # Create chart and add plot
    if not self.plotChartNode:
      plotChartNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotChartNode")
      plotChartNode.AddAndObservePlotSeriesNodeID(outputPlotSeries.GetID())
      self.plotChartNode = plotChartNode

    # Show plot in layout
    slicer.modules.plots.logic().ShowChartInLayout(self.plotChartNode)
    slicer.app.layoutManager().plotWidget(0).plotView().fitToContent()


class LineProfileTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_LineProfile1()

  def test_LineProfile1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = LineProfileLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')

DISTANCE_ARRAY_NAME = "Distance"
INTENSITY_ARRAY_NAME = "Intensity"
