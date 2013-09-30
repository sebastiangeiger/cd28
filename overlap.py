import cv2
import numpy as np

def pixelwise_overlap(cd_8_image,cd_28_image):
  cd_8_image = cd_8_image.astype(np.int32)
  cd_28_image = cd_28_image.astype(np.int32)
  assert (np.unique(cd_8_image) == [0, 255]).all(), \
    "Expected the image to only have the values 0 and 255"
  assert (np.unique(cd_28_image) == [0, 255]).all(), \
    "Expected the image to only have the values 0 and 255"
  # Multiplying cd_28_image with 2 yields the values 0 and 510
  # When the two matrices are added up this results in the following:
  # 0: Pixel black in CD8 and in CD28
  # 255: Pixel white in CD8, black in CD28
  # 510: Pixel white in CD28, black in CD8
  # 765: Pixel white in CD8 and CD28
  summed = np.add(cd_8_image, np.multiply(cd_28_image,2))
  hist, bins = np.histogram(summed, bins=[0,127,383,639,895])
  both_black       = hist[0]
  black_28_white_8 = hist[1]
  white_28_black_8 = hist[2]
  both_white       = hist[3]
  total = black_28_white_8 + white_28_black_8 + both_white
  return {
      "in both": float(both_white)/total*100,
      "in cd8 but not in cd28": float(black_28_white_8)/total*100,
      "in cd28 but not in cd8": float(white_28_black_8)/total*100
      }

def just_threshold(image):
  image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  image = cv2.convertScaleAbs(image)
  ret,image = cv2.threshold(image,40,255,cv2.THRESH_BINARY)
  return image

def overlap_test():
  A = just_threshold(cv2.imread("test images/S.tif"))
  B = just_threshold(cv2.imread("test images/B.tif"))
  print determine_overlap(A,B)

if  __name__ =='__main__':
  overlap_test()
