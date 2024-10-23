import os
import sys
import numpy as np
import torch
from torch.autograd import grad
import vtk
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk
import pymeshlab
import pandas as pd
from pykeops.torch import Vi, Vj

# torch type and device
use_cuda = torch.cuda.is_available()
torchdeviceId = torch.device("cuda:0") if use_cuda else "cpu"
torchdtype = torch.float32

# PyKeOps counterpart
KeOpsdeviceId = torchdeviceId.index  # id of Gpu device (in case GPU is  used)
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
    #wr.SetFileVersion(1)
    wr.SetFileVersion(42)
    #wr.SetFileFormat(1,2)
    if binary:
        wr.SetFileTypeToBinary()
    wr.Update()

# Reduction using pymeshlab
def decimate(v, f, target_faces):
    ms = pymeshlab.MeshSet()
    ms.add_mesh(pymeshlab.Mesh(vertex_matrix=v, face_matrix=f))
    ms.meshing_decimation_quadric_edge_collapse(targetfacenum=target_faces,
                                                preserveboundary=True,
                                                preservenormal=True,
                                                preservetopology=True,
                                                planarquadric=True)
    m0 = ms.mesh(0)
    return m0.vertex_matrix(), m0.face_matrix()


# For LDDMM
def GaussKernel(sigma):
    x, y, b = Vi(0, 3), Vj(1, 3), Vj(2, 3)
    gamma = 1 / (sigma * sigma)
    D2 = x.sqdist(y)
    K = (-D2 * gamma).exp()
    return (K * b).sum_reduction(axis=1)

# For Varifold
def GaussLinKernel(sigma):
    x, y, u, v, b = Vi(0, 3), Vj(1, 3), Vi(2, 3), Vj(3, 3), Vj(4, 1)
    gamma = 1 / (sigma * sigma)
    D2 = x.sqdist(y)
    K = (-D2 * gamma).exp() * (u * v).sum() ** 2
    return (K * b).sum_reduction(axis=1)

# For Currents
def GaussLinCurrentsKernel(sigma):
    x, y, u, v = Vi(0, 3), Vj(1, 3), Vi(2, 3), Vj(3, 3)
    gamma = 1 / (sigma * sigma)
    D2 = x.sqdist(y)
    K = (-D2 * gamma).exp() * (u * v).sum()
    return K.sum_reduction(axis=1)

# For Currents
def GaussLinCurrentsKernel(sigma):
    x, y, u, v = Vi(0, 3), Vj(1, 3), Vi(2, 3), Vj(3, 3)
    gamma = 1 / (sigma * sigma)
    D2 = x.sqdist(y)
    K = (-D2 * gamma).exp() * (u * v).sum()
    return K.sum_reduction(axis=1)

# For Currents to match C++ code
def GaussLinCurrentsKernelC(sigma):
    x, y, u, v = Vi(0, 3), Vj(1, 3), Vi(2, 3), Vj(3, 3)
    gamma = 1 / (2 * sigma * sigma)
    D2 = x.sqdist(y)
    K = (-D2 * gamma).exp() * (u * v).sum() * 0.5
    return K.sum_reduction(axis=1)


# Forward integration
def RalstonIntegrator():
    def f(ODESystem, x0, nt, deltat=1.0):
        x = tuple(map(lambda x: x.clone(), x0))
        dt = deltat / nt
        l = [x]
        for i in range(nt):
            xdot = ODESystem(*x)
            xi = tuple(map(lambda x, xdot: x + (2 * dt / 3) * xdot, x, xdot))
            xdoti = ODESystem(*xi)
            x = tuple(
                map(
                    lambda x, xdot, xdoti: x + (0.25 * dt) * (xdot + 3 * xdoti),
                    x,
                    xdot,
                    xdoti,
                )
            )
            l.append(x)
        return l

    return f

# LDDMM definitions

def Hamiltonian(K):
    def H(p, q):
        return 0.5 * (p * K(q, q, p)).sum()

    return H


def HamiltonianSystem(K):
    H = Hamiltonian(K)

    def HS(p, q):
        Gp, Gq = grad(H(p, q), (p, q), create_graph=True)
        return -Gq, Gp

    return HS

def Shooting(p0, q0, K, nt=10, Integrator=RalstonIntegrator()):
    return Integrator(HamiltonianSystem(K), (p0, q0), nt)


def Flow(x0, p0, q0, K, deltat=1.0, Integrator=RalstonIntegrator()):
    HS = HamiltonianSystem(K)

    def FlowEq(x, p, q):
        return (K(x, q, p),) + HS(p, q)

    return Integrator(FlowEq, (x0, p0, q0), deltat)[0]


def LDDMMloss(K, dataloss, gamma=0):
    def loss(p0, q0):
        p, q = Shooting(p0, q0, K)[-1]
        return gamma * Hamiltonian(K)(p0, q0) + dataloss(q)

    return loss

# Basic Varifold loss
# VT: vertices coordinates of target surface,
# FS,FT : Face connectivity of source and target surfaces
# K kernel
def lossVarifoldSurf(FS, VT, FT, K):
    def get_center_length_normal(F, V):
        V0, V1, V2 = (
            V.index_select(0, F[:, 0]),
            V.index_select(0, F[:, 1]),
            V.index_select(0, F[:, 2]),
        )
        centers, normals = (V0 + V1 + V2) / 3, 0.5 * torch.cross(V1 - V0, V2 - V0)
        length = (normals**2).sum(dim=1)[:, None].sqrt()
        return centers, length, normals / length

    CT, LT, NTn = get_center_length_normal(FT, VT)
    cst = (LT * K(CT, CT, NTn, NTn, LT)).sum()

    def loss(VS):
        CS, LS, NSn = get_center_length_normal(FS, VS)
        return (
            cst
            + (LS * K(CS, CS, NSn, NSn, LS)).sum()
            - 2 * (LS * K(CS, CT, NSn, NTn, LT)).sum()
        )

    return loss


# Also implement a basic currents loss
def lossCurrentsSurf(FS, VT, FT, K):
    def get_center_length_normal(F, V):
        V0, V1, V2 = (
            V.index_select(0, F[:, 0]),
            V.index_select(0, F[:, 1]),
            V.index_select(0, F[:, 2]),
        )
        centers, normals = (V0 + V1 + V2) / 3, 0.5 * torch.cross(V1 - V0, V2 - V0)
        return centers, normals

    CT, NT = get_center_length_normal(FT, VT)
    cst = K(CT, CT, NT, NT).sum()
    
    def loss(VS):
        CS, NS = get_center_length_normal(FS, VS)
        tt,ss,st = cst, K(CS, CS, NS, NS).sum(), 2 * K(CS, CT, NS, NT).sum()
        print(f'tt: {tt}, ss: {ss}, st: {st}')
        return (
            cst
            + K(CS, CS, NS, NS).sum()
            - 2 * K(CS, CT, NS, NT).sum()
        )

    return loss

# This function loads a mesh and extracts derived objects/tensors
def load_mesh(fn, target_faces=None):
    pd = vtk_all_point_arrays_to_cell_arrays(load_vtk(fn))
    v, f = vtk_get_points(pd), vtk_get_triangles(pd)
    if target_faces:
        v, f = decimate(v, f, target_faces)
    #lp = mesh_label_prob_maps(pd)
    return {
        'fn': fn,
        'pd': pd,
        'v': v,
        'f': f,
        #'lp': lp,
        'vt': torch.tensor(v, dtype=torchdtype, device=torchdeviceId).contiguous(),
        'ft': torch.tensor(f, dtype=torch.long, device=torchdeviceId).contiguous()
        #'lpt': torch.tensor(lp, dtype=torchdtype, device=torchdeviceId).contiguous()
    }


def closure():
    optimizer.zero_grad()
    L = loss(p0, q0)
    print("loss", L.detach().cpu().numpy())
    L.backward()
    return L

print("decimating the mesh............")
src_path=str(sys.argv[1])
tgt_path=str(sys.argv[2])

md_src = load_mesh(os.path.join(src_path, sys.argv[3]))
print(md_src.keys(), len(md_src['f']), len(md_src['v']))

v_dec, f_dec = decimate(md_src['v'], md_src['f'], 300000)
print(len(v_dec), len(f_dec))
save_vtk(vtk_make_pd(v_dec, f_dec), os.path.join(tgt_path, sys.argv[4]))
