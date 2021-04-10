# createUI
import maya.cmds as cmds
import pymel.core as pm
import maya.OpenMaya as OpenMaya
import json


class deformCalc(object):
    def __init__(self):

        self.window = 'areaCalc'
        self.title = 'deformation Calculator'
        self.size = (600, 400)

        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)

        self.window = cmds.window(self.window, title=self.title, width=self.size[0])

        cmds.columnLayout(adjustableColumn=True)
        cmds.text(label='selected objects')
        itemList = cmds.ls(selection=True)

        self.selectionBox = cmds.textScrollList('itemList', append=itemList)
        self.refreshButton = cmds.button(label='Refresh list', command=self.refreshList, width=200, height=25,
                                         align='center')
        self.button = cmds.button(label='Calculate', command=self.toggleButton)
        cmds.separator(height=5)

        self.name = cmds.textFieldGrp(label='File Name')
        self.pathFinder = cmds.textFieldButtonGrp(label='Save Path', buttonLabel='Browse',
                                                  buttonCommand=self.browseFiles)
        self.data = []

        cmds.showWindow()

    def refreshList(self, *args):

        cmds.textScrollList(self.selectionBox, e=True, removeAll=True)
        itemList = cmds.ls(selection=True)
        for obj in itemList:
            cmds.textScrollList(self.selectionBox, e=True, append=obj)

    def toggleButton(self, *arg):

        items = cmds.textScrollList(self.selectionBox, q=True, ai=True)
        print("items: {}".format(items))
        if not len(items) == 2:
            print("please select two objects")
            raise Exception("incorrect selection amount: Please select 2 items")

        dataSet1 = []
        dataSet2 = []
        x = 0
        for mesh in items:
            print("starting area calculation for: {}".format(mesh))
            selectionList = OpenMaya.MSelectionList()
            selectionList.add(mesh)
            dp = OpenMaya.MDagPath()
            selectionList.getDagPath(0, dp)
            print("Dagpath: {}".format(dp.fullPathName()))
            fnMesh = OpenMaya.MFnMesh(dp)

            iterator = OpenMaya.MItMeshPolygon(dp)
            polyNumber = iterator.count()
            print("polynumber: {}".format(polyNumber))

            for y in range(polyNumber):
                print("polyIndex: {}".format(iterator.index()))
                faceArea = OpenMaya.MScriptUtil()
                faceAreaPntr = faceArea.asDoublePtr()

                iterator.getArea(faceAreaPntr)
                next(iterator)

                if x == 0:
                    dataSet1.append(faceArea.getDouble(faceAreaPntr))
                else:
                    dataSet2.append(faceArea.getDouble(faceAreaPntr))
            iterator.reset()
            if x == 0:
                x = 1
            else:
                x = 0

        if not len(dataSet1) == len(dataSet2):
            raise Exception("DataSets have unequal number of polygons")
        result = []

        print("starting deformation calculation")
        for x in range(len(dataSet1)):
            deformation = dataSet2[x] / dataSet1[x]
            print("Poly {},: {}".format(x, deformation))
            result.append(deformation)

        print('dataSet1: {}'.format(dataSet1))
        print('dataSet2: {}'.format(dataSet2))
        print("result: {}".format(result))
        self.saveData(result)

    def printFunction(self):
        pStatement = cmds.textField('pStatementInput', q=True, text=True)
        print(pStatement)

    def browseFiles(self):

        self.file_path = cmds.fileDialog2(fm=3, okc='select')
        print(self.file_path)
        cmds.textFieldButtonGrp(self.pathFinder, e=True, tx=str(self.file_path[0]))

    def saveData(self, result):
        savepath = cmds.textFieldButtonGrp(self.pathFinder, q=True, tx=True)
        name = cmds.textFieldGrp(self.name, q=True, tx=True)
        print('savePath: {}'.format(savepath))
        print('name: {}'.format(name))
        with open(savepath + "\\" + name + ".json", "w") as write_file:
            json.dump(result, write_file)


mywindow = deformCalc()