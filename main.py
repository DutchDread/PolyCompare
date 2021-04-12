# createUI
import maya.cmds as cmds
import pymel.core as pm
import maya.OpenMaya as OpenMaya
import json


class deformCalc(object):
    def __init__(self):

        self.mywin = 'areaCalc'
        self.title = 'deformation Calculator'
        self.size = (200, 400)

        if cmds.window(self.mywin, exists=True):
            cmds.deleteUI(self.mywin, window=True)

        self.window = cmds.window(self.mywin, title=self.title, widthHeight=self.size)

        cmds.columnLayout(adjustableColumn=True)
        cmds.text(label='selected objects')
        itemList = cmds.ls(selection=True)

        self.selectionBox = cmds.textScrollList('itemList', append=itemList)
        self.refreshButton = cmds.button(label='Refresh list', command=self.refreshList, width=200, height=25,
                                         align='center')
        cmds.text(label='Generate raports')
        self.name = cmds.textFieldGrp(label='File Name')
        self.pathFinder = cmds.textFieldButtonGrp(label='Save Path', buttonLabel='Browse',
                                                  buttonCommand=self.browseFiles)
        cmds.separator(height=5)
        self.button = cmds.button(label='Generate Stress Report', command=self.toggleButton)
        self.button2 = cmds.button(label='Generate duplicate VertLoc Report', command=self.getPositions)

        cmds.separator(height=30)
        cmds.text(label='Execute from file')
        self.itemFinder = cmds.textFieldButtonGrp(label='File Path', buttonLabel='Browse',
                                                  buttonCommand=self.browseFiles2)

        self.button3 = cmds.button(label='Set verts to location', command=self.setPositions)

        self.data = []

        cmds.showWindow()

    def refreshList(self, *args):

        cmds.textScrollList(self.selectionBox, e=True, removeAll=True)
        itemList = cmds.ls(selection=True)
        for obj in itemList:
            cmds.textScrollList(self.selectionBox, e=True, append=obj)

    def getPositions(self, *arg):
        items = cmds.textScrollList(self.selectionBox, q=True, ai=True)
        print("items: {}".format(items))
        if not len(items) == 2:
            print("please select two objects")
            raise Exception("incorrect selection amount: Please select 2 items")
        dataSet1 = []
        dataSet2 = []
        x = 0

        # Get vertex locations
        for mesh in items:
            print("getting vertex locations for: {}".format(mesh))
            selectionList = OpenMaya.MSelectionList()
            selectionList.add(mesh)
            dp = OpenMaya.MDagPath()
            selectionList.getDagPath(0, dp)
            print("Dagpath: {}".format(dp.fullPathName()))

            inMeshMPointArray = OpenMaya.MPointArray()
            currentInMeshMFnMesh = OpenMaya.MFnMesh(dp)
            currentInMeshMFnMesh.getPoints(inMeshMPointArray, OpenMaya.MSpace.kWorld)

            if x == 0:
                for i in range( inMeshMPointArray.length() ) :
                    dataSet1.append( [inMeshMPointArray[i][0], inMeshMPointArray[i][1], inMeshMPointArray[i][2]] )
            elif x == 1:
                for i in range( inMeshMPointArray.length() ) :
                    dataSet2.append( [inMeshMPointArray[i][0], inMeshMPointArray[i][1], inMeshMPointArray[i][2]] )

            '''
            for y in range(vertNumber):
                if x == 0:
                    
                    
                    dataSet1.append(iterator.position())
                elif x == 1:
                    dataSet2.append(iterator.position)
            '''

            if x == 0:
                x = 1
            elif x==1:
                x = 0

            #compare vertex positions
            print("dataSet1: {}".format(dataSet1))
            print("dataSet2: {}".format(dataSet2))

            result = self.findIdenticals(dataSet1, dataSet2)
            savepath = cmds.textFieldButtonGrp(self.pathFinder, q=True, tx=True)
            name = cmds.textFieldGrp(self.name, q=True, tx=True)
            if savepath != "" and name != "":
                self.saveData(result)
            else:
                print("savepath or name not specified, not saving file")



    def findIdenticals(self, referenceModel, comparisonModel):
        """
        Returns a list of lists with matching vertex indices in the form of (comparisonModelIndex, referenceModelIndex)

        :param referenceModel: The position list for the vertices of the model you wish to compare against.

        :param comparisonModel: The position list for the vertices of the model that you want to compare to the referenceModel.
        """

        resultList = []

        for comVert in range(len(comparisonModel)):
            for refVert in range(len(referenceModel)):
                if comparisonModel[comVert] == referenceModel[refVert]:
                    lst = [comVert,refVert]
                    resultList.append(lst)
        print("comparison breakdown: {}".format(resultList))
        return(resultList)

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

    def setPositions(self, *args):
        filePath = cmds.textFieldButtonGrp(self.itemFinder, q=True, tx=True)
        input = []
        with open(filePath, 'r') as json_file:
            input = json.load(json_file)
            print("input: {}".format(input))

        items = cmds.textScrollList(self.selectionBox, q=True, ai=True)
        print("items: {}".format(items))
        if not len(items) == 2:
            print("please select two objects")
            raise Exception("incorrect selection amount: Please select 2 items")


        dataSet1 = []
        dataSet2 = []
        x = 0

        # Get vertex locations
        for mesh in items:
            print("getting vertex locations for: {}".format(mesh))
            selectionList = OpenMaya.MSelectionList()
            selectionList.add(mesh)
            dp = OpenMaya.MDagPath()
            selectionList.getDagPath(0, dp)
            print("Dagpath: {}".format(dp.fullPathName()))

            inMeshMPointArray = OpenMaya.MPointArray()
            currentInMeshMFnMesh = OpenMaya.MFnMesh(dp)
            currentInMeshMFnMesh.getPoints(inMeshMPointArray, OpenMaya.MSpace.kWorld)

            if x == 0:
                for i in range( inMeshMPointArray.length() ) :
                    dataSet1.append( [inMeshMPointArray[i][0], inMeshMPointArray[i][1], inMeshMPointArray[i][2]] )
            elif x == 1:
                for i in range( inMeshMPointArray.length() ) :
                    dataSet2.append( [inMeshMPointArray[i][0], inMeshMPointArray[i][1], inMeshMPointArray[i][2]] )

            if x == 0:
                x = 1
            elif x==1:
                x = 0

        #Create new vertexlocation set
        print("dataSet1: {}".format(dataSet1))
        print("dataSet2: {}".format(dataSet2))
        print("input: {}".format(input))
        positions = dataSet1
        print("length input: {}".format(len(input)))

        for iden in input:
            print("iden: {}".format(iden))
            positions[iden[1]] = dataSet2[iden[0]]


        #Setting VertexLocations for 1st input
        selectionList = OpenMaya.MSelectionList()
        selectionList.add(items[0])
        dp = OpenMaya.MDagPath()
        selectionList.getDagPath(0, dp)
        newMesh_array = OpenMaya.MPointArray()

        for vert in positions:
            newMesh_array.append(*vert)

        mSpace = OpenMaya.MSpace.kWorld
        mFnSet = OpenMaya.MFnMesh(dp)
        mFnSet.setPoints(newMesh_array, mSpace)


    def printFunction(self):
        pStatement = cmds.textField('pStatementInput', q=True, text=True)
        print(pStatement)

    def browseFiles(self):

        self.file_path = cmds.fileDialog2(fm=3, okc='select')
        print(self.file_path)
        cmds.textFieldButtonGrp(self.pathFinder, e=True, tx=str(self.file_path[0]))

    def browseFiles2(self):

        self.file_path = cmds.fileDialog2(fm=1, okc='select')
        print(self.file_path)
        cmds.textFieldButtonGrp(self.itemFinder, e=True, tx=str(self.file_path[0]))




    def saveData(self, result):
        savepath = cmds.textFieldButtonGrp(self.pathFinder, q=True, tx=True)
        name = cmds.textFieldGrp(self.name, q=True, tx=True)
        print('savePath: {}'.format(savepath))
        print('name: {}'.format(name))
        with open(savepath + "\\" + name + ".json", "w") as write_file:
            json.dump(result, write_file)

mywindow = deformCalc()