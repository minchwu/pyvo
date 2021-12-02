# -*- coding: utf-8 -*-
# author: Wu Mingchun

import numpy as np
import random
import matplotlib.pyplot as plt
from scipy.spatial import *
from scipy.spatial.qhull import Voronoi

"""Voronoi.2D
信息生成并导出至文本文件，供Abaqus调用
"""
# 六边形节点定位信息
width = np.sqrt(3)/2
height = 1
point_num_x = 5
point_num_y = 5
reg_area = 4

# 数据点生成
points = np.array([
    [width*i*[1, -1][kw], height*j*[1, -1][lh]+i % 2/2]
    for i in range(point_num_x)
    for kw in range(2)  # 对称生成坐标点
    for j in range(point_num_y+i % 2)  # 列的奇偶位置点数加减
    for lh in range(2)])  # 对称生成坐标点
points = np.unique(points, axis=0)  # 去除因对称引起的重复坐标

# 设定区域范围
points = points[np.all(np.abs(points) < reg_area, axis=1)]

# 生成泰森多边形信息
vor = Voronoi(points)

# 信息存储，供ABQ调用
np.savetxt(r'E:\FECAE\LATTICE\Voronoi\points.txt', vor.points, fmt='%.8f')
np.savetxt(r'E:\FECAE\LATTICE\Voronoi\vertices.txt', vor.vertices, fmt='%.8f')
np.savetxt(r'E:\FECAE\LATTICE\Voronoi\ridge_points.txt',
           vor.ridge_points, fmt='%d')
np.savetxt(r'E:\FECAE\LATTICE\Voronoi\ridge_vertices.txt',
           vor.ridge_vertices, fmt='%d')

plt.figure(num=1, figsize=(8, 8))
npoints = vor.vertices
for each in vor.ridge_vertices:
    each = np.asarray(each)
    if np.all(each >= 0):
        plt.plot(npoints[each, 0], npoints[each, 1], 'k')
plt.autoscale(tight=True)
plt.xlim([-width*3, width*3])
plt.ylim([-height*3, height*3])
plt.show()
