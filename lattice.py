# -*- coding: utf-8 -*-
# author: Wu Mingchun


"""FEM.

Voronoi Lattice for Heat-Transfer
Define ABQ-Key Ctrl-R
"""

# 第三方库导入
from abaqus import *
from abaqusConstants import *
import numpy as np
import regionToolset
from material import createMaterialFromDataString
import os

# 数据库名定义
MODEL_NAME = 'Voronoi-Rand'
PART_NAME = 'PART-1'
INST_NAME = 'PART-1-1'
GWIDTH = 2.6
GHEIGHT = 3

# 工作目录设置
WORK_DIR = r'E:/FECAE/LATTICE/'
os.chdir(WORK_DIR)
# 模型保存
# mdb.saveAs(pathName='{}{}'.format(WORK_DIR, MODEL_NAME))

MAT_NAME = 'T300'
# 材料属性
MATSTRING = """
    {'name': 'T300',
    'materialIdentifier': '',
    'description': '',
    'elastic':
    {'noTension': OFF, 'temperatureDependency': OFF,
    'moduli': LONG_TERM, 'dependencies': 0, 'noCompression': OFF,
    'table': ((125000.0, 9000.0, 9000.0, 0.32, 0.32, 0.46, 4600.0, 4600.0, 3082.0),),
    'failStress': {'temperatureDependency': OFF,
    'table': ((1760.0, 1050.0, 51.0, 130.0, 60.0, 0.0, 0.0),), 'dependencies': 0},
    'type': ENGINEERING_CONSTANTS},
    'density': {'temperatureDependency': OFF,
    'table': ((1.6e-09,),),
    'dependencies': 0, 'fieldName': '',
    'distributionType': UNIFORM}}"""

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

"""几何建模"""
# 部件生成
md.Part(name=PART_NAME)
part = md.parts[PART_NAME]
session.viewports['Viewport: 1'].view.setProjection(projection=PARALLEL)

# 参考平面
part.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=0.0)
part.DatumAxisByPrincipalAxis(principalAxis=XAXIS)
part.DatumAxisByPrincipalAxis(principalAxis=YAXIS)
# 适应视图
session.viewports['Viewport: 1'].view.fitView()

# 几何草图
sketch = md.ConstrainedSketch(
    name='sketch-1',
    sheetSize=100,
    gridSpacing=5)

# 草图绘图
sketch.rectangle(
    point1=(-GWIDTH, -GHEIGHT),
    point2=(GWIDTH, GHEIGHT))

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
# 适应视图
session.viewports['Viewport: 1'].view.fitView()

sketch = md.ConstrainedSketch(
    name='sketch-2',
    sheetSize=100,
    gridSpacing=5)
# 晶界网格
for each in ridge_vertices:
    if np.all(each >= 0):
        v1 = vertices[each[0]]
        v2 = vertices[each[1]]
        sketch.Line(point1=v1, point2=v2)

# 分割平面选取
faces = part.faces
# 选区框构建
box = faces.getBoundingBox()['low'] + faces.getBoundingBox()['high']
pfaces = faces.getByBoundingBox(*box)
part.PartitionFaceBySketch(
    sketchUpEdge=datums[3], faces=pfaces, sketch=sketch)
part.setPrimaryObject()
# 适应视图
session.viewports['Viewport: 1'].view.fitView()
# Voronoi 多边形节点
# for each in vertices:
#     each = np.append(each, 0)
#     part.DatumPointByCoordinate(coords=each)

"""材料属性"""
# 元数据点-参考点-局部坐标系生成
# RM = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]]) # 旋转变换
part.DatumCsysByThreePoints(
    coordSysType=CARTESIAN,
    origin=(0, 0, 0),
    point1=(1, 0, 0),
    point2=(0, 1, 0))
for each in points:
    if (np.abs(each[0]) <= GWIDTH) and (np.abs(each[1]) <= GHEIGHT):
        each = np.append(each, 0)
        # 点旋转张成坐标系
        # point1 = each+np.append(np.random.random(2), 0)
        # point2 = np.matmul(RM, point1)
        # # part.DatumPointByCoordinate(coords=each)
        # 张开标准局部坐标，添加随机旋转角度
        # box = np.append(each-1, each+1)
        # df = faces.getByBoundingBox(*box)
        # findAt() local face
        """生成几何序列对象"""
        face = faces.findAt((each,))
        region = regionToolset.Region(faces=face)
        orientation = datums[6]
        rotAng = np.random.rand()*360  # 随机角度旋转
        part.MaterialOrientation(
            region=region,
            orientationType=SYSTEM,
            axis=AXIS_3,
            localCsys=orientation,
            fieldName='',
            additionalRotationType=ROTATION_ANGLE,
            additionalRotationField='',
            angle=rotAng)

# 材料定义 T300
createMaterialFromDataString(
    modelName=MODEL_NAME,
    name=MAT_NAME,
    version='2021',
    dataString=MATSTRING)
# 截面定义 Shell
md.HomogeneousShellSection(
    name='Section-1',
    preIntegrate=OFF,
    material=MAT_NAME,
    thicknessType=UNIFORM,
    thickness=1.0,
    thicknessField='',
    nodalThicknessField='',
    idealization=NO_IDEALIZATION,
    poissonDefinition=DEFAULT,
    thicknessModulus=None,
    temperature=GRADIENT,
    useDensity=OFF,
    integrationRule=SIMPSON,
    numIntPts=5)
# 材料填充区域
region = part.Set(faces=faces, name='Voronoi')
# 截面赋予
part.SectionAssignment(
    region=region,
    sectionName='Section-1',
    offset=0.0,
    offsetType=MIDDLE_SURFACE,
    offsetField='',
    thicknessAssignment=FROM_SECTION)

"""装配"""
mds = md.rootAssembly
mds.DatumCsysByDefault(CARTESIAN)
inst = mds.Instance(name=INST_NAME, part=part, dependent=ON)
session.viewports['Viewport: 1'].view.setProjection(projection=PARALLEL)

"""分析步"""
md.StaticStep(
    name='Step-1',
    previous='Initial',
    initialInc=0.1,
    maxInc=0.1,
    nlgeom=ON)

"""边界与载荷"""
edges = inst.edges
# 覆盖框
box_high = edges.getBoundingBox()['high']
box_low = edges.getBoundingBox()['low']
# 边界选取框
edges1 = edges.getByBoundingBox(
    box_low[0]-1e-5, box_low[1]-1e-5, box_low[2]-1e-5,
    box_low[0]+1e-5, box_high[1]+1e-5, box_high[2]+1e-5)
region = mds.Set(edges=edges1, name='BC-1')
md.DisplacementBC(
    name='BC-1',
    createStepName='Initial',
    region=region,
    u1=SET, u2=SET, u3=SET,
    ur1=SET, ur2=SET, ur3=SET,
    amplitude=UNSET,
    distributionType=UNIFORM,
    fieldName='',
    localCsys=None)
# 载荷
edges2 = edges.getByBoundingBox(
    box_high[0]-1e-5, box_low[1]-1e-5, box_low[2]-1e-5,
    box_high[0]+1e-5, box_high[1]+1e-5, box_high[2]+1e-5)
region = mds.Set(edges=edges2, name='DISP-1')
md.DisplacementBC(
    name='DISP-1',
    createStepName='Step-1',
    region=region,
    u1=1.0, u2=0.0, u3=0.0,
    ur1=0.0, ur2=0.0, ur3=0.0,
    amplitude=UNSET,
    distributionType=UNIFORM,
    fieldName='',
    localCsys=None)
# 视图重置
session.viewports['Viewport: 1'].setValues(displayedObject=mds)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-1')
session.viewports['Viewport: 1'].view.fitView()

"""网格划分"""
part.seedPart(
    size=0.01*(GWIDTH+GHEIGHT),
    deviationFactor=0.1,
    minSizeFactor=0.1)
part.generateMesh()

"""任务提交计算"""
mds.regenerate()
job_name = MODEL_NAME
mdb.Job(
    name=job_name,
    model=MODEL_NAME,
    description='',
    type=ANALYSIS,
    atTime=None,
    waitMinutes=0,
    waitHours=0,
    queue=None,
    memory=90,
    memoryUnits=PERCENTAGE,
    getMemoryFromAnalysis=True,
    explicitPrecision=SINGLE,
    nodalOutputPrecision=SINGLE,
    echoPrint=OFF,
    modelPrint=OFF,
    contactPrint=OFF,
    historyPrint=OFF,
    userSubroutine='',
    scratch='',
    resultsFormat=ODB,
    multiprocessingMode=DEFAULT,
    numCpus=2,
    numDomains=2,
    numGPUs=0)

# 模型保存
# mdb.save()
# 任务提交
# TODO: 批处理任务提交
mdb.jobs[job_name].submit(consistencyChecking=OFF)

# """后处理

# 结果计算时间存在延迟，后处理程序需要分离执行
# """
# # 结果文件读取
# odb1 = session.openOdb(name='{}/{}.odb'.format(WORK_DIR, job_name))
# # 视图载入
# session.viewports['Viewport: 1'].setValues(displayedObject=odb1)
# session.viewports['Viewport: 1'].makeCurrent()
# # 显示云图
# session.viewports['Viewport: 1'].odbDisplay.display.setValues(
#     plotState=(CONTOURS_ON_DEF, ))
# # 显示位移图
# session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
#     variableLabel='U', outputPosition=NODAL, refinement=(COMPONENT, 'U1'), )
# # 隐藏网格线
# session.viewports['Viewport: 1'].odbDisplay.commonOptions.setValues(
#     visibleEdges=FREE)
# # 设置视图
# session.viewports['Viewport: 1'].view.setValues(session.views['Front'])
# session.viewports['Viewport: 1'].view.fitView()
