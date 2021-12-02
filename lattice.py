# -*- coding: utf-8 -*-
# author: Wu Mingchun


"""FEM.

Voronoi Lattice for Heat-Transfer
"""

# 第三方库导入
from abaqus import *
from abaqusConstants import *
import numpy as np

# 数据库名定义
MODEL_NAME = 'Voronoi'
PART_NAME = 'PART-1'

# 几何信息读取
points = np.loadtxt(
    r'E:\FECAE\LATTICE\Voronoi\points.txt', dtype=float)
vertices = np.loadtxt(
    r'E:\FECAE\LATTICE\Voronoi\vertices.txt', dtype=float)
ridge_vertices = np.loadtxt(
    r'E:\FECAE\LATTICE\Voronoi\ridge_vertices.txt', dtype=int)

# 模型数据库生成
mdb.Model(name=MODEL_NAME, modelType=STANDARD_EXPLICIT)
md = mdb.models[MODEL_NAME]

# 部件生成
md.Part(name=PART_NAME)
part = md.parts[PART_NAME]

# 参考平面
part.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=0.0)
part.DatumAxisByPrincipalAxis(principalAxis=XAXIS)
part.DatumAxisByPrincipalAxis(principalAxis=YAXIS)

# 几何草图
sketch = md.ConstrainedSketch(
    name='sketch-1',
    sheetSize=100,
    gridSpacing=5)
sketch.setPrimaryObject(option=SUPERIMPOSE)  # 草图视图定位

# 草图绘图
sketch.rectangle(
    point1=(-2.6, -3.0),
    point2=(2.6, 3.0))
sketch.setPrimaryObject(option=SUPERIMPOSE)  # 草图视图定位

# 参考特征
datums = part.datums
# 几何部件shell
part.Shell(
    sketchPlane=datums[1],  # 空间定位
    sketchUpEdge=datums[3],
    sketchPlaneSide=SIDE1,
    sketchOrientation=RIGHT,
    sketch=sketch)
part.setPrimaryObject()

sketch = md.ConstrainedSketch(
    name='sketch-2',
    sheetSize=100,
    gridSpacing=5)
sketch.setPrimaryObject(option=SUPERIMPOSE)

for each in ridge_vertices:
    if np.all(each >= 0):
        v1 = vertices[each[0]]
        v2 = vertices[each[1]]
        sketch.Line(point1=v1, point2=v2)
sketch.setPrimaryObject(option=SUPERIMPOSE)

# 分割平面选取
faces = part.faces
# 选区框构建
box = faces.getBoundingBox()['low'] + faces.getBoundingBox()['high']
pfaces = faces.getByBoundingBox(*box)
part.PartitionFaceBySketch(
    sketchUpEdge=datums[3], faces=pfaces, sketch=sketch)
part.setPrimaryObject()

# 元数据点-参考点
for each in points:
    each = np.append(each, 0)
    part.DatumPointByCoordinate(coords=each)

# Voronoi 多边形节点
for each in vertices:
    each = np.append(each, 0)
    part.DatumPointByCoordinate(coords=each)

# TODO: build a datum-plane and an axis-y for the shell

# imprint polyline
# for each in ridge_vertices:
#     if np.all(each >= 0):
#         v1 = np.append(vertices[each[0]], 0)
#         v2 = np.append(vertices[each[1]], 0)
#         part.WirePolyLine(points=((v1, v2)),)

# separate polyline
# for each in ridge_vertices:
#     if np.all(each >= 0):
#         v1 = np.append(vertices[each[0]], 0)
#         v2 = np.append(vertices[each[1]], 0)
#         part.WirePolyLine(points=((v1, v2)), mergeType=SEPARATE, meshable=ON)
