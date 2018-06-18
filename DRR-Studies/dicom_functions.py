#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May 30 11:45:31 2018

@author: Payam
"""


import itk
import os
import sys
from read_image import get_itk_image_type
import numpy as np
import scipy as sp
import scipy.stats
#%%

def dicom_reader(input_dicom_directory,verbose):
    #%%
    # Check that the input exists
    if not os.path.isdir(input_dicom_directory):
        os.sys.exit('Input \"{}\" is not a directory. Exiting...'.format(input_dicom_directory))
    
    
    # Create the reader
    print('Gathering dicom names from {}'.format(input_dicom_directory))
    names_generator = itk.GDCMSeriesFileNames.New()
    names_generator.SetInputDirectory(str(input_dicom_directory))
    names_generator.SetGlobalWarningDisplay(False)
    names_generator.SetUseSeriesDetails(True)
    input_file_names = names_generator.GetInputFileNames()
    
    # Print info
    print('  Found {} files'.format(len(input_file_names)))
    if verbose:
        for idx, file_name in enumerate(input_file_names):
            print('  File {: >8}: {}'.format(idx, file_name))
    
    # Determine pixel type and read in stack
    print('Reading DICOM files into a stack')
    # image_type = get_itk_image_type(input_file_names[0]) # it seems that the dicom reader doesn't work with the double data type. perhaps due to the large data size. Float, and short seemed to lead to the same resutls so short was selected.
    image_type = itk.Image[itk.F,3]
    #%%
    ReaderType = itk.ImageSeriesReader[image_type]
    reader = ReaderType.New()
    dicomIO = itk.GDCMImageIO.New()
    reader.SetImageIO(dicomIO)
    reader.SetFileNames(input_file_names)
    
    try:
        print("in progress ... May take few seconds")
        reader.Update()
        print("Image Read Successfully")
    except ValueError: 
        print("ERROR: ExceptionObject cauth! \n")
        print(ValueError)
        sys.exit()
    if verbose:
        print("Read image information are as follows:\n")
        print(reader.GetOutput())
    itk.imwrite(reader.GetOutput(),'/Volumes/Storage/Payam/Desktop/bob.nii')
#%%
    return reader
#%%
def dicom_writer(image,output_file_name,force):
    # Check if the output exists, prompt to overwrite
    if not force:
        if os.path.exists(output_file_name):
            answer = input('Output file \"{outputImage}\" exists. Overwrite? [Y/n] '.format(outputImage=output_file_name))
            if str(answer).lower() not in set(['yes','y', 'ye', '']):
                os.sys.exit('Will not overwrite \"{inputFile}\". Exiting...'.
                format(inputFile=output_file_name))

    
    print('Writing to {}'.format(output_file_name))
    itk.imwrite(image, str(output_file_name))
    print('Writing of the image is finished')
    

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0*np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    return m, m-h, m+h
