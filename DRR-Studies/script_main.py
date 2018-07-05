#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  7 13:55:00 2018

@author: Payam
"""
#%% import libraries
import itk
import numpy as np
from read_image import get_itk_image_type
import main_functions 
import os

from StereoFlouroscopyRegistration.io.read_image import get_itk_image_type

input_filename = '/Users/pzandiyeh/Documents/Storage/Projects/Registration/QuickData/knee_ct_volume_identity.nii'
output_filename = ['knee_test_cam1.nii', # output file name 1 
                   'knee_test_cam2.nii'] # output file name 2

verbose = False          # verbose details of all steps. 

#% -------------------- Reader -------------------------
InputImageType = get_itk_image_type(input_filename)
OutputImageType= InputImageType


inputImage = itk.imread(input_filename)

#%% Set input information
sizeOutput = [1024,1400,1] # The size of output image
threshold  = 0. 

rot = [0., 0., 0.]     # rotation in degrees in x, y, and z direction. 
t   = [0. ,0. ,0.]     # translation in x, y, and z directions. 
cor = [0. ,0. ,0.]     #  offset of the rotation from the center of image (3D)

spaceOutput = [0.167,0.167,1]

delta = sizeOutput[0]*spaceOutput[0]/2

focalPoint   = [0.0,0.0,1000.0]
originOutput = [delta,delta,-200.0]
directionOutput = np.matrix([[  1.,  0.,  0.],
                             [  0.,  1.,  0.],
                             [  0.,  0.,  1.]])
#%%

for counter_x in range(0,5,5): # Rotation in x
    for counter_y in range(0,5,5): # Rotation in y
        for counter_z in range(0,5,5): # Rotation in z
            rot = [float(counter_x),float(counter_y),float(counter_z)] # Making the rotation into an array
            print(rot)
            output_directory = "/Users/pzandiyeh/Desktop/OutputImages" # output directory
            if not os.path.exists(output_directory): # If the directory is not existing , create one. 
                os.mkdir(output_directory) # Make the directory
            filetype = '.nii' # type of output image ... it can be nifti or dicom
            filename = 'rx_'+str(int(rot[0])) + 'ry_'+str(int(rot[1])) + 'rz_'+str(int(rot[2]))+filetype # makes the complete path
            output_filename = os.path.join(output_directory,filename) # creating the output directory where all the images are stored.
            main_functions.drr(inputImage,output_filename,rot,t,focalPoint,originOutput,sizeOutput,cor,spaceOutput,directionOutput,threshold,InputImageType,OutputImageType,verbose) # creating drr. 
            
            
#%% For later. 
    #import itk_helpers as Functions 
##%%
## Transferring the 3D image so that the center of rotation of the image is located at global origin. 
#
#Functions.rigid_body_transform3D(input_filename='/Volumes/Storage/Projects/Registration/QuickData/OA-BEADS-CT.nii',\
#                                  output_filename='/Volumes/Storage/Projects/Registration/QuickData/transformed_ct.nii',\
#                                    t =[-1.14648438, 132.85351562, 502.09999385],rot = [-90.,0.,90.])


