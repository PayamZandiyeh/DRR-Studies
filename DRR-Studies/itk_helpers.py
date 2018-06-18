# -*- coding: utf-8 -*-
'''General utility functions for working with ITK in Python'''

import itk
import numpy as np

def create_itk_image(dimension, pixel_string, image_region):
    '''Create an ITK image.

    No checks are performed to guarantee the inputs are valid
    inputs.

    Args:
        dimension (int):                Image dimensions
        pixel_string (string):          The pixel type as a string
        image_region (itk.ImageRegion): The image region over which the image is defined

    Returns:
        itk.Image:                      The created ITK image
    '''
    pixel_type = itk.ctype(pixel_string)
    image_type = itk.Image[pixel_type, dimension]
    image = image_type.New()
    image.SetRegions(image_region)
    image.Allocate()

    return image

def create_itk_image_region(dimension, index, size):
    '''Create an ITK image region.

    Image index and size are ordered (x,y,z). The index
    and size should have dimension number of elements. No
    error checking is performed.

    Args:
        dimension (int):  Image dimensions
        index (list):     The starting index of the image
        size (list):      The size of the image

    Returns:
        itk.ImageRegion:  The created ITK image region
    '''
    # Test inputs
    assert len(index) == dimension, "index must be of length dimension"
    assert len(size) == dimension, "size must be of length dimension"

    # Create region
    itk_index = itk.Index[dimension]()
    for idx in range(dimension):
        itk_index[idx] = index[idx]

    itk_size = itk.Size[dimension]()
    for idx in range(dimension):
        itk_size[idx] = size[idx]

    region = itk.ImageRegion[dimension]()
    region.SetSize(itk_size)
    region.SetIndex(itk_index)

    region.SetIndex(itk_index)

    return region

def set_itk_image_origin(image, origin):
    '''Set the origin of an ITK image.

    Origin is ordered (x,y,z). The input image is modified.
    The origin should have the same length as the image has
    dimensions.

    Args:
        image (itk.Image):  Input itkImage
        origin (list):      The starting index of the image

    Returns:
        None
    '''
    assert len(origin) == image.GetImageDimension(), \
      'Origin must be the same size as the image origins'
    np_origin = np.array(origin)
    image.SetOrigin(np_origin)

def set_itk_image_direction(image, direction):
    '''Set the direction matrix of an ITK image.

    Direction matrix should be indexed [row][column]. The input image is
    modified. The direction matrix should have the same number of rows
    and columns as the image has dimensions.

    Args:
        image (itk.Image):  Input itkImage
        direction (np.array):  The direction matrix

    Returns:
        None
    '''
    # Test inputs
    dimension = image.GetImageDimension()
    assert direction.shape == (dimension, dimension), \
        'Direction matrix should have same rows and columns has image has dimensions'

    # Assign the direction matrix
    direction_as_vnl_matrix = image.GetDirection().GetVnlMatrix()
    for ii in range(dimension):
        for jj in range(dimension):
            direction_as_vnl_matrix.put(ii, jj, direction[ii][jj])

def change_image_direction(oldDirection,newDirection,DimensionOut):
    '''
        change_image_direction(oldDirection,newDirection,DimensionOut)
        Changes the old Direction to a new direction (given the image dimension).
        Input Arguments:
        oldDirection : The original direction of the image e.g. image.GetDirection()
        newDirection : The direction that we like to set the image direction to.
        DimensionOut : The dimension of the image that we like to output (2D or 3D)
        
        '''
    #%%
    vnlMatrix = oldDirection.GetVnlMatrix()
    for i in range(DimensionOut):
        for j in range(DimensionOut):
            vnlMatrix.put(i,j,newDirection[i,j])


def print_direction(imageDirection,DimensionOut):
    vnlMatrix = imageDirection.GetVnlMatrix()
    for i in range(DimensionOut):
        for j in range(DimensionOut):
            print "{:>8.4f}".format(vnlMatrix.get(i,j)),
        print

def get_transform_direction(transform):
    vnl_matrix = transform.GetMatrix().GetVnlMatrix()
    return get_vnl_matrix(vnl_matrix)
    
def get_vnl_matrix(VnlMatrix):
    dummy = np.zeros((3,3))
    for ii in range(3):
        for jj in range(3):
            dummy[ii,jj]=VnlMatrix.get(ii,jj)
    return dummy
    
def rigid_body_transform3D(input_filename,output_filename,rot=[0.,0.,0.],t=[0.,0.,0.],cor=[0.,0.,0.],threshold=0.,default_pixel_value=0,min_out=0,max_out=255,verbose=False):
    """This function makes a rigid body transform on the 3D volume of image and writes it in the output"""
    #    input_filename  = '/Volumes/Storage/Projects/Registration/QuickData/OA-BEADS-CT.nii'
    #    output_filename = '/Volumes/Storage/Projects/Registration/QuickData/transformed_ct.nii'
    #    
    #    threshold  = 0.
    #    default_pixel_value = 100
    #    min_out = 0
    #    max_out = 255
    #    
    #    rot = [40. ,0. ,0.]   # Rotation in degrees in x, y, and z direction. 
    #    t   = [100. ,100. ,100.]   # translation in x, y, and z directions. 
    #    cor = [0. ,0. ,0.]   # offset of the rotation from the center of image (3D)
    #    
    #    
    #    verbose = False      # Verbose details of all steps. 
    #    
    
    #% ------------------------------- Import Libraries ------------------------
    import itk # imports insight Toolkit
    import numpy
    import sys
    #import StereoFlouroscopyRegistration.util.itk_helpers as Functions
    #%%------------------ Starting the main body of the code ---------------- 
    # -------------------- Reader -------------------------
    InputPixelType  = itk.ctype("short")
    DimensionIn  = 3
    
    InputImageType  = itk.Image[InputPixelType , DimensionIn ]
    
    
    ReaderType = itk.ImageFileReader[InputImageType]
    reader     = ReaderType.New()
    reader.SetFileName(input_filename)
    
    try:
        print("Reading image: " + input_filename)
        reader.Update()
        print("Image Read Successfully")
    except ValueError: 
        print("ERROR: ExceptionObject cauth! \n")
        print(ValueError)
        sys.exit()
        
    inputImage = reader.GetOutput()
    
    if verbose :
        print(inputImage)
        
    inOrigin     = inputImage.GetOrigin()                   # Get the origin of the image.
    inSpacing    = inputImage.GetSpacing()                  # Get the resolution of the input image.
    inSize       = inputImage.GetBufferedRegion().GetSize() # Get the size of the input image.
    inDirection  = inputImage.GetDirection()
    
    #%% ------------------ Transformation 
    # This part is inevitable since the interpolator (Ray-cast) and resample Image
    # image filter uses a Transformation -- Here we set it to identity. 
    TransformType = itk.CenteredEuler3DTransform[itk.D]
    transform     = TransformType.New()
    
    direction_mat = get_vnl_matrix(inDirection.GetVnlMatrix())
    
    rot = numpy.dot(-1,rot)           # Due to Direction of transform mapping ( 8.3.1 in the ITK manual)
    t   = numpy.dot(-1,t  )           # Due to Direction of transform mapping ( 8.3.1 in the ITK manual)
    
    
    
    rot = direction_mat.dot(numpy.transpose(rot))           
    t   = direction_mat.dot(numpy.transpose(t  ))          
    
    
    transform.SetRotation(numpy.deg2rad(rot[0]),numpy.deg2rad(rot[1]),numpy.deg2rad(rot[2])) # Setting the rotation of the transform
    transform.SetTranslation(itk.Vector.D3(t))    # Setting the translation of the transform
    transform.SetComputeZYX(True)  # The order of rotation will be ZYX. 
    
    center = direction_mat.dot(inOrigin)+ numpy.multiply(inSpacing,inSize)/2. # Setting the center of rotation as center of 3D object + offset determined by cor. 
    center = direction_mat.dot(center)-t # Convert the image to the local coordinate system. 
    transform.SetCenter(center)                     # Setting the center of rotation. 
    
    if verbose :
        print(transform)
    #% ------------------ Interpolator ------------------------------------
    InterpolatorType = itk.LinearInterpolateImageFunction[InputImageType,itk.D]
    interpolator = InterpolatorType.New()
     #%%----------------- Resample Image Filter -----------------------
     # In this part the resample image filter to map a 3D image to 2D image plane with desired specs is designed
    FilterType = itk.ResampleImageFilter[InputImageType,InputImageType]                     # Defining the resample image filter type. 
    resamplefilter = FilterType.New()                                                       # Pointer to the filter
#    R = Functions.get_transform_direction(transform)
#    T = numpy.transpose(t)
#    
    outOrigin = inOrigin - t #+ R.dot(numpy.transpose(direction_mat.dot(inOrigin)))
#    transform_matrix = Functions.get_vnl_matrix(transform.GetMatrix().GetVnlMatrix())
    #outDirection = transform_matrix.dot(direction_mat)
    outDirection = inDirection
    scaling = 1 # the scaling factor for the image. 
    
    outSize= [scaling*inSize[0],scaling*inSize[1],inSize[2]]
    
    resamplefilter.SetInput(inputImage)                                                     # Setting the input image data 
    resamplefilter.SetDefaultPixelValue(default_pixel_value)                                # Setting the default Pixel value
    resamplefilter.SetInterpolator(interpolator)                                            # Setting the interpolator
    resamplefilter.SetTransform(transform)                                                  # Setting the transform
    resamplefilter.SetSize(outSize)                                                         # Setting the size of the output image. 
    resamplefilter.SetOutputSpacing(inSpacing)                                              # Setting the spacing(resolution) of the output image. 
    # Functions.change_image_direction(resamplefilter.GetOutputDirection(),outDirection,3)
    resamplefilter.SetOutputOrigin(outOrigin)                                               # Setting the output origin of the image
    resamplefilter.SetOutputDirection(outDirection)                                         # Setting the output direction of the image. 
    resamplefilter.Update()                                                                 # Updating the resample image filter.
    
    if verbose:
        print(resamplefilter)
    
    
    #%% ------------------ Writer ------------------------------------
    # The output of the resample filter can then be passed to a writer to
    # save the DRR image to a file.
        
    WriterType=itk.ImageFileWriter[InputImageType]
    writer=WriterType.New()
    writer.SetFileName(output_filename)
    writer.SetInput(resamplefilter.GetOutput())
    
    try:
        print("Writing the transformed Volume at : " + output_filename)
        writer.Update()
        print("Volume Printed Successfully")
    except ValueError: 
        print("ERROR: ExceptionObject caugth! \n")
        print(ValueError)
        sys.exit()