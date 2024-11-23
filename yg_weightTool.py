from maya import cmds
import math
import maya.mel as mel
from PySide2.QtGui import QCursor
import maya.OpenMaya as om

'''yg_weightTool.py, small tool to copy/paste, smooth, soft and set weights values'''

'''use:
   ->just drag and n drop on maya to open it
   ->select a mesh, click on "set", choose your deformer and that's it
   ->work with skinCluster, blendshape, cluster, lattice, nonLinear, wire, jiggle, shrinkWrap, deltaMush, tension, proximityWrap and textureDeformer deformers'''

'''base settings:
    ->ctrl + c: copy weights
    ->ctrl + v: paste weights
    ->ctrl + x: set weights
    ->alt + x: smooth weights'''

__author__      = "Yann GENTY"
__email__       = "y.genty.cs@gmail.com"
__version__     = "1.5.0"
__copyright__   = "Copyright (c) 2024, Yann GENTY"

############################## FUNCTIONS ##

class Callback():
    __author__ = "Adrien PARIS"
    __email__ = "a.paris.cs@gmail.com"
    __version__     = "3.1.0"
    __copyright__   = "Copyright 2021, Creative Seeds"

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.repeatArgs = args
        self.kwargs = kwargs
        self.repeatable_value = False
        self.getCommandArgument_value = False

    def repeatable(self):
        ''' Call this methode to make the function repeatable with 'g'
        '''
        self.repeatable_value = True
        return self

    def getCommandArgument(self):
        ''' Call this methode to receive the argument of the event
        '''
        self.getCommandArgument_value = True
        return self

    def _repeatCall(self):
        return self.func(*self.repeatArgs, **self.kwargs)

    def __call__(self, *args):
        ag = self.args + args if self.getCommandArgument_value else self.args
        if self.repeatable_value:
            import __main__
            __main__.cb_repeatLast = self
            self.repeatArgs = ag
            cmds.repeatLast(ac='''python("import __main__; __main__.cb_repeatLast._repeatCall()"); ''')
        return self.func(*ag, **self.kwargs)

def datahotkeys():
    '''manages all shortcut-related information'''
    altCopy = cmds.checkBox("Scb_1a", q=True, v=True) #boolean
    ctrlCopy = cmds.checkBox("Scb_1b", q=True, v=True) #boolean
    letterCopy = cmds.textField("Stf_1", q=True, tx=True)[0] #string #keep only one letter in textfield
    nameCopy = "copyWeight"

    altPaste = cmds.checkBox("Scb_2a", q=True, v=True)
    ctrlPaste = cmds.checkBox("Scb_2b", q=True, v=True)
    letterPaste = cmds.textField("Stf_2", q=True, tx=True)[0]
    namePaste = "pasteWeight"

    altSet = cmds.checkBox("Scb_3a", q=True, v=True)
    ctrlSet = cmds.checkBox("Scb_3b", q=True, v=True)
    letterSet = cmds.textField("Stf_3", q=True, tx=True)[0]
    nameSet = "setWeight"

    altSmooth = cmds.checkBox("Scb_4a", q=True, v=True)
    ctrlSmooth = cmds.checkBox("Scb_4b", q=True, v=True)
    letterSmooth = cmds.textField("Stf_4", q=True, tx=True)[0]
    nameSmooth = "smoothWeight"    

    return [[nameCopy, altCopy, ctrlCopy, letterCopy],[namePaste, altPaste, ctrlPaste, letterPaste],[nameSet, altSet, ctrlSet, letterSet],[nameSmooth, altSmooth, ctrlSmooth, letterSmooth]]

def setHotkeys():
    '''enable/disabled hotkeys'''

    #collect hotkey data
    datas = datahotkeys()

    nameCopy = datas[0][0]
    altCopy = datas[0][1]
    ctrlCopy = datas[0][2]
    letterCopy = datas[0][3]
    cmds.optionVar(intValue=[("altCopy", altCopy),("ctrlCopy", ctrlCopy)], stringValue=[("letterCopy", letterCopy)]) #register in pref

    namePaste = datas[1][0]
    altPaste = datas[1][1]
    ctrlPaste = datas[1][2]
    letterPaste = datas[1][3]
    cmds.optionVar(intValue=[("altPaste", altPaste),("ctrlPaste", ctrlPaste)], stringValue=[("letterPaste", letterPaste)])

    nameSet = datas[2][0]
    altSet = datas[2][1]
    ctrlSet = datas[2][2]
    letterSet = datas[2][3]
    cmds.optionVar(intValue=[("altSet", altSet),("ctrlSet", ctrlSet)], stringValue=[("letterSet", letterSet)])

    nameSmooth = datas[3][0]
    altSmooth = datas[3][1]
    ctrlSmooth = datas[3][2]
    letterSmooth = datas[3][3]
    cmds.optionVar(intValue=[("altSmooth", altSmooth),("ctrlSmooth", ctrlSmooth)], stringValue=[("letterSmooth", letterSmooth)])

    if cmds.button("Sb1", query=True, bgc=True) == COLOR_BASE:
        cmds.hotkey(keyShortcut=letterCopy, ctrlModifier=ctrlCopy, altModifier=altCopy, name="") #erase hotkeys if already exists
        cmds.hotkey(keyShortcut=letterPaste, ctrlModifier=ctrlPaste, altModifier=altPaste, name="")
        cmds.hotkey(keyShortcut=letterSet, ctrlModifier=ctrlSet, altModifier=altSet, name="")
        cmds.hotkey(keyShortcut=letterSmooth, ctrlModifier=ctrlSmooth, altModifier=altSmooth, name="")

        #duplicate the default hotkeyset if its selected (bc we can't add new hotkeys on Maya Default hotkey set)
        if cmds.hotkeySet(q=True, current=True ) == 'Maya_Default':
            cmds.hotkeySet("yg_weightTool", current=True )
            info("creation of a new hotkey set “yg_weightTool”")

        #delete the previous runTimeCommand if it exists
        for rtc in [nameCopy, namePaste, nameSet, nameSmooth]:
            if cmds.runTimeCommand(rtc, exists=True):
                cmds.runTimeCommand(rtc, e=True, delete=True)

        #create runTimCommand customs, commands, and hotkeys
        cmds.runTimeCommand(nameCopy, annotation="copyWeight for yg_weightPaster", category='Custom Scripts', commandLanguage="python", command="copyPaste(1)")
        cmds.nameCommand(nameCopy, ann="copyWeight for yg_weightPaster", c='python("copyPaste(1)")', sourceType="python")
        cmds.hotkey(keyShortcut=letterCopy, ctrlModifier=ctrlCopy, altModifier=altCopy, name=nameCopy)
    
        cmds.runTimeCommand(namePaste, annotation="pasteWeight for yg_weightPaster", category='Custom Scripts', commandLanguage="python", command="copyPaste(2)")
        cmds.nameCommand(namePaste, ann="pasteWeight for yg_weightPaster", c='python("copyPaste(2)")', sourceType="python")
        cmds.hotkey(keyShortcut=letterPaste, ctrlModifier=ctrlPaste, altModifier=altPaste, name=namePaste)

        cmds.runTimeCommand(nameSet, annotation="setWeight for yg_weightPaster", category='Custom Scripts', commandLanguage="python", command="setWeightWindow()")
        cmds.nameCommand(nameSet, ann="setWeight for yg_weightPaster", c='python("setWeightWindow()")', sourceType="python")
        cmds.hotkey(keyShortcut=letterSet, ctrlModifier=ctrlSet, altModifier=altSet, name=nameSet)

        cmds.runTimeCommand(nameSmooth, annotation="smoothWeight for yg_weightPaster", category='Custom Scripts', commandLanguage="python", command="smoothWeight()")
        cmds.nameCommand(nameSmooth, ann="smoothWeight for yg_weightPaster", c='python("smoothWeight()")', sourceType="python")
        cmds.hotkey(keyShortcut=letterSmooth, ctrlModifier=ctrlSmooth, altModifier=altSmooth, name=nameSmooth)

        cmds.button("Sb1", edit=True, bgc=COLOR_VALID)
        message("hotkeys are configured")
        cmds.button("Sb2", edit=True, bgc=COLOR_BASE) #switch on the “save” button

        cmds.textField("Stf_1", e=True, tx=letterCopy) #refresh display
        cmds.textField("Stf_2", e=True, tx=letterPaste)
        cmds.textField("Stf_3", e=True, tx=letterSet)
        cmds.textField("Stf_4", e=True, tx=letterSmooth)

        cmds.menuItem("mi1", edit=True, label=annSettingsButton("copy")) #refresh UI
        cmds.menuItem("mi2", edit=True, label=annSettingsButton("paste"))
        cmds.menuItem("mi3", edit=True, label=annSettingsButton("set"))
        cmds.menuItem("mi4", edit=True, label=annSettingsButton("smooth"))

    else:
        #delete hotkey assignation, runTimeCommand and Command (can't restore hotkey to base maya's setting)

        cmds.hotkey(keyShortcut=letterCopy, ctrlModifier=ctrlCopy, altModifier=altCopy, n="")
        cmds.hotkey(keyShortcut=letterPaste, ctrlModifier=ctrlPaste, altModifier=altPaste, n="")
        cmds.hotkey(keyShortcut=letterSet, ctrlModifier=ctrlSet, altModifier=altSet, n="")
        cmds.hotkey(keyShortcut=letterSmooth, ctrlModifier=ctrlSmooth, altModifier=altSmooth, n="")

        for rtc in [nameCopy, namePaste, nameSet, nameSmooth]:
            if cmds.runTimeCommand(rtc, exists=True):
                cmds.runTimeCommand(rtc, e=True, delete=True)

        for index in range(1, cmds.assignCommand(q=True, numElements=True) + 1): #list index of all commands and delete our own (start from 1 and not 0 otherwise maya bug)
            if cmds.assignCommand(index, q=True, name=True) in [nameCopy,namePaste,nameSet,nameSmooth]:
                cmds.assignCommand(index, e=True, delete=True)      

        cmds.button("Sb1", edit=True, bgc=COLOR_BASE)
        message("hotkeys are removed")

def saveHotkeys():
    '''enable/disabled if shortcuts are saved for the next time Maya is opened'''

    #collect hotkey data
    datas = datahotkeys()

    altCopy = datas[0][1]
    ctrlCopy = datas[0][2]
    letterCopy = datas[0][3]

    altPaste = datas[1][1]
    ctrlPaste = datas[1][2]
    letterPaste = datas[1][3]
    
    altSet = datas[2][1]
    ctrlSet = datas[2][2]
    letterSet = datas[2][3]
    
    altSmooth = datas[3][1]
    ctrlSmooth = datas[3][2]
    letterSmooth = datas[3][3]
   
    if cmds.button("Sb2", q=True, bgc=True) == COLOR_BASE:
        cmds.hotkey(autoSave=True)

        cmds.optionVar(intValue=[("altCopy", altCopy),("ctrlCopy", ctrlCopy)], stringValue=[("letterCopy", letterCopy)]) #save in Prefs
        cmds.optionVar(intValue=[("altPaste", altPaste),("ctrlPaste", ctrlPaste)], stringValue=[("letterPaste", letterPaste)])
        cmds.optionVar(intValue=[("altSet", altSet),("ctrlSet", ctrlSet)], stringValue=[("letterSet", letterSet)])
        cmds.optionVar(intValue=[("altSmooth", altSmooth),("ctrlSmooth", ctrlSmooth)], stringValue=[("letterSmooth", letterSmooth)])

        cmds.savePrefs(g=True)

        cmds.button("Sb2", e=True, bgc=COLOR_VALID)
        message("hotkeys are saved")
    else:
        cmds.hotkey(autoSave=False)

        cmds.optionVar(remove=["altCopy","ctrlCopy","letterCopy","altPaste","ctrlPaste","letterPaste","altSet","ctrlSet","letterSet","altSmooth","ctrlSmooth","letterSmooth"])

        cmds.button("Sb2", e=True, bgc=COLOR_BASE)
        message("hotkeys are no longer saved")

def resetHotkeys():
    '''reset all hotkeys to default setting'''
    cmds.button("Sb1", e=True, bgc=COLOR_BASE)

    cmds.checkBox("Scb_1a", e=True, v=False)
    cmds.checkBox("Scb_1b", e=True, v=True)
    cmds.textField("Stf_1", e=True, tx="c")

    cmds.checkBox("Scb_2a", e=True, v=False)
    cmds.checkBox("Scb_2b", e=True, v=True)
    cmds.textField("Stf_2", e=True, tx="v")

    cmds.checkBox("Scb_3a", e=True, v=False)
    cmds.checkBox("Scb_3b", e=True, v=True)
    cmds.textField("Stf_3", e=True, tx="x")

    cmds.checkBox("Scb_4a", e=True, v=True)
    cmds.checkBox("Scb_4b", e=True, v=False)
    cmds.textField("Stf_4", e=True, tx="x")

    setHotkeys()

def autoFrame():
    if cmds.menuItem("cb0", query=True, checkBox=True):
        cmds.viewFit(an=True)

def openTool():
    deformer = cmds.textScrollList("tsl", query=True, selectItem=True)
    if "." in deformer[0]:
        cmds.select(cmds.textField("tf0", q=True, tx=True))

        if not cmds.artAttrCtx("artAttrBlendShapeContext", q=True, exists=True):
            cmds.artAttrCtx("artAttrBlendShapeContext", i1="paintBlendshape.png", whichTool="blendShapeWeights")
                        
        if not cmds.artAttrCtx("artBlendShapeSelectTarget", q=True, exists=True):
            mel.eval('source "artAttrBlendShapeProperties"')

        shape =  cmds.textScrollList("tsl", query=True, selectItem=True)[0].split(".")[1]
        cmds.artAttrCtx("artAttrBlendShapeContext", e=True, toolOnProc='artBlendShapeSelectTarget artAttrCtx "{}";'.format(shape))

        cmds.ArtPaintBlendShapeWeightsTool()
        cmds.toolPropertyWindow()

        #old one
        #mel.eval('artBlendShapeSelectTarget artAttrCtx "{}";'.format(cmds.textScrollList("tsl", query=True, selectItem=True)[0].split(".")[1]))          

    elif cmds.nodeType(deformer) == "skinCluster":
        cmds.ArtPaintSkinWeightsTool()
        cmds.toolPropertyWindow()
    else:
        cmds.ArtPaintAttrTool()
        mel.eval('artSetToolAndSelectAttr( "artAttrCtx", "cluster.{}.weights" );'.format(cmds.textScrollList("tsl", query=True, selectItem=True)[0]))
        cmds.toolPropertyWindow()

def setObject(index):
    '''Analyzes the selected object and verifies that it is a mesh with a shape, and lists the deformers present in its history.'''

    oldSel = cmds.textScrollList("tsl", query=True, selectItem=True)
    cmds.textScrollList("tsl", edit=True, ra=True) #reset list
    if index == 0:  #define whether the function is started by the “set” button or by one of the filter checkboxes
        sel = cmds.ls(sl=True)
    if index == 1:
        sel = [cmds.textField("tf0", q=True, tx=True)]
        if sel == ['']: #if nothing is selected, stop the function
            return

    if not len(sel):
        message("select at least one object")
        cmds.textField("tf0", edit=True, tx="")
        return
    
    else:
        if cmds.listRelatives(sel[0], shapes=True) and cmds.nodeType(sel[0]) == "transform": #if transform with shape
            if len(sel) > 1:
                message("select only one object")
                cmds.textField("tf0", edit=True, tx="")
                return
            else:
                sel = sel[0]   
        elif "[" in sel[0]: #if sel is a vertex, then select his mesh 
            sel = sel[0].split(".")[0]
        else:
            message("object must be a mesh")
            cmds.textField("tf0", edit=True, tx="")
            return
    
        cmds.textField("tf0", edit=True, tx=sel)
        message("")

        deformers = []
        if not cmds.listHistory(sel, pdo=True):
            message("object has no deformers")
            cmds.textField("tf0", edit=True, tx="")
            return

        else:
            for inputNode in cmds.listHistory(sel, pdo=True):
                if cmds.nodeType(inputNode) in listFilter():
                    if cmds.nodeType(inputNode) == "blendShape": #custom system to add all blendshape targets
                        targets = [str(inputNode) + "." +  shapes for shapes in cmds.listAttr(inputNode + '.w', multi=True)]
                        for target in targets:
                            cmds.textScrollList("tsl", edit=True, a=[str(target)])
                            deformers.append(target)
                    else:
                        cmds.textScrollList("tsl", edit=True, a=[str(inputNode)])
                        deformers.append(inputNode)

            if not deformers:
                message("object has no visible deformers")

     
    
    if oldSel: #reselect old selection if it refreshes
        try:
            oldSel[0]
            if oldSel[0] in cmds.textScrollList("tsl", query=True, allItems=True):
                cmds.textScrollList("tsl", edit=True, selectItem=oldSel[0])
        except:
            return

def selectInfluence(index):
    '''Select all vertices influenced by the selected deformer, only on mesh selected or not'''
    sel = cmds.textScrollList("tsl", query=True, selectItem=True)
    if sel:
        cmds.select(cmds.deformer(sel, query=True, cmp=True), r=True)
        cmds.polyListComponentConversion(cmds.ls(sl=True, flatten=True), toVertex=True)
        
        selectList = []
        if index == 1:
            for vertice in cmds.ls(sl=True, flatten=True):
                if cmds.textField("tf0", query=True, tx=True) in vertice:
                    selectList.append(vertice)
        else:
            selectList = cmds.ls(sl=True, flatten=True)

        cmds.select(selectList, r=True)
        info("select:" + str(selectList))

        autoFrame()
    else:
        message("select a deformer")

def checkDeformer(vtx, deformerSet):
    '''verify if vertex is part of deformer's influence'''
    if vtx in cmds.ls(cmds.sets(deformerSet, query=True), flatten=True):
        return True
    else:
        return False

def copyPaste(index):
    '''collect, calcul, paste values, differents way for skinCluster, blendshapes and other deformers'''
    global pasteWeight
    global pasteWeightSkin

    if not  cmds.textScrollList("tsl", query=True, selectItem=True):
        message("select a deformer")
        return
    else:


        if index == 1:
            pasteWeightSkin.clear() #clean weights values before copy
            #check deformer's datas
            deformer = cmds.textScrollList("tsl", query=True, selectItem=True)[0]
            sel = cmds.ls(cmds.polyListComponentConversion(cmds.ls(sl=True, flatten=True), toVertex=True), flatten=True)
            deformerSet = cmds.listConnections(deformer, type="objectSet")

            if "." in deformer: #additionnal datas for blendshapes   
                target = deformer.split(".")[1] #separate blendshape and target name
                deformer_bs = deformer.split(".")[0] 
                targetIndex = str(cmds.listAttr(deformer_bs + '.w', m=True).index(target))
                deformerSet = cmds.listConnections(deformer_bs, type="objectSet")

            if not sel:
                message("select vertex")
                return
            else:
                #1. collect values
                weightList=[]
                if cmds.nodeType(deformer) == "skinCluster": #if skinCluster
                    jointsList = []
                    iList = []
                    for vtx in sel: #query all joints that influenced selected vtx
                        weightList = cmds.skinPercent(deformer, vtx, query=True, value=True)
                        for weight in weightList:
                            if weight > 0.001:
                                i = weightList.index(weight)
                                if not i in iList:
                                   iList.append(i) 
                    for i in iList:
                        jointsList.append([cmds.skinCluster(deformer, query=True, inf=True)[i], i])

                    joints = []
                    for joint in jointsList: #query weights on selected vtx for these joints
                        weight = []
                        for vtx in cmds.ls(sel, flatten=True):
                            weight.append(cmds.skinPercent(deformer, vtx, query=True, value=True)[int(joint[1])])

                        joints.append([joint[0], weight])
      
                else:    
                    for vtx in sel:
                        if checkDeformer(vtx, deformerSet): #verify if vertex is part of deformer's influence, else weight value is set at 0
                            if "." in deformer:                          #if blendshape
                                vtxIndex = vtx.split("[")[1][:-1]

                                weight = cmds.getAttr(deformer_bs + ".inputTarget[0].inputTargetGroup[" + targetIndex + "].targetWeights[" + vtxIndex + "]")
                                weightList.append(weight)

                            else:                                        #other deformers
                                weight = cmds.percent(deformer, vtx, query=True, value=True)[0]
                                weightList.append(weight)
                                
                        else:
                            weight = 0
                            weightList.append(weight)
                            info(vtx + " don't part of '"+ deformer +"', his weight is set to 0")

                #2. sum values
                if cmds.nodeType(deformer) == "skinCluster":
                    msg = ""
                    i=0
                    for joint in joints:
                        weights = joints[i][1]
                        bone = joint[0]
                        value = round(math.fsum(weights) / len(weights), 3)
                        pasteWeightSkin.append((bone, value))
                        msg = msg + bone + ":" + str(value) +", "
                        i+=1
                    info("copy " + msg)
              
                else:
                    pasteWeight  = round(math.fsum(weightList) / len(weightList), 3)
                    message("copy " + str(pasteWeight))              

        elif index == 2:
            #check deformer's datas (bc user can change between copy and paste)
            deformer = cmds.textScrollList("tsl", query=True, selectItem=True)[0]
            sel = cmds.ls(cmds.polyListComponentConversion(cmds.ls(sl=True, flatten=True), toVertex=True), flatten=True)
            deformerSet = cmds.listConnections(deformer, type="objectSet")

            if "." in deformer: #additionnal datas for blendshapes   
                target = deformer.split(".")[1] #separate blendshape and target name
                deformer_bs = deformer.split(".")[0] 
                targetIndex = str(cmds.listAttr(deformer_bs + '.w', m=True).index(target))
                deformerSet = cmds.listConnections(deformer_bs, type="objectSet")
            
            if not sel:
                message("select vertex")
                return
            else:
                if cmds.nodeType(deformer) == "skinCluster": #if skinCluster            [['A', 0.5], ['B', 0.5]] -> ( string, float ), 
                    i = 0
                    for vtx in sel:
                        if not checkDeformer(vtx, deformerSet):
                            info(vtx + " isn't in '" + deformer + "', paste not applied")
                            i += 1
                            pass
                        else:
                            print(pasteWeightSkin)
                            cmds.skinPercent(deformer, vtx, transformValue=pasteWeightSkin)
                            i += 1
                elif "." in deformer:                        #if blendshape
                    for vtx in sel:
                        vtxIndex = vtx.split("[")[1][:-1]
                        cmds.setAttr(deformer_bs + ".inputTarget[0].inputTargetGroup[" + targetIndex + "].targetWeights[" + vtxIndex + "]", pasteWeight) 
                    message("paste " + str(pasteWeight))
                else:                                        #other deformers
                    autoAdd(sel, deformer)
                    for vtx in sel:                          
                        if not checkDeformer(vtx, deformerSet):
                            info(vtx + " isn't in '" + deformer + "', paste not applied")
                            pass
                        else:                        
                            cmds.percent(deformer, vtx, value=pasteWeight)               
                    message("paste " + str(pasteWeight))

def smoothWeight():
    '''smooth weight, depend than deformer selected'''
    if not cmds.textScrollList("tsl", query=True, selectItem=True):
        message("select a deformer")
        return
    else:
        deformer = cmds.textScrollList("tsl", query=True, selectItem=True)[0]
        sel = cmds.ls(sl=True, fl=True) 
        if sel and "vtx" in sel[0]:
            if "." in deformer:
                baseSel = cmds.ls(sl=True, fl=True)
                mesh = cmds.textField("tf0", q=True, tx=True)

                cmds.select(mesh) #need to select mesh when load tool to prevent error message
                cmds.ArtPaintBlendShapeWeightsTool()
                mel.eval('artBlendShapeSelectTarget artAttrCtx "{}";'.format(cmds.textScrollList("tsl", query=True, selectItem=True)[0].split(".")[1]))

                cmds.select(baseSel) #reselect vtx base sel before smooth their weights

                backSAO = cmds.artAttrCtx(cmds.currentCtx(), q=True, sao=True) #save old settings
                backValue = cmds.artAttrCtx(cmds.currentCtx(), q=True, value=True)

                cmds.artAttrCtx(cmds.currentCtx(), e=True, sao="smooth") #smooth weights
                cmds.artAttrCtx(cmds.currentCtx(), e=True, colorfeedback=False)
                cmds.artAttrCtx(cmds.currentCtx(), e=True, value=1)
                cmds.artAttrCtx(cmds.currentCtx(), e=True, clear=True)
                cmds.artAttrCtx(cmds.currentCtx(), e=True, colorfeedback=True)

                cmds.artAttrCtx(cmds.currentCtx(), e=True, sao=backSAO) #go back to old settings
                cmds.artAttrCtx(cmds.currentCtx(), e=True, value=backValue)

                mel.eval("setToolTo $gSelect") #return to selection tool, and select base vtx sel on mesh
                mel.eval('doMenuComponentSelectionExt("{}", "{}", 0);'.format(mesh,"vertex"))
                cmds.select(baseSel)

            elif cmds.nodeType(deformer) == "skinCluster":
                mel.eval('doSmoothSkinWeightsArgList 3 { "0", "5", "0", "1"   }')

            else:
                addSel = autoAdd(sel, deformer)
                if addSel:
                    cmds.select(addSel, add=True)

                cmds.ArtPaintAttrTool()
                mel.eval('artSetToolAndSelectAttr( "artAttrCtx", "cluster.{}.weights" );'.format(cmds.textScrollList("tsl", query=True, selectItem=True)[0]))

                backSAO = cmds.artAttrCtx(cmds.currentCtx(), q=True, sao=True) #save old settings
                backValue = cmds.artAttrCtx(cmds.currentCtx(), q=True, value=True)

                cmds.artAttrCtx(cmds.currentCtx(), e=True, sao="smooth")
                cmds.artAttrCtx(cmds.currentCtx(), e=True, colorfeedback=False)
                cmds.artAttrCtx(cmds.currentCtx(), e=True, value=1)
                cmds.artAttrCtx(cmds.currentCtx(), e=True, clear=True)
                cmds.artAttrCtx(cmds.currentCtx(), e=True, colorfeedback=True)

                cmds.artAttrCtx(cmds.currentCtx(), e=True, sao=backSAO) #go back to old settings
                cmds.artAttrCtx(cmds.currentCtx(), e=True, value=backValue)
                
                mel.eval("setToolTo $gSelect")

            message("smooth applied")
        else:
            message("select vertex")

def setWeight(deformer, sel):
    '''set a new weight on the selected vertex, dont work for skinCluster'''
    weight = cmds.floatField("ff", query=True, value=True)
    cmds.deleteUI("AWwin")
    
    if "." in deformer: #if blendshape
        target = deformer.split(".")[1]
        deformer_bs = deformer.split(".")[0] 
        targetIndex = str(cmds.listAttr(deformer_bs + '.w', m=True).index(target))

        for vtx in sel:
            vtxIndex = vtx.split("[")[1][:-1]
            cmds.setAttr(deformer_bs + ".inputTarget[0].inputTargetGroup[" + targetIndex + "].targetWeights[" + vtxIndex + "]", weight) 
        message("set " + str(weight))

    else:               #other deformers 
        for vtx in sel:
            cmds.percent(deformer, vtx, value=weight)               
        message("set " + str(weight))

def softWeight():
    sel = cmds.ls(sl=True)
    deformer = cmds.textScrollList("tsl", query=True, selectItem=True)[0]

    if cmds.nodeType(deformer) == "skinCluster":
        message("does not work for skinCluster")
        return
    else:
        if not sel:
            message("selection is empty")
            return
        else:
            if not "vtx" in sel[0]: 
                message("select vertex")
                return
            else:
                if not cmds.softSelect(query=True, softSelectEnabled=True):
                    message("activate soft selection")
                    return
                else:
                    selection = om.MSelectionList()
                    softSelection = om.MRichSelection()
                    om.MGlobal.getRichSelection(softSelection)
                    softSelection.getSelection(selection)
                    
                    dagPath = om.MDagPath()
                    component = om.MObject()
                    
                    iter = om.MItSelectionList(selection,om.MFn.kMeshVertComponent)
                    elements = []
                    while not iter.isDone(): 
                        iter.getDagPath(dagPath, component)
                        dagPath.pop()
                        node = dagPath.fullPathName()
                        fnComp = om.MFnSingleIndexedComponent(component)   
                                
                        for i in range(fnComp.elementCount()):
                            elements.append([node, fnComp.element(i), fnComp.weight(i).influence()] )
                        iter.next()

                    selection = ["%s.vtx[%d]" % (el[0], el[1])for el in elements] 

                    if "." in deformer: #if blendshape
                        target = deformer.split(".")[1]
                        deformer_bs = deformer.split(".")[0] 
                        targetIndex = str(cmds.listAttr(deformer_bs + '.w', m=True).index(target))

                        for i in range(len(elements)):
                            vtxIndex = selection[i].split("[")[1][:-1]
                            cmds.setAttr(deformer_bs + ".inputTarget[0].inputTargetGroup[" + targetIndex + "].targetWeights[" + vtxIndex + "]", elements[i][2]) 

                    else: #if other deformers
                        for i in range(len(elements)):
                            cmds.percent(deformer, selection[i], v=elements[i][2])

                    message("soft weight done")

def addWeight():
    '''add selected component (only vertex) in selected deformer influence'''
    deformer = cmds.textScrollList("tsl", query=True, selectItem=True)[0]
    deformerSet = cmds.listConnections(deformer, type="objectSet")[0]
    sel = cmds.ls(sl=True, fl=True)
    if cmds.nodeType(deformer) == "skinCluster" or "." in deformer:
        message("work only for common deformers")
        return
    else:
        for component in sel:
            if not "vtx" in component:
                message("select only vertex")
                return
        for vtx in sel:
            cmds.sets(vtx, add=deformerSet)
        message("vertex add in " + deformer)

def autoAdd(sel, deformer):
    '''automatically adds vertex that are not in the deformer set'''
    if not cmds.menuItem("cb9", q=True, checkBox=True) :
        return
    else:
        deformerSet = cmds.listConnections(deformer, type="objectSet")[0]
        setMembers = cmds.ls(cmds.sets(deformerSet, query=True), flatten=True)
        vtxList = [vtx for vtx in sel if vtx not in setMembers]   
        
        if vtxList: #add vtx in deformer and set them at 0, then return vtx list
            cmds.sets(vtxList, add=deformerSet)
            cmds.percent(deformer, vtxList, v=0)
            return vtxList
        else:
            return None

#################################### LIB ##

global pasteWeight
pasteWeightSkin = []
COLOR_BASE = [0.3600061036087587, 0.3600061036087587, 0.3600061036087587]
COLOR_VALID = [0.467002365148394, 0.7689936675059129, 0.25099565117875944]

########################### UI FUNCTIONS ##

def info(text):
    '''print infos in warning bar'''
    print(" ")
    mel.eval('trace -where ""; print "{}"; trace -where "";'.format(text))

def message(text):
    '''print info in the UI'''
    cmds.text("text", edit=True, l=text)

def listFilter():
    '''update filter list according to parameters checkbox'''
    filters = []
    for deformerType in ["skinCluster", "blendShape", "cluster", "lattice", "nonLinear", "wire", "jiggle","shrinkWrap","deltaMush","tension","proximityWrap","textureDeformer"]:
        if cmds.menuItem("cb_" + deformerType, query=True, checkBox=True):
            filters.append(deformerType)
    return filters

def changeTitle():
    '''change popup menu's title according to the deformer selected'''
    cmds.menuItem("dvd0", e=True, l=str(cmds.textScrollList("tsl", query=True, selectItem=True)[0]))

def showAll():
        '''check on all checkbox'''
        for deformerType in ["skinCluster", "blendShape", "cluster", "lattice", "nonLinear", "wire", "jiggle","shrinkWrap","deltaMush","tension","proximityWrap","textureDeformer"]:
            cmds.menuItem("cb_" + deformerType, edit=True, checkBox=True)
        setObject(1)

def showNone():
        '''check off all checkbox'''
        for deformerType in ["skinCluster", "blendShape", "cluster", "lattice", "nonLinear", "wire", "jiggle","shrinkWrap","deltaMush","tension","proximityWrap","textureDeformer"]:
            cmds.menuItem("cb_" + deformerType, edit=True, checkBox=False)
        setObject(1)

def resetSetButton():
    '''reset set button when hotkey setting change and delete all related data'''

    cmds.button("Sb1", e=True, bgc=COLOR_VALID) #fake state of buttons for delete hotkey's datas
    cmds.button("Sb2", e=True, bgc=COLOR_VALID)

    setHotkeys()
    saveHotkeys()
    message("")

def annSettingsButton(index):
    '''manage right-click for the settings button'''
    CopyString = "copy: " + str("Alt+" if cmds.checkBox("Scb_1a", q=True, v=True) else "") + str("Ctrl+" if cmds.checkBox("Scb_1b", q=True, v=True) else "") + str(cmds.textField("Stf_1", q=True, tx=True))
    PasteString = "paste: " + str("Alt+" if cmds.checkBox("Scb_2a", q=True, v=True) else "") + str("Ctrl+" if cmds.checkBox("Scb_2b", q=True, v=True) else "") + str(cmds.textField("Stf_2", q=True, tx=True))
    SetString = "set: " + str("Alt+" if cmds.checkBox("Scb_3a", q=True, v=True) else "") + str("Ctrl+" if cmds.checkBox("Scb_3b", q=True, v=True) else "") + str(cmds.textField("Stf_3", q=True, tx=True))
    SmoothString = "smooth: " + str("Alt+" if cmds.checkBox("Scb_4a", q=True, v=True) else "") + str("Ctrl+" if cmds.checkBox("Scb_4b", q=True, v=True) else "") + str(cmds.textField("Stf_4", q=True, tx=True))

    for string in [CopyString, PasteString, SetString, SmoothString]:
        if index == string.split(":")[0]:
            return string

def openSettingsWindow():
    '''just opens the settings window, modifying its values according to the previous session'''

    if cmds.runTimeCommand("copyWeight", exists=True): #verify if at least one runTimeCommand is present

        cmds.button("Sb1", edit=True, bgc=COLOR_VALID) #initialize kotkeys buttons ("save"/"set")
        cmds.button("Sb2", edit=True, bgc=COLOR_VALID) 
    
        for hotkey, index in zip(["Copy", "Paste", "Set", "Smooth"],[1, 2, 3, 4]): #copies existing shortcuts
            altValue = cmds.optionVar(q="alt" + hotkey)
            cmds.checkBox("Scb_" + str(index) + "a", e=True, v=altValue)

            ctrlValue = cmds.optionVar(q="ctrl" + hotkey)
            cmds.checkBox("Scb_" + str(index) + "b", e=True, v=ctrlValue)            
            
            letterValue = cmds.optionVar(q="letter" + hotkey)
            cmds.textField("Stf_" + str(index), e=True, tx=letterValue)

    cmds.showWindow("Settings") #open window

##################################### UI ##

def setWeightWindow():
    '''open context window to set new weight on sel'''
    deformer = cmds.textScrollList("tsl", query=True, selectItem=True)
    sel = cmds.ls(sl=True, fl=True)
    if not deformer :
        message("select a deformer")
        return
    else:
        if not sel:
            message("empty selection")
            return
        else:
            if not ".vtx" in sel[0]:
                message("select vertex")
                return
            else:
                if cmds.nodeType(deformer) == "skinCluster":
                    message("does not work for skinCluster")
                    return
                else:
                    if cmds.window("AWwin", exists=True):
                        cmds.deleteUI("AWwin")
                

                    cmds.window("AWwin", tlb=True, t=deformer[0])
                    AWform = cmds.formLayout(h=40, p="AWwin")
                    cmds.floatField("ff", p=AWform, pre=3, cc=Callback(setWeight, deformer[0], sel))
                    cmds.formLayout(AWform, edit=True, attachForm=[("ff", 'bottom', 0),("ff", 'top', 0),("ff", 'left', 0),("ff", 'right', 0)])
                    cmds.showWindow("AWwin")

                    coordX, coordY = QCursor.pos().x(), QCursor.pos().y() #get pointer global position on screen
                    cmds.window("AWwin", edit=True, topLeftCorner=[50+coordY, 50+coordX])

def settingsWindow():
    '''create window for all settings'''
    cmds.window("Settings", tlb=True, t="Settings", ret=True)  #ret=retains the window after it has been closed
    Sform = cmds.formLayout("ahahah", p="Settings", numberOfDivisions=100, h=150, w=250)

    St_1 = cmds.text("St_1", p=Sform, l="copy: ", al="right")
    Scb_1a = cmds.checkBox("Scb_1a", p=Sform, l="Alt", v=False, cc=Callback(resetSetButton))
    Scb_1b = cmds.checkBox("Scb_1b", p=Sform, l="Ctrl", v=True, cc=Callback(resetSetButton))
    Stf_1 = cmds.textField("Stf_1", p=Sform, tx="c", cc=Callback(resetSetButton))

    St_2 = cmds.text("St_2", p=Sform, l="paste: ", al="right")
    Scb_2a = cmds.checkBox("Scb_2a", p=Sform, l="Alt", v=False, cc=Callback(resetSetButton))
    Scb_2b = cmds.checkBox("Scb_2b", p=Sform, l="Ctrl", v=True, cc=Callback(resetSetButton))
    Stf_2 = cmds.textField("Stf_2", p=Sform, tx="v", cc=Callback(resetSetButton))

    St_3 = cmds.text("St_3", p=Sform, l="set: ", al="right")
    Scb_3a = cmds.checkBox("Scb_3a", p=Sform, l="Alt", v=False, cc=Callback(resetSetButton))
    Scb_3b = cmds.checkBox("Scb_3b", p=Sform, l="Ctrl", v=True, cc=Callback(resetSetButton))
    Stf_3 = cmds.textField("Stf_3", p=Sform, tx="x", cc=Callback(resetSetButton))

    St_4 = cmds.text("St_4", p=Sform, l="smooth: ", al="right")
    Scb_4a = cmds.checkBox("Scb_4a", p=Sform, l="Alt", v=True, cc=Callback(resetSetButton))
    Scb_4b = cmds.checkBox("Scb_4b", p=Sform, l="Ctrl", v=False, cc=Callback(resetSetButton))
    Stf_4 = cmds.textField("Stf_4", p=Sform, tx="x", cc=Callback(resetSetButton))

    Sb1 = cmds.button("Sb1", parent=Sform, l="set", ann="set hotkeys", c=Callback(setHotkeys), bgc=COLOR_BASE)
    Sb2 = cmds.button("Sb2", parent=Sform, l="save", ann="save hotkeys fort next maya launch", c=Callback(saveHotkeys))
    Sb3 = cmds.button(parent=Sform, l="reset", c=Callback(resetHotkeys))

    #layout
    #1st line
    cmds.formLayout(Sform, edit=True, attachForm=[(St_1, 'top', 2.5),(Scb_1a, 'top', 2.5),(Scb_1b, 'top', 2.5),(Stf_1, 'top', 2.5),(St_1, 'left', 2.5),(Stf_1, 'right', 2.5)],
                                    attachPosition=[(St_1, 'right', 2.5, 25),(Scb_1a, 'left', 2.5, 25),(Scb_1a, 'right', 2.5, 50),(Scb_1b, 'left', 2.5, 50),(Scb_1b, 'right', 2.5, 75),(Stf_1, 'left', 2.5, 75),
                                                    (St_1, 'bottom', 2.5, 20),(Scb_1a, 'bottom', 2.5, 20),(Scb_1b, 'bottom', 2.5, 20),(Stf_1, 'bottom', 2.5, 20)])
    #2nd line
    cmds.formLayout(Sform, edit=True, attachForm=[(St_2, 'left', 2.5),(Stf_2, 'right', 2.5)],
                                    attachPosition=[(St_2, 'top', 2.5, 20),(Scb_2a, 'top', 2.5, 20),(Scb_2b, 'top', 2.5, 20),(Stf_2, 'top', 2.5, 20),
                                                    (St_2, 'bottom', 2.5, 40),(Scb_2a, 'bottom', 2.5, 40),(Scb_2b, 'bottom', 2.5, 40),(Stf_2, 'bottom', 2.5, 40),
                                                    (St_2, 'right', 2.5, 25),(Scb_2a, 'left', 2.5, 25),(Scb_2a, 'right', 2.5, 50),(Scb_2b, 'left', 2.5, 50),(Scb_2b, 'right', 2.5, 75),(Stf_2, 'left', 2.5, 75)])
    #3rd line
    cmds.formLayout(Sform, edit=True, attachForm=[(St_3, 'left', 2.5),(Stf_3, 'right', 2.5)],
                                    attachPosition=[(St_3, 'top', 2.5, 40),(Scb_3a, 'top', 2.5, 40),(Scb_3b, 'top', 2.5, 40),(Stf_3, 'top', 2.5, 40),
                                                    (St_3, 'bottom', 2.5, 60),(Scb_3a, 'bottom', 2.5, 60),(Scb_3b, 'bottom', 2.5, 60),(Stf_3, 'bottom', 2.5, 60),
                                                    (St_3, 'right', 2.5, 25),(Scb_3a, 'left', 2.5, 25),(Scb_3a, 'right', 2.5, 50),(Scb_3b, 'left', 2.5, 50),(Scb_3b, 'right', 2.5, 75),(Stf_3, 'left', 2.5, 75)])
    #4th line
    cmds.formLayout(Sform, edit=True, attachForm=[(St_4, 'left', 2.5),(Stf_4, 'right', 2.5)],
                                    attachPosition=[(St_4, 'top', 2.5, 60),(Scb_4a, 'top', 2.5, 60),(Scb_4b, 'top', 2.5, 60),(Stf_4, 'top', 2.5, 60),
                                                    (St_4, 'bottom', 2.5, 80),(Scb_4a, 'bottom', 2.5, 80),(Scb_4b, 'bottom', 2.5, 80),(Stf_4, 'bottom', 2.5, 80),
                                                    (St_4, 'right', 2.5, 25),(Scb_4a, 'left', 2.5, 25),(Scb_4a, 'right', 2.5, 50),(Scb_4b, 'left', 2.5, 50),(Scb_4b, 'right', 2.5, 75),(Stf_4, 'left', 2.5, 75)])
    #5th line
    cmds.formLayout(Sform, edit=True, attachForm=[(Sb1, 'left', 3),(Sb3, 'right', 3),(Sb1, 'bottom', 4),(Sb2, 'bottom', 4),(Sb3, 'bottom', 4)],
                                    attachPosition=[(Sb1, 'right', 2.5, 33),(Sb2, 'left', 2.5, 33),(Sb2, 'right', 2.5, 66),(Sb3, 'left', 2.5, 66)],
                                    attachNone=[(Sb1, 'top'),(Sb2, 'top'),(Sb3, 'top')])

def mainWindow():
    W_NAME = "yg_weightTool"
    #checks if windows are already open
    if cmds.workspaceControl(W_NAME, query=True, exists=True):
        cmds.deleteUI(W_NAME)
    if cmds.window("AWwin", exists=True):
        cmds.deleteUI("AWwin")
    if cmds.window("Settings", exists=True):
        cmds.deleteUI("Settings")

    #main windows
    settingsWindow() #setup settings window without open it
    cmds.workspaceControl(W_NAME)

    #buttons
    form =  cmds.formLayout(numberOfDivisions=100, w=240, h=243)
    t0 = cmds.text(l="object", al="right")
    tf0 = cmds.textField("tf0", tx="")
    b0 = cmds.button(l="set", h=20, ann="set objets selection", c=Callback(setObject,0).repeatable())
    tsl = cmds.textScrollList("tsl", bgc=COLOR_BASE, ann="right-click to see options", ams=False, sc=Callback(changeTitle))
    t1 = cmds.text("text", l="")
    b1 = cmds.button("b1", l="settings", ann="right click to see current settings", c=Callback(openSettingsWindow), bgc=COLOR_BASE)

    #layout
    cmds.formLayout(form, edit=True, 
                    attachForm=[(tsl, 'left', 4.5),(tsl, 'right', 4.5),(tsl, 'top', 5),(b1, 'left', 5),(b1, 'right', 5),(b1, 'bottom', 5),(t1, 'left', 5),(t1, 'right', 5),(t0, 'top', 9),(tf0, 'top', 5),(b0, 'top', 5),(t0, 'left', 5),(b0, 'right', 5)],
                    attachPosition=[(tsl, 'bottom', 0, 75),(t0, 'right', 2.5, 25,),(tf0, 'left', 2.5, 25,),(tf0, 'right', 2.5, 75,),(b0, 'left', 2.5, 75,)],
                    attachNone=[(b1, 'top'),(t0, 'bottom'),(tf0, 'bottom'),(b0, 'bottom')],
                    attachControl=[(t1, 'top', 5, tsl),(t1, 'bottom', 5, b1),(tsl, 'top', 6, t0)])

    #popup menus
    ppm = cmds.popupMenu(parent="tsl", button=3)
    cmds.menuItem("dvd0", parent=ppm, label="", divider=True)
    cmds.menuItem(parent=ppm, label="sel vertices member", c=Callback(selectInfluence, 2))
    cmds.menuItem(parent=ppm, label="sel vertices member on mesh", ann="select influenced vertices only on selected mesh", c=Callback(selectInfluence, 1))
    cmds.menuItem("cb0", parent=ppm, label="autoframe on sel", checkBox=True, c=Callback(autoFrame))
    cmds.menuItem(parent=ppm, label="", divider=True)
    cmds.menuItem(parent=ppm, label="add sel to deformer", ann="add selected component to deformer influence, only work for common deformers", c=Callback(addWeight))
    cmds.menuItem("cb9", parent=ppm, label="auto add sel to deformer", ann="automatically add components not under the influence of the deformer, only work for common deformers", checkBox=False)    
    cmds.menuItem(parent=ppm, label="", divider=True)
    cmds.menuItem(parent=ppm, label="open paint tool", ann="open the appropriate paint weight tool and select the deformer", c=Callback(openTool).repeatable())
    cmds.menuItem(parent=ppm, label="soft sel weight", ann="transforms softSelection values into weight, does not work for skinCluster", c=Callback(softWeight).repeatable())
    cmds.menuItem(parent=ppm, label="", divider=True)
    sm = cmds.menuItem(parent=ppm, label="show", subMenu=True, docTag=True)
    cmds.menuItem(parent=sm, label="All", c=Callback(showAll))    
    cmds.menuItem(parent=sm, label="None", c=Callback(showNone))   
    cmds.menuItem("cb_skinCluster", parent=sm, label="skinCluster", checkBox=True, c=Callback(setObject, 1))
    cmds.menuItem("cb_blendShape", parent=sm, label="blendShape", checkBox=True, c=Callback(setObject, 1))
    cmds.menuItem(parent=sm, label="common deformers", divider=True)
    cmds.menuItem("cb_cluster", parent=sm, label="cluster", checkBox=True, c=Callback(setObject, 1))
    cmds.menuItem("cb_lattice", parent=sm, label="lattice", checkBox=True, c=Callback(setObject, 1))
    cmds.menuItem("cb_nonLinear", parent=sm, label="nonLinear", checkBox=True, c=Callback(setObject, 1))
    cmds.menuItem("cb_wire", parent=sm, label="wire", checkBox=True, c=Callback(setObject, 1))
    cmds.menuItem("cb_jiggle", parent=sm, label="jiggle", checkBox=True, c=Callback(setObject, 1))
    cmds.menuItem("cb_shrinkWrap", parent=sm, label="shrinkWrap", checkBox=True, c=Callback(setObject, 1))
    cmds.menuItem("cb_deltaMush", parent=sm, label="deltaMush", checkBox=True, c=Callback(setObject, 1))
    cmds.menuItem("cb_tension", parent=sm, label="tension", checkBox=True, c=Callback(setObject, 1))
    cmds.menuItem("cb_proximityWrap", parent=sm, label="proximityWrap", checkBox=True, c=Callback(setObject, 1))
    cmds.menuItem("cb_textureDeformer", parent=sm, label="textureDeformer", checkBox=True, c=Callback(setObject, 1))

    ppm2 = cmds.popupMenu(parent="b1", button=3)
    cmds.menuItem(parent=ppm2, label="hotkeys", subMenu=True, itl=True, divider=True)
    cmds.menuItem("mi1", parent=ppm2, label=annSettingsButton("copy"), itl=True, en=False)
    cmds.menuItem("mi2", parent=ppm2, label=annSettingsButton("paste"), itl=True, en=False)
    cmds.menuItem("mi3", parent=ppm2, label=annSettingsButton("set"), itl=True, en=False)
    cmds.menuItem("mi4", parent=ppm2, label=annSettingsButton("smooth"), itl=True, en=False)

def initialize():
    #set mesh at start
    if cmds.ls(sl=True):
        setObject(0)

mainWindow()
initialize()

def onMayaDroppedPythonFile(args) :
    print(args)