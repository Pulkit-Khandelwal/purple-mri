import os
import time
import glob
import random
import geomloss

import numpy as np
import scipy
import torch
from torch.autograd import grad

import plotly.graph_objs as go
import vtk
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk
import pymeshlab
import pandas as pd

from pykeops.torch import Vi, Vj

import os

# torch type and device
use_cuda = torch.cuda.is_available()
torchdeviceId = torch.device("cuda:0") if use_cuda else "cpu"
torchdtype = torch.float32

# PyKeOps counterpart
KeOpsdeviceId = torchdeviceId.index  # id of Gpu device (in case Gpu is  used)
KeOpsdtype = torchdtype.__str__().split(".")[1]  # 'float32'

use_cuda = torch.cuda.is_available()
torchdeviceId = torch.device("cuda:0") if use_cuda else "cpu"


# Read VTK mesh
def load_vtk(filename):
    rd = vtk.vtkPolyDataReader()
    rd.SetFileName(filename)
    rd.Update()
    return rd.GetOutput()

# Read points from the polydata
def vtk_get_points(pd):
    return vtk_to_numpy(pd.GetPoints().GetData())

# Read the faces from the polydata
def vtk_get_triangles(pd):
    return vtk_to_numpy(pd.GetPolys().GetData()).reshape(-1,4)[:,1:]

# Map all point arrays to cell arrays
def vtk_all_point_arrays_to_cell_arrays(pd):
    flt = vtk.vtkPointDataToCellData()
    flt.SetInputData(pd)
    flt.Update()
    return flt.GetOutput()

# Read a point array
def vtk_get_point_array(pd, name):
    a = pd.GetPointData().GetArray(name)
    return vtk_to_numpy(a) if a is not None else None

# Add a cell array to a mesh
def vtk_set_point_array(pd, name, array, array_type=vtk.VTK_FLOAT):
    a = numpy_to_vtk(array, array_type=array_type)
    a.SetName(name)
    pd.GetPointData().AddArray(a)

# Read a cell array
def vtk_get_cell_array(pd, name):
    a = pd.GetCellData().GetArray(name)
    return vtk_to_numpy(a) if a is not None else None

# Add a cell array to a mesh
def vtk_set_cell_array(pd, name, array):
    a = numpy_to_vtk(array)
    a.SetName(name)
    pd.GetCellData().AddArray(a)

# Make a VTK polydata from vertices and triangles
def vtk_make_pd(v, f):
    pd = vtk.vtkPolyData()

    pts = vtk.vtkPoints()
    pts.SetData(numpy_to_vtk(v))
    pd.SetPoints(pts)

    ca = vtk.vtkCellArray()
    ca.SetCells(f.shape[0], numpy_to_vtk(np.insert(f, 0, 3, axis=1).ravel(), array_type=vtk.VTK_ID_TYPE))
    pd.SetPolys(ca)
    return pd

# Save VTK polydata
def save_vtk(pd, filename, binary = False):
    wr=vtk.vtkPolyDataWriter()
    wr.SetFileName(filename)
    wr.SetInputData(pd)
    #wr.SetFileVersion(42)
    #wr.SetFileFormat(1,2)
    if binary:
        wr.SetFileTypeToBinary()
    wr.Update()


# This function loads a mesh and extracts derived objects/tensors
def load_mesh(fn, target_faces=None):
    pd = vtk_all_point_arrays_to_cell_arrays(load_vtk(fn))
    v, f = vtk_get_points(pd), vtk_get_triangles(pd)
    thickness = vtk_get_cell_array(pd, 'curv')
    if target_faces:
        v, f = decimate(v, f, target_faces)
    #lp = mesh_label_prob_maps(pd)
    return {
        'fn': fn,
        'pd': pd,
        'v': v,
        'f': f,
        'thickness': thickness,
        'vt': torch.tensor(v, dtype=torchdtype, device=torchdeviceId).contiguous(),
        'ft': torch.tensor(f, dtype=torch.long, device=torchdeviceId).contiguous()
        #'lp': lp,
        #'lpt': torch.tensor(lp, dtype=torchdtype, device=torchdeviceId).contiguous()
    }

dir_vtk_files_input=''
dir_vtk_files_output_with_nans=''

subjects = [f for f in os.listdir(dir_vtk_files_input) if f.endswith('.rh.thickness_5mm.pial.vtk')]
print("total subjects: ", len(subjects))
fwhm_list=['5']
surf_type_list=['pial']

for fwhm in fwhm_list:
    for surf_type in surf_type_list:
        print(fwhm, surf_type)
        for subj in subjects:
            print(subj)

            md_src_file =  dir_vtk_files_input + subj
            md_src = load_mesh(md_src_file)

            pd = vtk_make_pd(md_src['v'], md_src['f'])
            arr = md_src['thickness']
            arr[arr == 0] = np.NaN
            vtk_set_cell_array(pd, 'thickness', arr)
            save_vtk(pd, dir_vtk_files_output_with_nans + subj, binary=True)

####### check which cases in the AD continuum list have incorrect thickness
####### that is are there any cases with zero thickness in the template space


subjects=['']
print("total subjects: ", len(subjects))
for subj in subjects:
    try:
        subj = 'rh.' + subj + '.rh.thickness_5mm.pial.vtk'
        print(subj)
        md_src_file =  dir_vtk_files_input + subj
        md_src = load_mesh(md_src_file)

        pd = vtk_make_pd(md_src['v'], md_src['f'])
        arr = md_src['thickness']
        #print(np.max(arr))
        if np.max(arr) == 0:
            print("check this subject for zero thickness: ", subj)
    except:
        print("check this subject for flip-ness: ", subj)
