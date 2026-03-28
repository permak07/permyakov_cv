import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import label, regionprops
import os

def distance(dot1,dot2):
    return (((dot1[0]-dot2[0])**2 + (dot1[1] - dot2[1])**2)**0.5)

folder = 'out/'
files = sorted(os.listdir(folder), key=lambda x: int(''.join(filter(str.isdigit, x))))


dots=[]

for filename in files:
    if filename.endswith('.npy'):
        img = np.load(folder + filename)
        labeled = label(img)
        props = regionprops(labeled)
        cur_dots=[]
        for p in props:
            yc, xc = p.centroid
            cur_dots.append((xc,yc))
        dots.append(cur_dots)

figures=[]
for cur_dots in dots:
    for dot in cur_dots:
        check=False
        for figure in figures:
            last_figure=figure[-1]
            dist=distance(dot,last_figure)
            if dist<50:
                figure.append(dot)
                check=True
                break
        if not check:
            figures.append([dot])
    

plt.figure(figsize=(8, 8))
for figure in figures:
    x=[dot[0] for dot in figure]
    y=[dot[1] for dot in figure]
    plt.plot(x, y, marker='o', color='blue', linewidth=1, alpha=0.5)
plt.title("Траектория объектов")
plt.xlabel("X координата")
plt.ylabel("Y координата")
plt.grid()
plt.show()