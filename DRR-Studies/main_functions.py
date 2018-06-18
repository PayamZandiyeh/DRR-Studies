import sys
import itk
import itk_helpers as Functions
import numpy as np
import dicom_functions as dfun

def drr(inputImage,output_filename,rot,t,focalPoint,originOutput,sizeOutput,cor,spaceOutput,directionOutput,threshold,InputImageType,OutputImageType,verbose):
    #%% Transfomration 
    inOrigin     = inputImage.GetOrigin()                   # Get the origin of the image.
    inSpacing    = inputImage.GetSpacing()                  # Get the resolution of the input image.
    inSize       = inputImage.GetBufferedRegion().GetSize() # Get the size of the input image.
    inDirection  = inputImage.GetDirection()
    
    #%% ------------------ Transformation 
    # This part is inevitable since the interpolator (Ray-cast) and resample Image
    # image filter uses a Transformation -- Here we set it to identity. 
    TransformType = itk.CenteredEuler3DTransform[itk.D]
    transform     = TransformType.New()
    
    direction_mat = Functions.get_vnl_matrix(inDirection.GetVnlMatrix())
    
    rot_mod = np.dot(-1,rot)           # Due to Direction of transform mapping ( 8.3.1 in the ITK manual)
    t_mod   = np.dot(-1,t  )           # Due to Direction of transform mapping ( 8.3.1 in the ITK manual)
    # Since this transform is for the movement of x-ray source and not the rigid body, therefore, no need to invert the rotation. 
    #
    #
    rot_mod = direction_mat.dot(np.transpose(rot_mod))           
    t_mod   = direction_mat.dot(np.transpose(t_mod  ))          
    
    
    transform.SetRotation(np.deg2rad(rot_mod[0]),np.deg2rad(rot_mod[1]),np.deg2rad(rot_mod[2])) # Setting the rotation of the transform
    transform.SetTranslation(itk.Vector.D3(t_mod))    # Setting the translation of the transform
    transform.SetComputeZYX(True)  # The order of rotation will be ZYX. 
    
    center = direction_mat.dot(inOrigin)+ np.multiply(inSpacing,inSize)/2. # Setting the center of rotation as center of 3D object + offset determined by cor. 
    center = direction_mat.dot(center)-t # Convert the image to the local coordinate system. 
    transform.SetCenter(center)                     # Setting the center of rotation. 
    
    if verbose:
        print(transform)
    
    #%% Raycast interpolator
    ScalarType = itk.D
    InterpolatorType = itk.RayCastInterpolateImageFunction[InputImageType,ScalarType]       # Defining the interpolator type from the template. 
    interpolator     = InterpolatorType.New()               # Pointer to the interpolator
    
    interpolator.SetInputImage(inputImage)                  # Setting the input image data
    interpolator.SetThreshold(threshold)                    # Setting the output threshold
    interpolator.SetFocalPoint(itk.Point.D3(focalPoint))    # Setting the focal point (x-ray source location)
    interpolator.SetTransform(transform)                    # Setting the transform -- 
    
    if verbose:
        print(interpolator)
    #%% filtering
    #%----------------- Resample Image Filter ------------------------
        # In this part the resample image filter to map a 3D image to 2D image plane with desired specs is designed
        
    FilterType = itk.ResampleImageFilter[InputImageType,OutputImageType]                    # Defining the resample image filter type. 
    resamplefilter = FilterType.New()               # Pointer to the filter
    
    resamplefilter.SetInput(inputImage)             # Setting the input image data 
    resamplefilter.SetDefaultPixelValue( 0 )      # Setting the default Pixel value
    resamplefilter.SetInterpolator(interpolator)    # Setting the interpolator
    resamplefilter.SetTransform(transform)          # Setting the transform
    resamplefilter.SetSize(sizeOutput)              # Setting the size of the output image. 
    resamplefilter.SetOutputSpacing(spaceOutput)    # Setting the spacing(resolution) of the output image. 
    resamplefilter.SetOutputOrigin(originOutput)    # Setting the output origin of the image
    Functions.change_image_direction(oldDirection=resamplefilter.GetOutputDirection(),newDirection=directionOutput,DimensionOut=3)     # Setting the output direction of the image  --- resamplefilter.SetImageDirection(args) was not working properly
    resamplefilter.Update()                         # Updating the resample image filter.
    
    filteringOutput = resamplefilter.GetOutput()
    
    if verbose:
        print(resamplefilter)
    #%%---------------- Rescaler Image Filter --------------------------
    RescalerFilterType = itk.RescaleIntensityImageFilter[InputImageType,OutputImageType]    # Defining the rescale image filter. 
    rescaler = RescalerFilterType.New()             # Pointer to the rescale filter
    rescaler.SetOutputMinimum(0)                    # Minimum output
    rescaler.SetOutputMaximum(255)                  # Maximum output 
    rescaler.SetInput(resamplefilter.GetOutput())   # Setting the input to the image filter. 
    
    filteringOutput = rescaler.GetOutput()
    
    if verbose:
        print(rescaler)
    
    #%%---------------- Flip Axis filter ------------------------------
    
    FlipFilterType = itk.FlipImageFilter[OutputImageType] 
    flipfilter = FlipFilterType.New()
    
    flipfilter.SetFlipAxes([0,0,0]) # Flip the axes along x and y but leave z intact.  
    flipfilter.SetInput(filteringOutput) # Setting the input to the flip filter.
    
    filteringOutput = flipfilter.GetOutput()
    
    if verbose:
        print(flipfilter)
    
     
    last_filter_output = filteringOutput    
    
    #%% ------------------ Writer ------------------------------------
    # The output of the resample filter can then be passed to a writer to
    # save the DRR image to a file.
    
    WriterType = itk.ImageFileWriter[OutputImageType]
    writer = WriterType.New()
    
    writer.SetFileName(output_filename)
    writer.SetInput(last_filter_output) # set the input as the output of filtering process. 
    
    try:
        print("Writing image: " + output_filename)
        writer.Update()
        print("Image Printed Successfully")
    except ValueError: 
        print("ERROR: ExceptionObject cauth! \n")
        print(ValueError)
        sys.exit()
    
    if verbose: 
        print('Details of image: ')
        print(last_filter_output)
          
