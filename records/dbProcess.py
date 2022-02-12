

import csv
import os
from pathlib import Path


def save(type, data):
    TXT_PATH = os.path.join(os.getcwd(), '../records/'+type+'Db.csv')
    print("saving in ", TXT_PATH)
    
    with open(TXT_PATH, "w") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(data.keys())
        writer.writerows(zip(*data.values()))
    

def read(type): 
    
    TXT_PATH = os.path.join(os.getcwd(), '../records/'+type+'Db.csv')
    print(TXT_PATH)
    reader = 0
    with open(TXT_PATH, "r") as readfile:
        reader = csv.reader(readfile)
        
    return reader.line_num
