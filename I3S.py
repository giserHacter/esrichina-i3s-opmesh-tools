
# -*- coding: UTF-8 -*-
##################
#author xp 20180802 修订：xupf  完善一些api内容
#I3S API version 1.6
#产品技术部
##############################################
import json
import gzip
import os
import zipfile
import struct

# i3s类
# I3S 文件路径
# create by xp dt:20180802 
class I3S():
    def __init__(self,I3SFilePath):
        self.i3SPath=I3SFilePath
        # LayerInfo 图层信息
        layerInfoPath=os.path.join(self.i3SPath,'3dSceneLayer.json.gz')
        self.sceneLayerInfo=SceneLayerInfo(layerInfoPath)

        # nodesPath=os.path.join(self.i3SPath,'nodes')
        # self.nodes=I3SNode(nodesPath)
        # 根节点
        rootNodePath=os.path.join(self.i3SPath,r'nodes\root\3dNodeIndexDocument.json.gz')
        self.i3SRootNode=I3SRootNode(rootNodePath)

        # 元数据
        # metadataPath=os.path.join(self.i3SPath,'metadata.json')
        # self.metadata=Metadata(metadataPath)

    # 获得所有节点数据
    def GetI3SNotes(self):
        nodesPath=os.path.join(self.i3SPath,'nodes')
        i3SNotes=[]
        for root,dirs,files in os.walk(nodesPath):
            for item in dirs:
                if item!='root':
                    i3SNotes.append(I3SNode(os.path.join(nodesPath,item,'3dNodeIndexDocument.json.gz')))
            break
        return i3SNotes
    

        
    # 根据ID查找Node
    # ID号
    # 返回值：note
    def FindNodebyID(self,id):
        nodePath=os.path.join(self.i3SPath,id)
        node=I3SNode(nodePath)
        return node

# i3s元数据类
# FilePath：I3S元数据文件路径
# create by xp dt:20180802 
class Metadata():
    def __init__(self,FilePath):
        self.filePath=FilePath
        metadatafile = open(self.filePath,'r',encoding='utf-8')
        file_content=metadatafile.read()
        self.metadataJson=json.loads(file_content)
        metadatafile.close()

# SceneLayerInfo基本信息
# 主要用来查询SceneLayer相关信息
# FilePath：SceneLayerInfo文件路径
# crateby xp dt:20180801
class SceneLayerInfo():
    # 初始化SceneLayerInfo
    # InputSceneLayerInfoFile：3dSceneLayer.json.gz 压缩包地址
    def __init__(self,FilePath):
        self.filePath=FilePath
        sceneLayerFile=gzip.open(self.filePath,'rb')
        file_content=sceneLayerFile.read()
        self.sceneLayerJson=json.loads(file_content)
        sceneLayerFile.close()
    
    # 获得空间参考
    def GetSpatialReference(self):
        return self.sceneLayerJson['spatialReference']
    # 获得空间参考
    def GetsceneLayerJson(self):
        return self.sceneLayerJson
    # 设置空间参考
    # NewSR:目标空间参考
    def SetSpatialReference(self, NewSR):
        self.sceneLayerJson['spatialReference']=NewSR
    
    # 获得空间范围
    def GetLayerExtent(self):
        return self.sceneLayerJson['store']['extent']
	#add xupf 调整空间索引链接
    def CRSindexChange(self,newwikd):
        self.sceneLayerJson['store']['indexCRS']="http://www.opengis.net/def/crs/EPSG/0/"+str(newwikd)
        self.sceneLayerJson['store']['vertexCRS']="http://www.opengis.net/def/crs/EPSG/0/"+str(newwikd)
    #add xupf 调整发现参考框架
    def normalReferenceFrame(self):
        self.sceneLayerJson['store']['normalReferenceFrame']="vertex-reference-frame"
    # 设置空间范围
    # NewExtent；目标空间范围
    def SetLayerExtent(self, NewExtent):
        self.sceneLayerJson['store']['extent']=NewExtent

    # 保存Json到gz压缩包
    def SaveJsonToGZ(self):
        sceneLayerFile=gzip.open(self.filePath,'wb')
        saveJson=json.dumps(self.sceneLayerJson)
        sceneLayerFile.write(str.encode(saveJson))
        sceneLayerFile.close()        

# I3S根节点
# FilePath：更节点路径
# create by xp dt20180801
class I3SRootNode():
    def __init__(self,FilePath):
        self.filePath=FilePath
        rootFile=gzip.open(self.filePath,'rb')
        file_content=rootFile.read()
        self.rootJson=json.loads(file_content)
        rootFile.close()
    
    # 保存json到压缩包
    def SaveJsonToGZ(self):
        saveJson=json.dumps(self.rootJson)
        rootFile=gzip.open(self.filePath,'wb')
        rootFile.write(str.encode(saveJson))
        rootFile.close()

# I3S节点
# FilePath：节点路径
# create by xp dt 20180801
class I3SNode():
    def __init__(self,FilePath):
        self.filePath=FilePath
        nodeFile=gzip.open(self.filePath,'rb')
        file_content=nodeFile.read()
        self.i3SNodeJson=json.loads(file_content)
        nodeFile.close()


    # 最小内切球
    def GetMBS(self):
        return self.i3SNodeJson['mbs']

    # 设置最小内切球
    # NewMBS：目标内切球
    def SetMBS(self,NewMBS):
        self.i3SNodeJson['mbs']=NewMBS

    # 最小定向外包矩形
    def GetOBB(self):
        if 'obb' in self.i3SNodeJson.keys() and  self.i3SNodeJson['obb']:
            return self.i3SNodeJson['obb']

    # 设置最小外包矩形
    # NewOBB：目标外包矩形
    def SetOBB(self,NewOBB):
        self.i3SNodeJson['obb']=NewOBB

    # 获得父节点
    def GetParentNode(self):
        return self.i3SNodeJson['parentNode']

    #设置父节点
    # NewParentNode：目标父节点
    def SetParentNode(self,NewParentNode):
        self.i3SNodeJson['parentNode']=NewParentNode

    # 获得子节点
    def GetChildrens(self):
        childrenNode=[]
        if 'children' in self.i3SNodeJson.keys() and  self.i3SNodeJson['children']:
            if len(self.i3SNodeJson['children'])>0:
                rootNodePath=os.path.split(self.filePath)[0]
                os.chdir(rootNodePath)
                for childnode in self.i3SNodeJson['children']:
                    fullPath=os.path.abspath(childnode['href'])
                    nodePath=os.path.join(fullPath,'3dNodeIndexDocument.json.gz')
                    childrenNode.append(I3SNode(nodePath))

        return childrenNode

    # 设置子节点
    # newChildrens：新子节点集合
    def SetChildrens(self,newChildrens):
        self.i3SNodeJson['children']=newChildrens

    # 保存json到压缩包
    def SaveJsonToGZ(self):
        saveJson=json.dumps(self.i3SNodeJson)
        nodeFile=gzip.open(self.filePath,'wb')
        nodeFile.write(str.encode(saveJson))
        nodeFile.close()

    # 获得属性attributeData引用地址
    def GetAttributes(self):
        attributes=[]
        if 'attributeData' in self.i3SNodeJson.keys() and self.i3SNodeJson['attributeData']:
            for index in len(self.i3SNodeJson['attributeData']):
                attributes.append(self.GetAttribute(index))
            return attributes

    # 根据索引获得属性 
    # index:属性索引
    def GetAttribute(self,index=0):
        rootNodePath=os.path.split(self.filePath)[0]
        os.chdir(rootNodePath)
        gzPath=self.i3SNodeJson['attributeData'][index]['href']+'.bin.gz'
        gzPath=os.path.abspath(gzPath)
        attribute=Attribute(gzPath)
        return attribute  

    # 获得Features引用地址
    def GetFeatures(self):
        features=[]
        if 'featureData' in self.i3SNodeJson.keys() and self.i3SNodeJson['featureData']:
            for index in range(len(self.i3SNodeJson['featureData'])):
                features.append(self.GetFeature(index))
            return features
        return features

    # 根据索引获得Feature
    # index：feature 索引
    def GetFeature(self,index=0):
        rootNodePath=os.path.split(self.filePath)[0]
        os.chdir(rootNodePath)
        gzPath=self.i3SNodeJson['featureData'][index]['href']+'.json.gz'
        gzPath=os.path.abspath(gzPath)
        feature=Features(gzPath)
        return feature

    # 获得Geometry
    def GetGeometries(self):
        geometries=[]
        if 'geometryData' in self.i3SNodeJson.keys() and self.i3SNodeJson['geometryData']:
            for index in range(len(self.i3SNodeJson['geometryData'])):
                geometries.append(self.GetGeometry(index))
            return geometries
        return geometries

    # 根据索引获得Geometry
    # index:索引
    def GetGeometry(self,index=0):
        rootNodePath=os.path.split(self.filePath)[0]
        os.chdir(rootNodePath)
        binPath=self.i3SNodeJson['geometryData'][index]['href']+'.bin.gz'
        binPath=os.path.abspath(binPath)
        rule=self.GetFeature(index).GeometryRule()
        geometry=Geometry(binPath,rule)
        return geometry

    #获得材质
    def GetShared(self):
        rootNodePath=os.path.split(self.filePath)[0]
        os.chdir(rootNodePath)
        filePath=self.i3SNodeJson['sharedResource']['href']+'\\sharedResource.json.gz'
        filePath=os.path.abspath(filePath)
        shared=Shared(filePath)
        return shared

    # 获得贴图
    #这里可能会出现小问题 xupf
    def GetTextures(self):
        textures=[]
        if 'textureData' in self.i3SNodeJson.keys() and self.i3SNodeJson['textureData']:
            for index in len(self.i3SNodeJson['textureData']):
                textures.append(index)
            return textures
        return textures

    # 根据索引获得贴图
    # index: 索引
    def GetTexture(self,index=0):
        if 'textureData' in self.i3SNodeJson.keys() and  self.i3SNodeJson['textureData']:
            rootNodePath=os.path.split(self.filePath)[0]
            os.chdir(rootNodePath)
            binPath=self.i3SNodeJson['textureData'][index]['href']+'.bin'
            binPath=os.path.abspath(binPath)
            texture=Texture(binPath)
            return texture
      
# Attribute类
# Attribute文件路径
# create by xp dt:20180802 
class Attribute():
    def __init__(self,FilePath):
        self.filePath=FilePath
        attributeFile=gzip.open(self.filePath,'rb')
        self.attributeFileBin=attributeFile.read()
        attributeFile.close()

    # 保存属性到gz压缩包
    def SaveBinToGZ(self):
        with gzip.open(self.filePath,'wb') as wf:
            wf.write(self.attributeFileBin)
            wf.close()

# Texture类
# Texture文件路径
# create by xp dt:20180802 
class Texture():
    def __init__(self,FilePath):
        
        self.filePath=FilePath
        # self.rules=Rules
        textureFile=gzip.open(self.filePath,'rb')
        self.textureBin=textureFile.read()
        textureFile.close()

    # 保存贴图到二进制文件
    def SaveBinToGZ(self):
        with gzip.open(self.filePath,'wb') as wf:
            wf.write(self.textureBin)
            wf.close()


# FeatureData类
# 待完善
# create by xp dt:20180802 
class FeatureData():
    def __init__(self):
        self.id=-1
        self.position=[]
        self.pivotOffset=[]
        self.mbb=[]
        self.layer=''
        self.geometries=None

# Features类
# Features文件路径
# create by xp dt:20180802 
class Features():
    def __init__(self,FilePath):
        self.filePath=FilePath
        featureFile=gzip.open(self.filePath,'r')
        file_content=featureFile.read()
        self.featureJson=json.loads(file_content)
        featureFile.close()

    # 获得所有ID 这个id表示的是返回列表元素的下标
    def featureDataArray(self):
        return self.featureJson['featureData']
        
    # 根据索引获得ID
    # index:索引
    def GetID(self, index=0):
        return self.featureJson['featureData'][index]['id']

    # 根据索引获得位置
    # index:索引
    def GetPosition(self,index=0):
        return self.featureJson['featureData'][index]['position']

    # 根据索引更新位置
    # index:索引
    def SetPosition(self,NewPosition,index=0):
        self.featureJson['featureData'][index]['position']=NewPosition
    
    #根据索引获得最小边界包围盒
    # index:索引
    def GetMbb(self,index=0):
        return self.featureJson['featureData'][index]['mbb']

    def SetMbb(self,NewMbb,index=0):
        self.featureJson['featureData'][index]['mbb']=NewMbb

    # 根据索引获得GeometryData
    # index:索引
    def GeometryData(self):
        return self.featureJson['geometryData']

    # 根据索引获得GeometryTransformation
    # index:索引
    def GetGeometryTransformation(self,index=0):
        return self.featureJson['geometryData'][index]['transformation']

    # 根据索引更新GeometryTransformation
    # index:索引
    def SetGeometryTransformation(self,NewTransformation, index=0):
        self.featureJson['geometryData'][index]['transformation']=NewTransformation

    # 根据索引获得GeometryRule
    # index:索引
    def GeometryRule(self,index=0):
        return self.featureJson['geometryData'][index]['params']['vertexAttributes']
    # 根据索引获得GeometryRule1
    # index:索引
    #by xupf 进行节点几何删除抽稀操作
    def GeometryRule1(self,index=0):
        return self.featureJson['geometryData'][index]['params']['featureAttributes']
    # 保存到gz压缩包
    def SaveJsonToGZ(self):
        saveJson=json.dumps(self.featureJson)
        featureFile=gzip.open(self.filePath,'w')
        featureFile.write(str.encode(saveJson))
        featureFile.close()

# Geometry类
# FilePath：Geometry文件路径
# Rules：解析规则
# create by xp dt:20180802 
class Geometry():
    def __init__(self,FilePath,Rules):
        self.filePath=FilePath
        self.rules=Rules
        geometryFile=gzip.open(self.filePath,'rb')
        self.geometryBin=geometryFile.read()
        geometryFile.close()

    
    # # 初始化位置，法线，UV,颜色
    # def Init(self, parameter_list):
    #     self.positionCollection=self.GetPositions()
    #     self.normalCollection=self.GetPosition()
    #     self.uv0Collection=self.GetPosition()
    #     self.colorCollection=self.GetPosition()

    # 获得所有的顶点位置
    def GetPositions(self):
        count=self.rules['position']['count']
        i=0
        positionCollection=[]
        while (i<count):
            positionCollection.append(self.GetPosition(i))
            i+=1
        return positionCollection

    # 获得所有顶点法线
    def GetNormals(self):
        count=self.rules['normal']['count']
        i=0
        normalCollection=[]
        while (i<count):
            normalCollection.append(self.GetNormal(i))
            i+=1
        return normalCollection

    # 获得所有顶点的UV
    def GetUV0s(self):
        count=self.rules['uv0']['count']
        i=0
        uv0Collection=[]
        while (i<count):
            uv0Collection.append(self.GetUV0(i))
            i+=1
        return uv0Collection

    # 获得所有顶点颜色
    def GetColors(self):
        count=self.rules['color']['count']
        i=0
        colorCollection=[]
        while (i<count):
            colorCollection.append(self.GetColor(i))
            i+=1
        return colorCollection
    
    # 根据索引过的顶点位置
    # index:索引
    def GetPosition(self,index=0):
        byteOffset=self.rules['position']['byteOffset']
        position=[]
        position.append(struct.unpack('f',self.geometryBin[byteOffset+0+index*12:byteOffset+4+index*12])[0])
        position.append(struct.unpack('f',self.geometryBin[byteOffset+4+index*12:byteOffset+8+index*12])[0])
        position.append(struct.unpack('f',self.geometryBin[byteOffset+8+index*12:byteOffset+12+index*12])[0]) 
        return position

    # 根据索引获得法线
    # index:索引
    def GetNormal(self,index=0):
        byteOffset=self.rules['normal']['byteOffset']
        normal=[]
        normal.append(struct.unpack('f',self.geometryBin[byteOffset+0+index*12:byteOffset+4+index*12])[0])
        normal.append(struct.unpack('f',self.geometryBin[byteOffset+4+index*12:byteOffset+8+index*12])[0])
        normal.append(struct.unpack('f',self.geometryBin[byteOffset+8+index*12:byteOffset+12+index*12])[0]) 
        return normal
    
    # 根据索引获得UV
    # index:索引
    def GetUV0(self,index=0):
        byteOffset=self.rules['uv0']['byteOffset']
        uv0=[]
        uv0.append(struct.unpack('f',self.geometryBin[byteOffset+0+index*8:byteOffset+4+index*8])[0])
        uv0.append(struct.unpack('f',self.geometryBin[byteOffset+4+index*8:byteOffset+8+index*8])[0])
        return uv0

    # 根据索引获得颜色
    # index:索引 
    def GetColor(self,index=0):
        byteOffset=self.rules['color']['byteOffset']
        color=[]
        color.append(struct.unpack('B',self.geometryBin[byteOffset+0+index*4:byteOffset+1+index*4])[0])
        color.append(struct.unpack('B',self.geometryBin[byteOffset+1+index*4:byteOffset+2+index*4])[0])
        color.append(struct.unpack('B',self.geometryBin[byteOffset+2+index*4:byteOffset+3+index*4])[0]) 
        color.append(struct.unpack('B',self.geometryBin[byteOffset+3+index*4:byteOffset+4+index*4])[0]) 
        return color
    #获得 GetfeaID
    # by xupf
    def GetfeaID(self):
        byteOffset=self.rules['id']['byteOffset']
        feaID=struct.unpack('Q',self.geometryBin[byteOffset:byteOffset+8])[0]
        return feaID
    #获得 GetFaceRange
    #获得面数范围
    # by xupf
    def GetFaceRange(self):
        byteOffset=self.rules['faceRange']['byteOffset']
        FaceRange=(struct.unpack('I',self.geometryBin[byteOffset:byteOffset+4])[0],struct.unpack('L',self.geometryBin[byteOffset+4:byteOffset+8])[0])
        return FaceRange
    #获得 GetVetexNum
    #获得顶点数目
    # by xupf
    def GetVetexNum(self):
        VetexNum=struct.unpack('I',self.geometryBin[0:4])[0]
        return VetexNum
          
    #获得 featureCount
    #获得要素数目
    # by xupf
    def GetfeatureCount(self):
        featureCount=struct.unpack('I',self.geometryBin[4:8])[0]
        return featureCount
    def getRegion(self):
        byteOffset=self.rules['region']['byteOffset']
        region=(struct.unpack('H',self.geometryBin[byteOffset:byteOffset+2])[0],struct.unpack('H',self.geometryBin[byteOffset+2:byteOffset+4])[0],struct.unpack('H',self.geometryBin[byteOffset+4:byteOffset+6])[0],struct.unpack('H',self.geometryBin[byteOffset+6:byteOffset+8])[0])
        return region
    #设置顶点数目
    # by xupf
    def SetVetexNum(self,num):
        VetexNum=struct.pack('I',num)
        self.geometryBin=VetexNum+self.geometryBin[4:]
    # 根据索引设置位置
    # index：索引
    # X,Y,Z位置坐标
    def SetPosition(self,Verticals):
        byteOffset=self.rules['position']['byteOffset']
        # value=struct.pack('f',X)+struct.pack('f',Y)+struct.pack('f',Z)
        value=bytes()
        for v in Verticals:
            value+=struct.pack('f',v)
        self.geometryBin=self.geometryBin[0:byteOffset]+value+self.geometryBin[byteOffset+len(Verticals)*4:]
    # 根据索引设置位置
    # index：索引
    # num表示顶点数目
    # by xupf 删除几何点的保存算法
    def SetPosition1(self,Verticals,normals,uvs,colors,num):
        # try:
        #     byteOffset=self.rules['region']['byteOffset']
        # except:
        #     byteOffset=None
        # value=struct.pack('f',X)+struct.pack('f',Y)+struct.pack('f',Z)
        value=bytes()
        for v in Verticals:
            value+=struct.pack('f',v)
        for n in normals:
            value+=struct.pack('f',n)
        for u in uvs:
            value+=struct.pack('f',u)
        for c in colors:
            value+=struct.pack('B',c)
        newNum=struct.pack('I',num)
        # if byteOffset:
        self.geometryBin=newNum+struct.pack('I',1)+value+struct.pack('Q',1)+struct.pack('I',0)+struct.pack('I',int(num/3)-1)

    # 根据索引设置法线
    # index:索引
    # X,Y,Z 法线
    def SetNormal(self,index,X,Y,Z):
        byteOffset=self.rules['normal']['byteOffset']
        value=struct.pack('f',X)+struct.pack('f',Y)+struct.pack('f',Z)
        self.geometryBin=self.geometryBin[0:byteOffset+index*12]+value+self.geometryBin[byteOffset+12+index*12:]
    #设置新的法线
    #by xupf
    def SetNormal1(self,normals):
        byteOffset=self.rules['normal']['byteOffset']
        value=bytes()
        for n in normals:
            value+=struct.pack('f',n)
        self.geometryBin=self.geometryBin[0:byteOffset]+value+self.geometryBin[byteOffset+len(normals)*4:]
    # 根据索引设置UV
    # index:索引
    # UV坐标 
    def SetUV0(self,index,U,V):
        byteOffset=self.rules['uv0']['byteOffset']
        value=struct.pack('f',U)+struct.pack('f',V)
        self.geometryBin= self.geometryBin[0:byteOffset+index*8]+value+ self.geometryBin[byteOffset+8+index*8:]
    #设置新的Uv
    #by xupf
    def SetUV1(self,uv):
        byteOffset=self.rules['uv0']['byteOffset']
        value=bytes()
        for u in uv:
            value+=struct.pack('f',u)
        self.geometryBin= self.geometryBin[0:byteOffset]+value+ self.geometryBin[byteOffset+len(uv)*4:]
    # 根据索引设置颜色
    # index:索引
    # RGBA   
    def SetColor(self,index,R,G,B,A):
        byteOffset=self.rules['color']['byteOffset']
        value=struct.pack('B',R)+struct.pack('B',G)+struct.pack('B',B)+struct.pack('B',A)
        self.geometryBin=self.geometryBin[0:byteOffset+index*4]+value+self.geometryBin[byteOffset+4+index*4:]
    #更新颜色的另一种方法
    # 更新by xupf
    def SetColor1(self,colors):
        byteOffset=self.rules['color']['byteOffset']
        value=bytes()
        for c in colors:
            value+=struct.pack('B',int(c))
        self.geometryBin=self.geometryBin[0:byteOffset]+value+self.geometryBin[byteOffset+len(colors):]    
    # 根据索引获得顶点
    # index:顶点索引
    # def GetVertexformIndex(self,Index=0):
    #     v= Vertex()
    #     v.position=self.GetPosition(Index)
    #     v.normal=self.GetNormal(Index)
    #     v.uv0=self.GetUV0(Index)
    #     aa=self.GetColor(Index)
    #     v.color=self.GetColor(Index)
    #     v.index=Index
    #     return v

    # 根据设置顶点
    # vertex ：顶点
    # def SetVertex(self,Vertex):
    #     self.SetPosition(Vertex.index,Vertex.position[0],Vertex.position[1],Vertex.position[2])
    #     self.SetNormal(Vertex.index,Vertex.normal[0],Vertex.normal[1],Vertex.normal[2])
    #     self.SetUV0(Vertex.index,Vertex.uv0[0],Vertex.uv0[1])
    #     self.SetColor(Vertex.index,Vertex.color[0],Vertex.color[1],Vertex.color[2],Vertex.color[3])
 
    # 保存更新到gz压缩包
    def SaveBinToGZ(self): 
        with gzip.open(self.filePath,'wb') as wf:
            wf.write(self.geometryBin)
            wf.close()
#created by xupf
#just for osgb convert to slpk
#time 20190603
class OSGBGeometry:
    """该类主要进行处理osgb转的slpk数据中的geometry"""
    def __init__(self,filepath):
        self.filepath=filepath
        geometryFile=gzip.open(self.filepath,'rb')
        self.geometryBin=geometryFile.read()
        geometryFile.close()
        #得到顶点计数
        self.vertexCount=struct.unpack('I',self.geometryBin[0:4])[0]
        # 初始化位置，法线，UV,颜色
    # def Init(self, parameter_list):
    #     self.positionCollection=self.GetPositions()
    #     self.normalCollection=self.GetPosition()
    #     self.uv0Collection=self.GetPosition()
    #     self.colorCollection=self.GetPosition()

    # 获得所有的顶点位置
    def GetPositions(self):
        count=self.vertexCount
        i=0
        positionCollection=[]
        while (i<count):
            positionCollection.append(self.GetPosition(i))
            i+=1
        return positionCollection

    # 获得所有顶点法线
    def GetNormals(self):
        count=self.vertexCount
        i=0
        normalCollection=[]
        while (i<count):
            normalCollection.append(self.GetNormal(i))
            i+=1
        return normalCollection

    def GetNormals2(self):
        count=self.vertexCount
        normalCollection=self.geometryBin[count*12+8:count*12+8+count*12]
        return normalCollection

    # 获得所有顶点的UV
    def GetUV0s(self):
        count=self.vertexCount
        i=0
        uv0Collection=[]
        while (i<count):
            uv0Collection.append(self.GetUV0(i))
            i+=1
        return uv0Collection

    # 获得所有顶点颜色
    def GetColors(self):
        count=self.vertexCount
        i=0
        colorCollection=[]
        while (i<count):
            colorCollection.append(self.GetColor(i))
            i+=1
        return colorCollection
        # 获得所有顶点颜色
    def GetColors2(self):
        count=self.vertexCount
        colorCollection=self.geometryBin[count*32+8:count*36+8]
        
        return colorCollection
    
    # 根据索引过的顶点位置
    # index:索引
    def GetPosition(self,index=0):
        byteOffset=8
        position=[]
        position.append(struct.unpack('f',self.geometryBin[byteOffset+0+index*12:byteOffset+4+index*12])[0])
        position.append(struct.unpack('f',self.geometryBin[byteOffset+4+index*12:byteOffset+8+index*12])[0])
        position.append(struct.unpack('f',self.geometryBin[byteOffset+8+index*12:byteOffset+12+index*12])[0]) 
        return position

    # 根据索引获得法线
    # index:索引
    def GetNormal(self,index=0):
        byteOffset=8+self.vertexCount*12
        normal=[]
        normal.append(struct.unpack('f',self.geometryBin[byteOffset+0+index*12:byteOffset+4+index*12])[0])
        normal.append(struct.unpack('f',self.geometryBin[byteOffset+4+index*12:byteOffset+8+index*12])[0])
        normal.append(struct.unpack('f',self.geometryBin[byteOffset+8+index*12:byteOffset+12+index*12])[0]) 
        return normal
    
    # 根据索引获得UV
    # index:索引
    def GetUV0(self,index=0):
        byteOffset=8+self.vertexCount*12*2
        uv0=[]
        uv0.append(struct.unpack('f',self.geometryBin[byteOffset+0+index*8:byteOffset+4+index*8])[0])
        uv0.append(struct.unpack('f',self.geometryBin[byteOffset+4+index*8:byteOffset+8+index*8])[0])
        return uv0

    # 根据索引获得颜色
    # index:索引 
    def GetColor(self,index=0):
        byteOffset=8+self.vertexCount*12*2+self.vertexCount*8
        color=[]
        color.append(struct.unpack('B',self.geometryBin[byteOffset+0+index*4:byteOffset+1+index*4])[0])
        color.append(struct.unpack('B',self.geometryBin[byteOffset+1+index*4:byteOffset+2+index*4])[0])
        color.append(struct.unpack('B',self.geometryBin[byteOffset+2+index*4:byteOffset+3+index*4])[0]) 
        color.append(struct.unpack('B',self.geometryBin[byteOffset+3+index*4:byteOffset+4+index*4])[0]) 
        return color
    #获得 GetfeaID
    # by xupf
    def GetfeaID(self):
        feaID=struct.unpack('Q',self.geometryBin[-16:-8])[0]
        return feaID
    #获得 GetFaceRange
    #获得面数范围
    # by xupf
    def GetFaceRange(self):
        FaceRange=(struct.unpack('I',self.geometryBin[-8:-4])[0],struct.unpack('I',self.geometryBin[-4:])[0])
        return FaceRange

          
    #获得 featureCount
    #获得要素数目
    # by xupf
    def GetfeatureCount(self):
        featureCount=struct.unpack('I',self.geometryBin[4:8])[0]
        return featureCount

    #设置顶点数目
    # by xupf
    def SetVetexNum(self,num):
        VetexNum=struct.pack('I',num)
        self.geometryBin=VetexNum+self.geometryBin[4:]
    # 根据索引设置位置
    # index：索引
    # X,Y,Z位置坐标
    def SetPosition(self,Verticals):
        byteOffset=8
        # value=struct.pack('f',X)+struct.pack('f',Y)+struct.pack('f',Z)
        value=bytes()
        for v in Verticals:
            value+=struct.pack('f',v)
        self.geometryBin=self.geometryBin[0:byteOffset]+value+self.geometryBin[byteOffset+len(Verticals)*4:]
    # 根据索引设置位置
    # index：索引
    # num表示顶点数目
    # by xupf 删除几何点的保存算法
    def SetPosition1(self,Verticals,normals,uvs,colors,num):
        # try:
        #     byteOffset=self.rules['region']['byteOffset']
        # except:
        #     byteOffset=None
        # value=struct.pack('f',X)+struct.pack('f',Y)+struct.pack('f',Z)
        value=bytes()
        for v in Verticals:
            value+=struct.pack('f',v)
        for n in normals:
            value+=struct.pack('f',n)
        for u in uvs:
            value+=struct.pack('f',u)
        for c in colors:
            value+=struct.pack('B',c)
        newNum=struct.pack('I',num)
        # if byteOffset:
        self.geometryBin=newNum+struct.pack('I',1)+value+struct.pack('Q',1)+struct.pack('I',0)+struct.pack('I',int(num/3)-1)

    # 根据索引设置法线
    # index:索引
    # X,Y,Z 法线
    def SetNormal(self,index,X,Y,Z):
        byteOffset=8+self.vertexCount*12
        value=struct.pack('f',X)+struct.pack('f',Y)+struct.pack('f',Z)
        self.geometryBin=self.geometryBin[0:byteOffset+index*12]+value+self.geometryBin[byteOffset+12+index*12:]
    #设置新的法线
    #by xupf
    def SetNormal1(self,normals):
        byteOffset=8+self.vertexCount*12
        value=bytes()
        for n in normals:
            value+=struct.pack('f',n)
        self.geometryBin=self.geometryBin[0:byteOffset]+value+self.geometryBin[byteOffset+len(normals)*4:]
    # 根据索引设置UV
    # index:索引
    # UV坐标 
    def SetUV0(self,index,U,V):
        byteOffset=8+self.vertexCount*12*2
        value=struct.pack('f',U)+struct.pack('f',V)
        self.geometryBin= self.geometryBin[0:byteOffset+index*8]+value+ self.geometryBin[byteOffset+8+index*8:]
    #设置新的Uv
    #by xupf
    def SetUV1(self,uv):
        byteOffset=8+self.vertexCount*12*2
        value=bytes()
        for u in uv:
            value+=struct.pack('f',u)
        self.geometryBin= self.geometryBin[0:byteOffset]+value+ self.geometryBin[byteOffset+len(uv)*4:]
    # 根据索引设置颜色
    # index:索引
    # RGBA   
    def SetColor(self,index,R,G,B,A):
        byteOffset=8+self.vertexCount*12*2+self.vertexCount*8
        value=struct.pack('B',R)+struct.pack('B',G)+struct.pack('B',B)+struct.pack('B',A)
        self.geometryBin=self.geometryBin[0:byteOffset+index*4]+value+self.geometryBin[byteOffset+4+index*4:]
    #更新颜色的另一种方法
    # 更新by xupf
    def SetColor1(self,colors):
        byteOffset=8+self.vertexCount*12*2+self.vertexCount*8
        value=bytes()
        for c in colors:
            value+=struct.pack('B',int(c))
        self.geometryBin=self.geometryBin[0:byteOffset]+value+self.geometryBin[byteOffset+len(colors):]    
    
    # 保存更新到gz压缩包
    def SaveBinToGZ(self): 
        with gzip.open(self.filepath,'wb') as wf:
            wf.write(self.geometryBin)
            wf.close()
# 顶点类
# 顶点类文件路径
# create by xp dt:20180802 
class Vertex:
    def __init__(self):
        self.position=[]
        self.normal=[]
        self.uv0=[]
        self.color=[]
        self.index=-1

# 着色器类
# 着色器类文件路径
# create by xp dt:20180802 
class Shared():
    def __init__(self,FilePath):
        self.filePath=FilePath
        SharedFile=gzip.open(self.filePath,'rb')
        file_content=SharedFile.read()
        self.SharedFileJson=json.loads(file_content)
        SharedFile.close()

    
    def SaveJsonToGZ(self):
        """保存到压缩包"""
        saveJson=json.dumps(self.SharedFileJson)
        SharedFile=gzip.open(self.filePath,'wb')
        SharedFile.write(saveJson)
        SharedFile.close()
