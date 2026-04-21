import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import label,regionprops
from skimage.io import imread
from skimage.color import rgb2hsv

image=imread("balls_and_rects.png")
hsv=rgb2hsv(image)
h=hsv[:,:,0]

result={}
count_fig=0
for color in np.unique(h):
    if color==0: continue

    binary=h==color
    labeled=label(binary)
    regions=regionprops(labeled)

    if not regions:
        continue

    attention=round(color,2)
    if attention not in result:
        result[attention]={"rect":0,"circles":0}

    for region in regions:
        count_fig+=1
        if region.extent>0.85:
            result[attention]['rect']+=1
        else:
            result[attention]['circles']+=1

print(f"Фигур всего: {count_fig}")
for attention,counts in result.items():
    print(f"Оттенок: {attention}")
    print(f"    Прямугольники: {counts['rect']}")
    print(f"    Круги: {counts['circles']}\n") 