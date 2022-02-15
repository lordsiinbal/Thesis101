from pycocotools.coco import COCO
import requests
import os.path
import csv

   
# instantiate COCO specifying the annotations json path
coco = COCO('Annotations/instances_train2017.json')
# Specify a list of category names of interest
classes = 'truck'
catIds = coco.getCatIds(catNms=[classes])
# Get the corresponding image ids and images using loadImgs
imgIds = coco.getImgIds(catIds=catIds)
images = coco.loadImgs(imgIds)
length = len(imgIds)
print(length, " number of images")

# Save the images into a local folder
ctr = 0
for im in images:
    # check if file already exist
   
    if os.path.isfile('dataset/vehicles/'+im['file_name']):
        length -=1
        continue
    
    print(ctr,"/",length," downloading..", im['file_name'])
    img_data = requests.get(im['coco_url']).content
    with open('dataset/vehicles/' + im['file_name'], 'wb') as handler:
        handler.write(img_data)
    ctr += 1

with open('Annotations/annotations_download_' + classes + '.csv', mode='w', newline='') as annot:
    for im in images:
        annIds = coco.getAnnIds(imgIds=im['id'], catIds=catIds, iscrowd=None)
        anns = coco.loadAnns(annIds)
        for i in range(len(anns)):
            annot_writer = csv.writer(annot)
            #annot_writer.writerow([im['coco_url'], anns[i]['bbox'][0], anns[i]['bbox'][1], anns[i]['bbox'][0] + anns[i]['bbox'][2], anns[i]['bbox'][1] + anns[i]['bbox'][3], classes])
            annot_writer.writerow(['downloaded_images/' + im['file_name'], int(round(anns[i]['bbox'][0])), int(round(anns[i]['bbox'][1])), int(round(anns[i]['bbox'][0] + anns[i]['bbox'][2])), int(round(anns[i]['bbox'][1] + anns[i]['bbox'][3])), classes])
            #print("anns: ", im['coco_url'], anns[i]['bbox'][0], anns[i]['bbox'][1], anns[i]['bbox'][0] + anns[i]['bbox'][2], anns[i]['bbox'][1] + anns[i]['bbox'][3], 'person')
    annot.close()
    
print("Done..")