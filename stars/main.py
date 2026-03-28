import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import label
from skimage.morphology import erosion

image=np.load("stars.npy")

labeled=label(image)
count_all=labeled.max()

struct=np.ones((3,3))
square_mask=erosion(image,footprint=struct)

square_labeled=label(square_mask)
count_square=square_labeled.max()

stars_count=count_all-count_square
print(f"Count stars = {stars_count}")
plt.imshow(image)
plt.show()