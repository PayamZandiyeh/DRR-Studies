# -*- coding: utf-8 -*-
'''Read a medical image'''

import vtk
import itk
import numpy as np

def get_vtk_reader_from_file_name(file_name):
    '''Find a valid vtkImageReader2 for a give file.

    If no reader can be found, None is returned. Currently, this
    function does not support reading in a DICOM series.

    The following readers are registered beyond the standard:
    vtkNIFTIImageReader, vtkDICOMImageReader.

    Args:
        file_name (string):     Input file name on disk

    Returns:
        vtk.vtkImageReader2:    The vtkImageReader2
    '''

    # Add readers which are not registered by default
    vtk.vtkImageReader2Factory.RegisterReader(vtk.vtkNIFTIImageReader())
    vtk.vtkImageReader2Factory.RegisterReader(vtk.vtkNrrdReader())

    # Disable the DICOM reader. It prints too many errors.
    # vtk.vtkImageReader2Factory.RegisterReader(vtk.vtkDICOMImageReader())

    # Use factory to return the correct reader
    reader = vtk.vtkImageReader2Factory.CreateImageReader2(file_name)
    return reader

def get_itk_homogeneous_coordinate_matrix(file_name):
    '''Read the homogeneous coordinates matrix in ITK.

    The coordinates are in the ITK frame of reference. In general, the
    ITK coordinate system indexes at point (P) from the image index (I)
    using an origin (O), an orthonormal direction cosine matrix (D), and
    diagnoal spacing matrix (S).
        P = O + D * diag(S) * I
    We keep the homogeneous coordinates as such:
        T = [ D | O ]
    We assume that VTK will take care of the image spacing for us, which
    is a reasonable assumption.

    None is returned if no itkImageIO is found. It is possible that
    an image is readable by VTK but no orientation can be found by
    ITK. It is also possible that an image is reordered when read by
    VTK causing the image to have a different orientation than ITK would
    expect.

    Args:
        file_name (string):     Input file name on disk

    Returns:
        np.array:               The orientation matrix in homogeneous coordinates
    '''
    # Try to get the ImageIO given the file name
    imageIO = itk.ImageIOFactory.CreateImageIO(file_name, itk.ImageIOFactory.ReadMode)
    if imageIO is None:
        return None
    imageIO.SetFileName(file_name)
    imageIO.ReadImageInformation()

    # Read the direction matrix, multiply by spacing
    image_dimensions = imageIO.GetNumberOfDimensions()
    orientation_matrix = np.zeros((image_dimensions+1, image_dimensions+1))
    for ii in range(image_dimensions):
        this_direction = imageIO.GetDirection(ii)
        # this_spacing = imageIO.GetSpacing(ii)
        for jj in range(image_dimensions):
            orientation_matrix[jj, ii] = this_direction[jj]

    # Read the origin
    for i in range(image_dimensions):
        orientation_matrix[i, image_dimensions] = imageIO.GetOrigin(i)
    orientation_matrix[image_dimensions, image_dimensions] = 1

    return orientation_matrix

def get_itk_image_type(file_name):
    '''Determine the image type for a file on disk.

    This can largely be replaced with itk.imread except for DICOM images
    where the image type must be known.

    If the file doesn't exist or an itk.ImageIO cannot be found, None is
    returned. This functions throws a KeyError if the input type is not
    supported.

    See https://gist.github.com/fbudin69500/e58cf629cc6069b3cdcc for example
    code. This may fail for int type images. Typically, you can get away with
    reading those images as short.

    Args:
        file_name (string): Input file name on disk

    Returns:
        itk.Image:  The created image type
    '''
    # Try to get the ImageIO given the file name
    imageIO = itk.ImageIOFactory.CreateImageIO(file_name, itk.ImageIOFactory.ReadMode)
    if imageIO is None:
        return None
    imageIO.SetFileName(file_name)
    imageIO.ReadImageInformation()

    # Get pixel type and dimension
    pixel_type_as_string = imageIO.GetComponentTypeAsString(imageIO.GetComponentType())
    pixel_type = get_itk_image_type.component_type_to_itk_type_dict[pixel_type_as_string]
    dimensions = imageIO.GetNumberOfDimensions()

    return itk.Image[pixel_type, dimensions]

# Create dictionary to map from ImageIOBase type to ctype
get_itk_image_type.component_type_to_itk_type_dict = {
    'float':            itk.F,  'double':           itk.D,
    'unsigned_char':    itk.UC, 'unsigned_short':   itk.US, 'unsigned_int': itk.UI,
    'unsigned_long':    itk.UL, 'signed_char':      itk.SC, 'signed_short': itk.SS,
    'signed int':       itk.SI, 'signed_long':      itk.SL, 'bool':         itk.B,
    'short':            itk.SS
}
