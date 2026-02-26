import numpy as np
import matplotlib.pyplot as plt

def lerp(v0, v1, t):
    return (1 - t) * v0 + t * v1

size = 100
image = np.zeros((size, size, 3), dtype="uint8")
assert image.shape[0] == image.shape[1]

color1 = [255, 128, 0]
color2 = [0, 128, 255]

for i in range(size):
    j=np.arange(size)
    v=(i+j)/(2*(size-1))

    r = lerp(color1[0], color2[0], v)
    g = lerp(color1[1], color2[1], v)
    b = lerp(color1[2], color2[2], v)

    image[i, :, 0] = r
    image[i, :, 1] = g
    image[i, :, 2] = b

plt.figure(1)
plt.imshow(image)
plt.show()