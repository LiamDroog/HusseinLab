# video grab test
import numpy as np
from PIL import Image
import cv2
import matplotlib.pyplot as plt


# image = cv2.imread('opencv_frame_0.png')
# cv2.imshow('image', image)

# image = Image.open('opencv_frame_0.png')
# image.show()
# data = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# cv2.imshow('bw', data)
# cv2.waitKey(0)
# meanarray = []
# for i in range(len(data[0])):
#     sum = 0
#     for j in range(len(data)):
#         sum += data[j][i]
#     meanarray.append(sum / len(data))
#
# plt.plot(meanarray)
# plt.show()
# cam = cv2.VideoCapture(0)
#
# cv2.namedWindow("test")
#
# img_counter = 0

# while True:
#     ret, frame = cam.read()
#     if not ret:
#         print("failed to grab frame")
#         break
#     cv2.imshow("test", frame)
#
#     k = cv2.waitKey(1)
#     if k%256 == 27:
#         # ESC pressed
#         print("Escape hit, closing...")
#         break
#     elif k%256 == 32:
#         # SPACE pressed
#         img_name = "opencv_frame_{}.png".format(img_counter)
#         cv2.imwrite(img_name, frame)
#         print("{} written!".format(img_name))
#         img_counter += 1
#
# cam.release()
#
# cv2.destroyAllWindows()

data = np.loadtxt('h5files/SpectralDat.txt', dtype=float)
print(data.shape)
x = data[:,0]
y = data[:,1]
plt.plot(x, y)
plt.show()


