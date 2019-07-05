import sys
import os
from PIL import Image
from PIL import ImageDraw
import math
import json

# Author:esrichina xupf


class SourceImage:
    def __init__(self, fullPath, oi):
        self.fullPath =fullPath
        self.origIndex = oi
        # Open the image and make sure it's in RGB mode.
        self.img = Image.open(self.fullPath)
        self.img = self.img.convert('RGB')
        self.uncropped = Rect(0, 0, self.img.size[0]-1, self.img.size[1]-1)
        self.rect = Rect(0, 0, self.img.size[0]-1, self.img.size[1]-1)
        if useBorder:
            self.rect.xmax += 2
            self.rect.ymax += 2


# A simple rect class using inclusive coordinates.
class Rect:
    def __init__(self, x0, y0, x1, y1):
        self.xmin = int(x0)
        self.xmax = int(x1)
        self.ymin = int(y0)
        self.ymax = int(y1)

    def width(self):
        return int(self.xmax - self.xmin + 1)

    def height(self):
        return int(self.ymax - self.ymin + 1)

# A k-d tree node containing rectangles used to tightly pack images.


class Node:
    def __init__(self):
        self.image = None
        self.rect = Rect(0, 0, 0, 0)
        self.child0 = None
        self.child1 = None

    # Iterate the full tree and write the destination rects to the source images.
    def finalize(self):
        if self.image != None:
            self.image.destRect = self.rect
        else:
            if self.child0 != None:
                self.child0.finalize()
            if self.child1 != None:
                self.child1.finalize()

    # Insert a single rect into the tree by recursing into the children.
    def insert(self, r, img):
        if self.child0 != None or self.child1 != None:
            newNode = self.child0.insert(r, img)
            if newNode != None:
                return newNode
            return self.child1.insert(r, img)
        else:
            if self.image != None:
                return None
            if r.width() > self.rect.width() or r.height() > self.rect.height():
                return None
            if r.width() == self.rect.width() and r.height() == self.rect.height():
                self.image = img
                return self
            self.child0 = Node()
            self.child1 = Node()
            dw = self.rect.width() - r.width()
            dh = self.rect.height() - r.height()
            if dw > dh:
                self.child0.rect = Rect(
                    self.rect.xmin, self.rect.ymin, self.rect.xmin + r.width() - 1, self.rect.ymax)
                self.child1.rect = Rect(
                    self.rect.xmin + r.width(), self.rect.ymin, self.rect.xmax, self.rect.ymax)
            else:
                self.child0.rect = Rect(
                    self.rect.xmin, self.rect.ymin, self.rect.xmax, self.rect.ymin + r.height() - 1)
                self.child1.rect = Rect(
                    self.rect.xmin, self.rect.ymin + r.height(), self.rect.xmax, self.rect.ymax)
            return self.child0.insert(r, img)

# An alternate heuristic for insertion order.


def imageArea(i):
    return i.rect.width() * i.rect.height()

# The used heuristic for insertion order, inserting images with the
# largest extent (in any direction) first.


def maxExtent(i):
    return max([i.rect.width(), i.rect.height()])


def writeAtlas(images, atlasW, atlasH,pathTxt):

    atlasImg = Image.new('RGB', [atlasW, atlasH])
    if useBorder:
        draw = ImageDraw.Draw(atlasImg)
        draw.rectangle((0, 0, atlasW, atlasH), fill=borderColor)
        for i in images:
            atlasImg.paste(i.img, [int(i.img.destRect.xmin + 1), int(
                i.img.destRect.ymin + 1), int(i.img.destRect.xmax), int(i.img.destRect.ymax)])
    else:
        for i in images:
            atlasImg.paste(i.img, [int(i.img.destRect.xmin), int(i.img.destRect.ymin), int(
                i.img.destRect.xmax + 1), int(i.img.destRect.ymax + 1)])
    atlasImg.save(pathTxt)
    atlasImg = None
    # img=Image.open(pathTxt)
    # img.resize((256,256),Image.ANTIALIAS)
    # atlasImg.save(pathTxt)
# Remove one pixel on each side of the images before dumping the CSS and JSON info.


def removeBorders(images):
    for i in images:
        i.img.destRect.xmin += 1
        i.img.destRect.ymin += 1
        i.img.destRect.xmax -= 1
        i.img.destRect.ymax -= 1


def writeJSON(images, atlasW, atlasH,atlasBaseName):
    jsonpath=atlasBaseName[:-4] + '.json'
    content={"atlas":atlasBaseName}
    for i in images:
        srcTex=Image.open(i.fullPath)
        myw=srcTex.size[0]
        myh=srcTex.size[1]
        temp={os.path.dirname(os.path.dirname(i.fullPath)):[i.img.destRect.xmin,i.img.destRect.ymin,myw,myh,atlasW,atlasH]}
        content.update(temp)
    with open(jsonpath,'w') as f:
        json.dump(content,f)





def addFolder(folder):
    global originalIndex
    for f in folder:
        images.append(SourceImage(f, originalIndex))
        originalIndex = originalIndex + 1

def NormalizeTex(Texpath):
    img=Image.open(Texpath)
    out = img.resize((1024,1024),Image.ANTIALIAS)
    out.save(Texpath)


# Sort the source images using the insert heuristic.
# images.sort(None,maxExtent)
originalIndex=0
useBorder = False
borderColor = 'red'
images = []

def TexAlats(folder,atlasBaseName1):
    atlasBaseName=os.path.join(atlasBaseName1,'textures','0_0.jpg')
    addFolder(folder)
    totalArea = 0
    totalAreaUncropped = 0
    for i in images:
        totalArea = totalArea + i.rect.width() * i.rect.height()
        totalAreaUncropped = totalAreaUncropped + \
            i.uncropped.width() * i.uncropped.height()
    width = math.floor(math.sqrt(totalArea))
    height = math.floor(totalArea / width)

    # Loop until success.
    while True:
        # Set up an empty tree the size of the expected atlas.
        root = Node()
        root.rect = Rect(0, 0, width, height)
        # Try to insert all the source images.
        ok = True
        for i in images:
            n = root.insert(i.rect, i.img)
            if n == None:
                ok = False
                break
        # If all source images fit break out of the loop.
        if ok:
            break

        # Increase the width or height by one and try again.
        if width > height:
            height = height + 1
        else:
            width = width + 1

    # We've succeeded so write the dest rects to the source images.
    root.finalize()
    root = None

    # Figure out the actual size of the atlas as it may not fill the entire area.
    atlasW = 0
    atlasH = 0
    for i in images:
        atlasW = max([atlasW, i.img.destRect.xmax])
        atlasH = max([atlasH, i.img.destRect.ymax])
    atlasW = int(atlasW+1)
    atlasH = int(atlasH+1)
    print('AtlasDimensions: ' + str(atlasW) + 'x' + str(atlasH) + '  :  ' +
        str(int(100.0 * (atlasW * atlasH)/totalAreaUncropped)) + '% of original')

    writeAtlas(images, atlasW, atlasH,atlasBaseName)
    if useBorder:
        removeBorders(images)
    writeJSON(images, atlasW, atlasH,atlasBaseName)
    NormalizeTex(atlasBaseName)

