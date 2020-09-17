# -*- coding: utf-8 -*-
"""
Created on Mon Apr 30 2018

ShapeAgainstTexture.py is a Fixation task for V4 recording with Shape in Texture stimuli
It interacts with fixationTask.py 
5 textures in Texture_SaT.mat
1 shape with 8 rotations

Stimulus set is 96 conditions
%%% Shape alone (1-8)
%%% 2xRF texture alone (9-13)
%%% Full texture alone (14-18)
%%% Shape1 + 2xRF texture (1: 19-23)
%%% Shape2 + 2xRF texture (2: 24-28)
%%% Shape3 + 2xRF texture (3: 29-33)
%%% Shape4 + 2xRF texture (4: 34-38)
%%% Shape5 + 2xRF texture (5: 39-43)
%%% Shape6 + 2xRF texture (6: 44-48)
%%% Shape7 + 2xRF texture (7: 49-53)
%%% Shape8 + 2xRF texture (8: 54-58)
%%% Shape1 + Full texture (1: 59-63)
%%% Shape2 + Full texture (2: 64-68)
%%% Shape3 + Full texture (3: 69-73)
%%% Shape4 + Full texture (4: 74-78)
%%% Shape5 + Full texture (5: 79-83)
%%% Shape6 + Full texture (6: 84-88)
%%% Shape7 + Full texture (7: 89-93)
%%% Shape8 + Full texture (8: 94-98)
%%% No stim (99)

@author: taekjunkim
"""

import os, sys, types   ## os is needed to specify file location
import scipy.io as spio   ## scipy is needed to load mat file
import h5py   ## to load mat file later than -v7.3
from pype import *
from Numeric import *   ## Numeric is needed for array computation. Possible to upgrade?
import numpy as np
import math
from random import *
from shapes import *   ## because of create bar for blank stimuli
from colors import *
from fixationTask import fixationTask
from b8StimFactory import *


def RunSet(app):
    app.taskObject.runSet(app)

def cleanup(app):
    app.taskObject.cleanup(app)

def main(app):
    app.taskObject = ShapeAgainstTexture(app)
    app.globals = Holder()
    app.idlefb()
    app.startfn = RunSet

# This is also something that all tasks have, and it's a python thing.
# Don't touch it.

if not __name__ == '__main__':
        loadwarn(__name__)
else:
        dump(sys.argv[1])


class ShapeAgainstTexture(fixationTask):
    
    def __init__(self, app):
        self.createParamTable(app)
        self.app = app
        self.mySprites = list()
        self.mySpriteList = list()
        self.spriteColors = list()
        self.myid = list()
        self.numStim = 0
        

    def createStimuli(self,app):

        ### global parameters
        gParam = app.getcommon()

        ### parameters defined in this task
        self.params = self.myTaskParams.check()
        params = self.params

        myFB = app.fb	#framebuffer
        myX = params['RF_Center_X']
        myY = params['RF_Center_Y']

        RF_ecc = ((myX**2)+(myY**2))**0.5
        RF_Scale = int(gParam['mon_ppd']+params['RFscalefactor']*RF_ecc)   ## RF size
        myScale = RF_Scale*params['SampleSizeFract']  ## within .9 of RF size        
        RF_Scale2 = 2*RF_Scale   ## 2xRF size
        FF_Scale = [1600,1200]

        randomize_stims = params['randomize_stimuli']
        myBG = params['bg_during']

        ### Shape stimuli from b8stimfactory
        self.sampling = 100
        self.numB8Shapes = 51
        self.B8ShapeSet = arange(1,self.numB8Shapes+1)
        fg_Stims = self.B8ShapeSet
        rotNum = list()
        for j in range(len(fg_Stims)):   ### number of rotation
            if j in [0,1]:   # stim 1,2
               rotNum.append(1)
            elif j in [31,36]: # stim 32,27
               rotNum.append(2)
            elif j in [4,6,33,44]: # stim 5,7,34,45
               rotNum.append(4)
            else:
               rotNum.append(8)   

        ### These numbers are "stim IDs minus 1"
        ShapeToBeUsed = [15]   ### 15 = 16(ShapeID) - 1                 
        
        ### Making Shape sprite        
        fg_color = params['fg_color']
        myFactory = b8StimFactory(myScale*2.0,myScale/2.0)
        ShapeNum = 0
        sShape = [None]*8
        for j in range(0,len(fg_Stims)):
            if j in ShapeToBeUsed:
               for r in range(0,45*rotNum[j],45):
                   rotation = r
                   sShape[ShapeNum] = myFactory.getB8Stim(
                                                      fg_Stims[j],self.sampling,
                                                      myFB,fg_color,rotation,
                                                      myX,myY,myBG,sp_h_offset=0,
                                                      sp_v_offset=0, sp_scaling=1,depth=1)  
                   ShapeNum = ShapeNum+1

        ### Making Circle Aperture (2xRF)   
        widthArray = np.linspace(-RF_Scale,RF_Scale,RF_Scale2)
        [xx, yy] = np.meshgrid(widthArray,widthArray)
        Radius = (xx**2 + yy**2)**0.5
        InRadius = RF_Scale-5
        OutRadius = RF_Scale+5
        CircleMtx = 1-((Radius-InRadius)/(OutRadius-InRadius))
        CircleMtx[Radius<=InRadius] = 1
        CircleMtx[Radius>OutRadius] = 0
        CircleMtx = CircleMtx*255

        ### Making Texture sprite from Texture_SaT.mat file
        MatFileBase = '/home/shapelab/.pyperc/Tasks/Taekjun'
        MatFileName = os.path.join(MatFileBase, 'Texture_SaT.mat')
        #sData = spio.loadmat(MatFileName)
        sData = h5py.File(MatFileName)
        
        TextureNum = 0      
        sTextureF = [None]*5                               
        for j in range(0,5):
            sTextureF[TextureNum] = Sprite(800, 600, 0, 0, fb=myFB, depth=1, on=0, centerorigin=1)
            imageNow = np.zeros((800,600,3))
            ref = sData.get('/Texture_SaT/ReconImg').value[j][0]
            imageNow[0:800,0:600,0] = sData[ref].value
            imageNow[0:800,0:600,1] = sData[ref].value
            imageNow[0:800,0:600,2] = sData[ref].value
            
            ### ArrayMatrix [Ypos,Xpos,Z]. surface array [Xpos,Ypos,Z]
            ### Transpose is needed
            ### imageNow = np.transpose(imageNow,(1,0,2))            
            imageNow = imageNow.tolist()   ### numpy.ndarray --> list 
            sTextureF[TextureNum].array[:] = imageNow

            sTextureF[TextureNum].scale(FF_Scale[0], FF_Scale[1])    #Scales to size in pixels		      
            TextureNum = TextureNum + 1

        idNow = 0
        ### Shape alone
        for j in range(0,ShapeNum):
            self.mySprites.append(sShape[j])
            idNow = idNow + 1
            self.myid.append(idNow)   
			
        ### 2xRF Texture alone
        sTextureS = [None]*5                                       
        for j in range(0,5):
            sTextureS[j] = Sprite(RF_Scale2, RF_Scale2, myX, myY, fb=myFB, depth=1, on=0, centerorigin=1)
            sTextureS[j].alpha = CircleMtx            
            sTextureS[j].array[0:RF_Scale2,0:RF_Scale2,:] \
            = sTextureF[j].array[FF_Scale[0]/2+myX-RF_Scale:FF_Scale[0]/2+myX+RF_Scale,
                                 FF_Scale[1]/2-myY-RF_Scale:FF_Scale[1]/2-myY+RF_Scale,:]
            StimNow = sTextureS[j].clone()
            self.mySprites.append(StimNow)
            idNow = idNow + 1
            self.myid.append(idNow)   
        
        ### Full Texture alone
        for j in range(0,len(sTextureF)):
            self.mySprites.append(sTextureF[j])
            idNow = idNow + 1
            self.myid.append(idNow)   

        
        ### Shape + Texture
        for j in range(0,len(sShape)):
            ShapeNow = np.array(sShape[j].array)
            #import pdb; pdb.set_trace()   
            index_pos = np.where(ShapeNow[:,:,0]==fg_color[0])                          
			
            for k in range(0,5):
				### 2xRF Texture
                #import pdb; pdb.set_trace()      				                                                    
                TextureNow = sTextureS[k].clone()
                pStart = int(RF_Scale-(len(ShapeNow)/2))
                TextureNow.array[pStart+index_pos[0],pStart+index_pos[1],0:3] = [fg_color[0],fg_color[1],fg_color[2]]
                self.mySprites.append(TextureNow)
                idNow = idNow + 1
                self.myid.append(idNow)   #1~370: b8stim in full orientation  
				
				### Full Texture
                TextureNow = sTextureF[k].clone()
                pStartX = FF_Scale[0]/2 + myX - int(len(ShapeNow)/2)
                pStartY = FF_Scale[1]/2 - myY - int(len(ShapeNow)/2)
                TextureNow.array[pStartX+index_pos[0],pStartY+index_pos[1],0:3] = [fg_color[0],fg_color[1],fg_color[2]]
                self.mySprites.append(TextureNow)
                idNow = idNow + 1
                self.myid.append(idNow)   #1~370: b8stim in full orientation  
        
        ShapeNow = None;   
        TextureNow = None;
        
        for j in range(0,params['nBlanks']):
            s = createBar(30, 30, myFB,myBG, 0, myX, myY, myBG)
            self.mySprites.append(s)
            idNow = idNow + 1
            self.myid.append(idNow)
            print idNow

        numUniqueStims = len(self.mySprites)
        stimNumbers = arange(0,numUniqueStims)
        for i in arange(0,params['nRepsPerStim']):
            if(randomize_stims):
                shuffle(stimNumbers)
            self.mySpriteList.extend(stimNumbers)
            self.numStim = self.numStim + len(self.mySprites)
        
                        
        ## these are the stim params that need to be encoded before start of task
        self.myFB = myFB
        self.myX = myX
        self.myY = myY
        self.myBG = myBG


    def createParamTable(self,app):            
        #create parameter table and window to go along with it
        P = app.getcommon()
        self.myTaskButton = app.taskbutton(text=__name__, check = 1)
        self.myTaskNotebook = DockWindow(title=__name__, checkbutton=self.myTaskButton)
        parfile = "%s.%s" % (app.taskname(), P['subject'])
        # Look for an existing saved parameter file for this task
        if parfile:
                parfile = parfile + '.par'

        # Initialization and default values for the parameters.  Each row is
        # one parameter.  The first value is the name of the parameter, the
        # second is its default value, the third defines the type of
        # the value (more on that later) and the fourth is optional and
        # is a descriptive label that pops up when you hold the mouse over
        # that entry in the table.  There are numerous standard parameter
        # types, the most common are self-explanatory.  is_color needs to be
        # 3 or 4 numbers in tuple format, e.g. (255,1,1) for red; the 4th
        # number is optional and is an alpha value (if left off, assumed
        # to be 255).  (0,0,0) is a special code for transparent or for
        # white noise fill pattern, depending on the task, so use (1,1,1)
        # for black.  is_any just gets passed as a string, this is what
        # to use if you need a list of numbers.  is_iparam can take a
        # variance value as either a percentage or an actual number of
        # units, so you'd have "1000+-10%" or "150+-50".  There are a ton of
        # others defined in ptable.py.  Values of None for default value and
        # type make that row into a heading of sorts that can be helpful for
        # organizing a large number of parameters.

        self.myTaskParams = ParamTable(self.myTaskNotebook, (        
            ("Stim Presentation Params", None, None), 
            ("nRepsPerStim", "20", is_int, "Number of repetitions of each stimulus to present"),
            ("nBlanks", "1", is_int, "The number of blank stimuli to present per block"),              
            ("randomize_stimuli", 1, is_boolean, "Whether or not to randomize stimuli within repetitions."),
            ("SampleSizeFract", ".9", is_float, "Fraction of RF that the size of the stimulus is suppose to be."),
            ("bg_before", "(10, 10, 10)", is_color, "The background color before stimulus presentation"),            
            ("bg_during", "(10, 10, 10)", is_color, "The background color during stimulus presentation"),
            ("fg_color", "(150, 150, 150)", is_color, "The foreground color during stimulus presentation"),
            ("bg_lum", "8", is_int, "Luminance of background (4,8,12 or 18)"),            
            ("RF_Params",None,None),
            ("RF_Center_X", "0",is_int,"X coordinate of the receptive field center in pixels"),
            ("RF_Center_Y", "0",is_int,"Y coordinate of the receptive field center in pixels"),
            ("Stim_Size", "256", is_int, "Size of the receptive field in pixels"),
            ("RFscalefactor", "0.625",is_float, "If scale by RF size, what's the scale factor?"),
            ("Task Params", None, None),
            ("iti", "2500", is_int, "Inter-trial interval"),
            ("IStime", "300", is_int, "Inter-stimulus interval"),
            ("stimon", "300", is_int, "Stimulus presentation"),
            ("nstim", "5", is_int, "Number of stimuli"),
            ("Reward Params", None, None),
            ("numdrops", "8", is_int, "Number of juice drops"),
            ("rmult", "1.0", is_float),
            ("Fixation Params", None, None, "Fixation Parameters"),
            ("fixcolor1", "(255,255,255)",is_color, 'Color of the fixation dot'),
            ("fixcolor2", "(128,128,128)",is_color),
            ("min_err", "0", is_int),
            ("max_err", "100", is_int),
            ("fixwait", "100", is_int),
            ("Record File Params", None, None, "Params for setting name of record file"),
            ("Use Special Name", "0", is_boolean, "If 1 then the record file name will be AnimalPrefixDate_TaskName_CellGroup_Iteration.rec"),
            ("RFDirectory", "/home/shapelab/recordFiles/", is_any, "Directory to use for Record Files"),               
            ("AnimalPrefix", "m", is_any, "Animal Prefix to use"),
            ("Date","080325", is_any, "Date to use "),
            ("TaskName","isolumcontrol", is_any, "TaskName"),
            ("CellGroup","01", is_int, "# of cell group encountered today"),
            ("Iteration","01", is_int, "# of times this task has been run on this cell group"),
            ("Misc Params", None, None, "Miscelaneous Parameters"),
            ("Recent Buffer Size", "50", is_int, "The number of trials to use to calculate recent performance"),
            ("pause_color", "(150,0,0)", is_color, "The screen will turn this color when the task is paused")
            ), file=parfile)

    def cleanup(self, app):
        #delete parameter table and anything else we created
        self.myTaskParams.save()
        self.myTaskButton.destroy()
        self.myTaskNotebook.destroy()
        del app.globals
        #self.myTaskParams.destroy()
#        if(len(self.mySprites) > 0):
#            for i in arange(1,len(self.mySprites)):
#                self.mySprites[i].__del__()

        
    def encodeISI(self,app,sIndex):
        sIDIndex = self.mySpriteList[sIndex]
        myid = self.myid[sIDIndex]
	
        app.encode_plex('stimid')
        app.encode_plex(int(myid+app.globals.plexStimIDOffset))

        app.encode('stimid')
        app.encode(int(myid+app.globals.plexStimIDOffset))
        

    def encodeTaskParameters(self,app):
        #encode task parameters
        params = self.myTaskParams.check()
        app.encode_plex('rfx')
        app.encode_plex(params['RF_Center_X']+ app.globals.yOffset)
        app.encode_plex('rfy')
        app.encode_plex(params['RF_Center_Y'] + app.globals.yOffset)
        app.encode_plex('stimWidth')                         
        app.encode_plex(params['Stim_Size'] + app.globals.yOffset)
        app.encode_plex('iti')
        app.encode_plex(int(params['iti']))
        app.encode_plex('stim_time')
        app.encode_plex(int(params['stimon']))
        app.encode_plex('isi')
        app.encode_plex(int(params['IStime']))
        app.encode_plex('numstim')
        app.encode_plex(int(params['nstim']))

        app.encode('rfx')
        app.encode(params['RF_Center_X']+ app.globals.yOffset)
        app.encode('rfy')
        app.encode(params['RF_Center_Y'] + app.globals.yOffset)
        app.encode('stimWidth')                         
        app.encode(params['Stim_Size'] + app.globals.yOffset)
        app.encode('iti')
        app.encode(int(params['iti']))
        app.encode('stim_time')
        app.encode(int(params['stimon']))
        app.encode('isi')
        app.encode(int(params['IStime']))
        app.encode('numstim')
        app.encode(int(params['nstim']))
     
    def encodeITI(self,app):
        pass

    def getSprite(self, index):
        return self.mySprites[self.mySpriteList[index]]

    def getNumStim(self):
        return self.numStim

    def getRecordFileName(self): #gets the record file for this task 
        params = self.myTaskParams.check()
        if(params['Use Special Name']):
            filename = "%s%s%s_%s_%02d_%02d.rec" % (params['RFDirectory'],params['AnimalPrefix'],params['Date'],params['TaskName'],params['CellGroup'],params['Iteration'])
        else:
            filename = None
        return filename
