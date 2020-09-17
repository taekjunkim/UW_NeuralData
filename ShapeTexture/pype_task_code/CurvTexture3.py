# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 21:23:54 2015

CurvTexture.py is a Fixation task for V4 recording with Curvature & Texture stimuli
It interacts with fixationTask.py 
It creates visual stimuli from bmp files

@author: taekjunkim
"""

import os, sys, types   ## os is needed to specify file location
import scipy.io as spio   ## scipy is needed to load mat file
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
    app.taskObject = CurvTexture(app)
    app.globals = Holder()
    app.idlefb()
    app.startfn = RunSet

# This is also something that all tasks have, and it's a python thing.
# Don't touch it.

if not __name__ == '__main__':
        loadwarn(__name__)
else:
        dump(sys.argv[1])


class CurvTexture(fixationTask):
    
    def __init__(self, app):
        self.createParamTable(app)
        self.app = app
        self.mySprites = list()
        self.mySpriteList = list()
        self.spriteColors = list()
        self.myid = list()
        self.numStim = 0
        

    def createStimuli(self,app):

        ## global parameters
        gParam = app.getcommon()

        ## parameters defined in this task
        self.params = self.myTaskParams.check()
        params = self.params

        myFB = app.fb	#framebuffer
        myX = params['RF_Center_X']
        myY = params['RF_Center_Y']

        RF_ecc = ((myX**2)+(myY**2))**0.5
        # import pdb; pdb.set_trace()
        myShapeScale = int(gParam['mon_ppd']+params['RFscalefactor']*RF_ecc)   ## RF size   
        myScale = int(myShapeScale*1.8)                
        ##if myShapeScale<128:
        ##   myScale = 256
        myShapeScale = myShapeScale*params['SampleSizeFract']  ## within .9 of RF size
        ### myScale = params['Stim_Size']        

        randomize_stims = params['randomize_stimuli']
        myBG = params['bg_during']

        idNow = 0        

        ## Shape stimuli from b8stimfactory
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
        ShapeToBeUsed = [1,2,3,4,5,8,9,10,11,13,14,17,18,19,20,22,23,25,26,
                         28,29,31,32,35,37,38,39,42,47,48]
        
        
        fg_color = params['fg_color']
        myFactory = b8StimFactory(myShapeScale*2.0,myShapeScale/2.0)
        for j in range(0,len(fg_Stims)):
            if j in ShapeToBeUsed:
               if j == 1:
                   for r in range(0,3):   ### dark, medium, bright
                       rotation = 0
                       s = myFactory.getB8Stim(
                               fg_Stims[j],self.sampling,myFB,(30+70*r,30+70*r,30+70*r),rotation,
                               myX,myY,myBG,sp_h_offset=0,sp_v_offset=0, sp_scaling=1,depth=1)  
                       #import pdb; pdb.set_trace()    
                       #s.scale(myShapeScale, myShapeScale)    #Scales to size in pixels    
                       self.mySprites.append(s)
                       idNow = idNow + 1
                       self.myid.append(idNow)   #1~370: b8stim in full orientation  
                       print idNow
               else:
                   for r in range(0,45*rotNum[j],45):
                       rotation = r
                       s = myFactory.getB8Stim(
                               fg_Stims[j],self.sampling,myFB,fg_color,rotation,
                               myX,myY,myBG,sp_h_offset=0,sp_v_offset=0, sp_scaling=1,depth=1)  
                       #import pdb; pdb.set_trace()    
                       #s.scale(myShapeScale, myShapeScale)    #Scales to size in pixels    
                       self.mySprites.append(s)
                       idNow = idNow + 1
                       self.myid.append(idNow)   #1~370: b8stim in full orientation  
                       print idNow
        
        ## Make circle aperture
        ShapeID = 2
        rotation = 0
        Ap = myFactory.getB8Stim(
                                 ShapeID,self.sampling,myFB,(255,255,255),rotation,
                                 myX,myY,(0,0,0),sp_h_offset=0,sp_v_offset=0, sp_scaling=1,depth=1)   

        """
        ## Circular mask for FFT low-pass filtering
        LowPassFilter = np.zeros((myScale,myScale))
        centerXY = myScale/2.0
        CutOffRadius = 3.0*myScale/37 ### 3 cycles/deg low-pass
        for i in range(1,myScale):
            for j in range(1,myScale):
                radius = (i-centerXY)**2 + (j-centerXY)**2
                radius = math.sqrt(radius)
                if radius < CutOffRadius:
                   #LowPassFilter[i,j] = 1 
                   LowPassFilter[i,j] = 1/(1 + (radius/CutOffRadius)**(2*3)) ### 3rd order ButterWorth Filter
        """
        
        ## Make grating stimuli
        CycPerDeg = [4,0.5]
        tiltInRadians = 0
        for j in range(0,len(CycPerDeg)):
            s = Sprite(myScale, myScale, myX, myY, fb=myFB, depth=1, on=0,centerorigin=1)
            s.alpha_gradient(myScale/2-5, myScale/2, x=0, y=0)		                 
               
            PixPerCyc = 37.0/CycPerDeg[j]   ### 37: PixPerDeg
            radiansPerPixel = (1/PixPerCyc) * 2*math.pi
            widthArray = np.linspace(-myScale/2,myScale/2,myScale)
            [xx, yy] = np.meshgrid(widthArray,widthArray)
            a = np.cos(tiltInRadians)*radiansPerPixel
            b = np.sin(tiltInRadians)*radiansPerPixel

            gratingMtx = np.sin(a*xx+b*yy)*100+100 ### mean luminance is matched to 100 as in Texture, 03/16/16
            gratingMtx = np.abs(gratingMtx)+1.0
            gratingMtx[gratingMtx>255] = 255            

            imageNow = np.zeros((myScale,myScale,3))
            imageNow[:,:,0] = gratingMtx
            imageNow[:,:,1] = gratingMtx
            imageNow[:,:,2] = gratingMtx                        

            ### ArrayMatrix [Ypos,Xpos,Z]. surface array [Xpos,Ypos,Z]
            ### Transpose is needed
            imageNow = np.transpose(imageNow,(1,0,2))
            imageNow = imageNow.tolist()
            s.array[:] = imageNow
            
            for o in range(0,4):
                ss = s.clone()
                ss.rotate(45*o,preserve_size=1, trim=0)
                #import pdb; pdb.set_trace()    
                self.mySprites.append(ss)
                idNow = idNow + 1
                self.myid.append(idNow)   #371 & later: texture stimuli
                print idNow

            ### Smaller circle aperture, then rotation
            ### Apply different aperture
            for o in range(0,4):
                sNow = s.clone()	
                sNow.rotate(45*o,preserve_size=1, trim=0)
                if myScale>len(Ap.array):
                   pStart = int(math.floor(myScale/2-len(Ap.array)/2))
                   sNow.alpha[:,:] = 0                      
                   sNow.alpha[pStart:pStart+len(Ap.array),pStart:pStart+len(Ap.array)] = Ap.array[:,:,0]
                elif myScale<len(Ap.array):
                   pStart = int(math.floor(len(Ap.array)/2-myScale/2))						
                   sNow.alpha[:,:] = Ap.array[pStart:pStart+myScale,pStart:pStart+myScale,0]  
                elif myScale == len(Ap.array):
                   sNow.alpha[:,:] = Ap.array[:,:,0]  						                                         
                self.mySprites.append(sNow)
                idNow = idNow + 1
                self.myid.append(idNow)   #371 & later: texture stimuli
                print idNow

		        
        gratingMtx = None;   widthArray = None;   imageNow = None

        
        ## Texture stimuli from bmp files
        myFileStart = params['Texture_start']
        myFileEnd = params['Texture_end']

        MatFileBase = '/home/shapelab/.pyperc/Tasks/Taekjun'
        #MatFileName = os.path.join('Taekjun', 'TextureStim.mat')
        MatFileName = os.path.join(MatFileBase, 'RawTexture3.mat')
        ### Textures in RawTexture.mat: mean luminance is matched to 100(0~255 range), 3/16/16
        
        sData = spio.loadmat(MatFileName)
        
        ### In RawTexture.mat
        ### stim1, stim2 are gratings with 4c/deg & 1c/deg
        ### stim3~21 are texture stimuli
        ### Therefore, myFileStart = 3, myFileEnd = 21
        for j in range(myFileStart, myFileEnd+1):
            #s = Sprite(1, 1, myX, myY, fb=myFB, depth=1, on=0,centerorigin=1,fname = str(j) + '.bmp')            
            s = Sprite(256, 256, myX, myY, fb=myFB, depth=1, on=0,centerorigin=1)
            # ArrayNow = s.array   # pygame.surfarray.pixels3d(self.im)
            # print ArrayNow.shape
            # s.alpha[150:300,:] = 120   #transparency            

            imageNow = np.zeros((256,256,3))
            #imageNow[0:256,0:256,0] = sData['TextureStim'][0][j-1]['StimMtx']
            #imageNow[0:256,0:256,1] = sData['TextureStim'][0][j-1]['StimMtx']
            #imageNow[0:256,0:256,2] = sData['TextureStim'][0][j-1]['StimMtx']
            imageNow[0:256,0:256,0] = sData['RawTexture'][0][j-1]['StimMtx']
            imageNow[0:256,0:256,1] = sData['RawTexture'][0][j-1]['StimMtx']
            imageNow[0:256,0:256,2] = sData['RawTexture'][0][j-1]['StimMtx']
            
            imageNow = np.abs(imageNow) + 1.0
            imageNow[imageNow>255] = 255
            
            ### ArrayMatrix [Ypos,Xpos,Z]. surface array [Xpos,Ypos,Z]
            ### Transpose is needed
            imageNow = np.transpose(imageNow,(1,0,2))            
            imageNow = imageNow.tolist()   ### numpy.ndarray --> list 
            s.array[:] = imageNow

            s.scale(myScale, myScale)    #Scales to size in pixels		      
            s.alpha_gradient(myScale/2-5, myScale/2, x=0, y=0)

            ### No filter, then rotation
            if j>2:
               for o in range(0,4):
                   ss = s.clone()
                   ss.rotate(45*o,preserve_size=1, trim=0)
                   self.mySprites.append(ss)
                   idNow = idNow + 1
                   self.myid.append(idNow)   #371 & later: texture stimuli
                   print idNow

            ### Smaller circle aperture, then rotation
            ### Apply different aperture
            if j>2:
               for o in range(0,4):
                   sNow = s.clone()	
                   sNow.rotate(45*o,preserve_size=1, trim=0)
                   if myScale>len(Ap.array):
                      pStart = int(math.floor(myScale/2-len(Ap.array)/2))
                      sNow.alpha[:,:] = 0                      
                      sNow.alpha[pStart:pStart+len(Ap.array),pStart:pStart+len(Ap.array)] = Ap.array[:,:,0]
                   elif myScale<len(Ap.array):
                      pStart = int(math.floor(len(Ap.array)/2-myScale/2))						
                      sNow.alpha[:,:] = Ap.array[pStart:pStart+myScale,pStart:pStart+myScale,0]  
                   elif myScale == len(Ap.array):
                      sNow.alpha[:,:] = Ap.array[:,:,0]  						                                         
                   self.mySprites.append(sNow)
                   idNow = idNow + 1
                   self.myid.append(idNow)   #371 & later: texture stimuli
                   print idNow


            """
            ### Low-pass filter, then rotation
            if j>2:   # if stim is not a grating
               imageNow = np.array(s.array) ### imageNow derived from surface, so do not transpose here
               f = np.fft.fft2(imageNow[:,:,0])
               fshift = np.fft.fftshift(f)
               fshift = fshift*LowPassFilter
               f_ishift = np.fft.ifftshift(fshift)
               imageBack = np.fft.ifft2(f_ishift)
               imageBack = np.abs(imageBack) + 1.0
               imageBack[imageBack>255] = 255
               #import pdb; pdb.set_trace() 
               imageNow[:,:,0] = imageBack
               imageNow[:,:,1] = imageBack
               imageNow[:,:,2] = imageBack
               imageNow = imageNow.tolist()   ### numpy.ndarray --> list 			    
               s.array[:] = imageNow
               for o in range(0,4):
                   ss = s.clone()
                   ss.rotate(45*o,preserve_size=1, trim=0)
                   self.mySprites.append(ss)
                   idNow = idNow + 1
                   self.myid.append(idNow)   #371 & later: texture stimuli
                   print idNow
            """        
        
        
        f = None;   fshift = None;   f_ishift = None;
        imageNow = None;   imageBack = None;
        sData = None;
                        
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
        #import pdb; pdb.set_trace()    

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
            ("Texture_start", 3, is_int, "select texture file number start"),
            ("Texture_end", 21, is_int, "select texture file number end"),
            ("nRepsPerStim", "5", is_int, "Number of repetitions of each stimulus to present"),
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
