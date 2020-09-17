#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 13:43:41 2019

this is the stimulus creation program for the b8 stimuli
51 stimuli in all. These were presented at 1, 2, 4 or 8 rotations
based on rotational symmetry
to create the stimuli, in addition to this program you need:
vertices1.txt

When prompted for the stimulus number, type a number between 1 and 51.

@author: taekjunkim
"""

#%%
import numpy as np;
import matplotlib.pyplot as plt;

#%%
def fvmax(invec):
    sample = 50.0;
    num = np.shape(invec)[0];
    inshft = np.vstack((invec[num-2,:],invec,invec[1,:]));
    ip = np.arange(0,50,1)/50;
    
    vtx = np.empty((1,num*50-49));
    vty = np.empty((1,num*50-49));
    dvtx = np.empty((1,num*50-49));
    dvty = np.empty((1,num*50-49));
    
    for i in range(0,num-1):
        bufvrt = inshft[i:i+4,:];
    
        incr = np.empty((4,len(ip)));
        incr[0,:] = -ip*ip*ip+3*ip*ip-3*ip+1;
        incr[1,:] = 3*ip*ip*ip-6*ip*ip+4;
        incr[2,:] = -3*ip*ip*ip+3*ip*ip+3*ip+1;
        incr[3,:] = ip*ip*ip;        
        
        dincr = np.empty((4,len(ip)));
        dincr[0,:] = -3*ip*ip+6*ip-3;
        dincr[1,:] = 9*ip*ip-12*ip;
        dincr[2,:] = -9*ip*ip+6*ip+3;
        dincr[3,:] = 3*ip*ip;        
        
        vtx[0,i*50:(i+1)*50] = np.sum(np.tile(bufvrt[:,0].reshape(4,1),(1,50))*incr,axis=0)/6.0;
        vty[0,i*50:(i+1)*50] = np.sum(np.tile(bufvrt[:,1].reshape(4,1),(1,50))*incr,axis=0)/6.0;        

        dvtx[0,i*50:(i+1)*50] = np.sum(np.tile(bufvrt[:,0].reshape(4,1),(1,50))*dincr,axis=0)/6.0;
        dvty[0,i*50:(i+1)*50] = np.sum(np.tile(bufvrt[:,1].reshape(4,1),(1,50))*dincr,axis=0)/6.0;        

    vtx[0,(num-1)*50] = vtx[0,0];
    vty[0,(num-1)*50] = vty[0,0];    

    dvtx[0,(num-1)*50] = dvtx[0,0];
    dvty[0,(num-1)*50] = dvty[0,0];    
    
    outvec = np.transpose(np.vstack((vtx, vty)));
    return outvec;


#%%
f = open('vertices1.txt','r');
nums_inTxt = [];
for line in f:
    nums_inTxt += line.split();
f.close()

nums_inTxt = np.float_(nums_inTxt);

shapeNum = input('Enter Stimulus number (1:51): ');
shapeNum = int(shapeNum);

idx = 0;
for i in range(51):   
    vrtnum = int(nums_inTxt[idx]);
    print(vrtnum);
    
    invec = np.empty((vrtnum,2));
    for j in range(vrtnum):
        invec[j,0] = nums_inTxt[idx+j*2+1];
        invec[j,1] = nums_inTxt[idx+j*2+2]; 
    idx += vrtnum*2 + 1;
    
    if i+1==shapeNum:
        bufvert = fvmax(invec);
        plt.figure(figsize=[10, 5]); 
        for r in range(8):
            rot = r*45*np.pi/180;
            plt.subplot(2,4,r+1);  
            plt.axis('off');
            plt.fill([-2.0, 2.0, 2.0, -2.0],[-2.0, -2.0, 2.0, 2.0],'k');
            
            figX = np.cos(rot)*bufvert[:,0]+np.sin(rot)*bufvert[:,1];
            figY = -np.sin(rot)*bufvert[:,0]+np.cos(rot)*bufvert[:,1];            
            plt.fill(figX,figY,'w');
    

