#Run Order: 1
#Generate png mask from json
#TODO
# split code to more functions
# change output images name
# change bbox saving to cover a little more space than limited by object border points
import cv2
import numpy as np
import json
import os
from tqdm import tqdm
import time
from shapely.geometry import Point, Polygon
from os.path import exists
import json
#from test import getJSON, path

#Directory with coco images
from utils.utils import getJSON

inputDir="/var/opt/coco/coco-annotator/"
path = '/mnt/datadisk2/data/2022.12.19MaskJsonScripts/' #inputDir''

#Directory where output images will be stored
outputDir='/mnt/datadisk2/data/2022.12.19MasksGenerated/'

mappingFiles = {}
#Create output directory if not exist
if not os.path.isdir(outputDir) and outputDir:
    os.mkdir(outputDir)
    print("[Log] Successfully created the directory")



#convert array of coordinates to array of points
#[x1, y1, x2, y2...] to [(x1,y1), (x2,y2)...]
def chunks(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]

#return bbox coordinates based on annotation points
def bb_box(points):
    points = np.array(points, dtype=np.int32)
    x_values=points[0::2]
    y_values=points[1::2]
    x_1=min(x_values)
    x_2=max(x_values)
    y_1=min(y_values)
    y_2=max(y_values)
    return int(x_1), int(x_2), int(y_1), int(y_2)

jsonList=getJSON(path)
for jsonFile in tqdm(jsonList):
    with open(jsonFile, encoding='utf-8') as f:
      data = json.load(f)
    print(jsonFile)

#iterate through each annotation
    for y in tqdm(range(0,len(data['annotations']))):
        isApproved = False;

        categoryId = data['annotations'][y]['category_id']
        if(categoryId == 13):
            with open(os.path.join(outputDir, 'ApprovedFiles.txt'), 'a') as convert_file:
                convert_file.write( str(data['annotations'][y]['image_id']) + '\r\n')

        photo_id = data['annotations'][y]['image_id']
        bbox=np.array([])
        #search for image with include current annotation
        for z in range(0, len(data['images'])):
            if data['images'][z]['id']== photo_id:
                imagePath = data['images'][z]['path']
                image=None
                try:
                    image = cv2.imdecode(np.fromfile(inputDir+data['images'][z]['path'], dtype=np.uint8), -1)
                    mappingFiles [photo_id] = imagePath
                except:
                    print("[Error] File {} not found".format((data['images'][z]['path'])))
                #create white mask with shape same as input image
                try:
                    mask = np.ones(image.shape, dtype=np.uint8)
                    mask.fill(255)
                except:
                    continue
                break



        for x in data['annotations'][y]['segmentation']:


            #check if photo was found, If not skip
            if image is None:
                print("[Warning] File " + inputDir+data['images'][z]['path'] + " not found, skipping")
                break
            else:
                #checking if annotation polygon is full or empty inside using negation
                roi = None
                for a in data['annotations'][y]['segmentation']:
                    #check if we check all higher polygons in hierarchy
                    if np.array_equal(x, a):
                        if roi == None:
                            roi= True
                        break
                    points = chunks(a, 2)
                    points = np.array(points, dtype=np.int32)
                    try:
                        poly = Polygon(points)
                        pp=Point(x[0], x[1])
                        #check if current polygon is inside higher rank polygon
                        # polygon inside full polygon is empty inside
                        # polygin inside empty polygon is full inside
                        if (pp.within(poly)):
                            if roi == None:
                                roi= False
                            else:
                                roi = not roi
                        if roi == None:
                            roi=True
                    except:
                        print(points)

                points = chunks(x, 2)
                points = np.array(points, dtype=np.int32)

                #if polygon is empty fill it with white color, otherwise black
                if roi == True:
                    cv2.fillPoly(mask, np.array([points]), 0)
                else:
                    cv2.fillPoly(mask, np.array([points]), (255,255,255))
                #sum all points of specific coco object
                bbox=np.concatenate((bbox, x))
        #calculate bbox coordinates
        try:
            x_1, x_2, y_1, y_2=bb_box(bbox)
        except:
            asdf = 10;
            continue

        #apply mask to an image
        #image=cv2.bitwise_or(image, mask)
        #mask=cv2.bitwise_not(mask)
        #save image
        #for y in range(0,len(data['annotations'])):
        #photo_id = data['annotations'][y]['image_id']


        #categoryId = data['annotations'][y]['category_id']
        maskPath = outputDir +"/Mask2/"+str(data['annotations'][y]['image_id'])+"_"+str(data['annotations'][y]['category_id'])+"_"+str(y)+".png"

        if(exists(maskPath) == False):
            cv2.imwrite(maskPath, mask)
            print(maskPath)
        else:
            print("Exists: " + maskPath)

        pngFileName = outputDir + "/Image2/" + str(data['annotations'][y]['image_id']) + ".png"
        jpgFileName = outputDir + "/Image2/" + str(data['annotations'][y]['image_id']) + ".jpg"
        if(exists(pngFileName) == False):
            cv2.imwrite(pngFileName, image)

           # print("[Log] Saving: " + data['images'][z]['file_name'])

        if (exists(jpgFileName) == False):
            cv2.imwrite(jpgFileName, image)

    with open('mappingFiles.txt', 'w') as convert_file:
        convert_file.write(json.dumps(mappingFiles))

