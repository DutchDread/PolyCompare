#createUI
import maya.cmds as cmds
import pymel.core as pm
import maya.OpenMaya as OpenMaya


class deformCalc(object):
    def __init__(self):

        self.window = 'areaCalc'
        self.title = 'deformation Calculator'
        self.size = (600,400)

        if cmds.window(self.window, exists = True):
            cmds.deleteUI(self.window, window = True)

        self.window = cmds.window(self.window, title = self.title, width = self.size[0])

        cmds.columnLayout(adjustableColumn=True)
        cmds.text(label = 'selected objects')
        itemList = cmds.ls(selection = True)

        self.selectionBox = cmds.textScrollList('itemList', append=itemList)
        self.refreshButton = cmds.button(label='Refresh list', command=self.refreshList, width=200, height=25, align='center')
        self.button = cmds.button(label = 'Calculate', command = self.toggleButton)
        cmds.separator(height = 5)

        self.name = cmds.textFieldGrp(label = 'File Name', text ='Editable')
        self.pathFinder = cmds.textFieldButtonGrp(label='Save Path', buttonLabel='Browse', buttonCommand = self.browseFiles)


        cmds.showWindow()

    def refreshList(self, *args):

        cmds.textScrollList(self.selectionBox, e=True, removeAll=True)
        itemList = cmds.ls(selection = True)
        for obj in itemList:
            cmds.textScrollList(self.selectionBox, e=True, append=obj)


    def toggleButton(self, *arg):

        items = cmds.textScrollList(self.selectionBox, q=True, ai=True)
        print("items: {}".format(items))

        for mesh in items:
            selectionList = OpenMaya.MSelectionList()
            selectionList.add(mesh)
            dp = OpenMaya.MDagPath()
            selectionList.getDagPath(0, dp)
            fnMesh = OpenMaya.MFnMesh(dp)

            iterator = OpenMaya.MItMeshPolygon(dp)
            items = iterator.count()
            faceAreas = []
            for x in range(items):
                print(iterator.currentItem())
                faceArea = OpenMaya.MScriptUtil()
                faceAreaPntr = faceArea.asDoublePtr()

                iterator.getArea(faceAreaPntr)
                faceAreas.append(faceArea.getDouble(faceAreaPntr))

                next(iterator)
            print(items)
            print(faceAreas)


    def printFunction(self):
        pStatement = cmds.textField('pStatementInput', q = True, text = True)
        print (pStatement)

    def browseFiles(self):

        self.file_path = cmds.fileDialog2(fm = 3, okc= 'select')
        print(self.file_path)
        cmds.textFieldButtonGrp(self.pathFinder, e=True, tx = str(self.file_path[0]))




mywindow = deformCalc()