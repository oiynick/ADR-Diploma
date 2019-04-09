import numpy as np
import struct
from PIL import Image, ImageOps

# Read the file (the file has been renamed)
with open('input.raw16', 'rb') as file:
    fileContent = file.read()

# Make data-array
data = []
for data1 in struct.iter_unpack("<H", fileContent):
    data += data1

# Creating data array, no key-words is needed
bands = np.zeros((543, 2048, 5), 'uint16')
it = np.nditer(bands, flags=['multi_index'], op_flags=['readwrite'])

for i in it:
    i[...] = data[it.multi_index[0]*11090 + 751 + it.multi_index[2] + it.multi_index[1]*5]/4

# Creating image un RGB
RGB = np.zeros((543, 2048, 3), 'uint8')

RGB[..., 0] = bands[:, :, 3]
RGB[..., 1] = bands[:, :, 4]
RGB[..., 2] = bands[:, :, 5]
image = Image.fromarray(RGB, 'RGB')

# Enhance the image and show it
enh_img = ImageOps.equalize(image)   # Histogram
enh_img = ImageOps.autocontrast(enh_img)  # Adjust contrast

enh_img.show()
