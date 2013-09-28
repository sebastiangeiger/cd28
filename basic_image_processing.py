import code
import cv2
import sys
import numpy as np
import fnmatch
import os
import re

def process_cd28_image(image_path):
  process = lambda image: shared_processing(image, gaussian_blur_radius = 7)
  return read_process_save(image_path, process)

def process_cd8_image(image_path):
  process = lambda image: shared_processing(image, gaussian_blur_radius = 1)
  return read_process_save(image_path, process)

def shared_processing(image, gaussian_blur_radius = 7, laplace_kernel_size = 5, threshold = 80, median_blur_radius = 3):
  image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  just_thresholded = cv2.convertScaleAbs(image)
  ret,just_thresholded = cv2.threshold(just_thresholded,40,255,cv2.THRESH_BINARY)
  gaussian = cv2.GaussianBlur(image,(gaussian_blur_radius,gaussian_blur_radius),0)
  laplacian_of_gaussian = cv2.Laplacian(gaussian, cv2.CV_16S, ksize = laplace_kernel_size, scale = 1, delta = 0)
  absolute_values = cv2.convertScaleAbs(laplacian_of_gaussian)
  ret,thresholded = cv2.threshold(absolute_values,threshold,255,cv2.THRESH_BINARY)
  median = cv2.medianBlur(thresholded,median_blur_radius)
  return {
      "thresholded": thresholded,
      "median": median,
      "just_thresholded": just_thresholded
      }

def read_process_save(image_path, process):
  if not os.path.isfile(image_path):
    raise Exception(image_path + " is not a file")
  image = cv2.imread(image_path)
  processed_images = process(image)
  without_extension = os.path.splitext(image_path)[0]
  for processing_step, image in processed_images.iteritems():
    cv2.imwrite(without_extension + ' ' + processing_step + '.png', image)
  return processed_images

def main():
  pairs = identify_pairs(sys.argv[1])
  for pair in pairs:
    determine_overlap(process_cd8_image(pair[0]),process_cd28_image(pair[1]))

def determine_overlap(cd_8_images,cd_28_images):
  cd_8_image = cd_8_images["median"].astype(np.int32)
  cd_28_image = cd_28_images["median"].astype(np.int32)
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
  print "Overlap: {0}".format(float(both_white)/total*100)
  print "Positive in CD 8: {0}".format(float(black_28_white_8)/total*100)
  print "Positive in CD 28: {0}".format(float(white_28_black_8)/total*100)

def identify_pairs(folder):
  identifiers = ["CD28","CD8"]
  pairs = []
  for dirpath, dirnames, filenames in os.walk(folder):
    pair = []
    for identifier in identifiers:
      matching_files = [f for f in filenames if identifier in f and f.endswith('.tif') ]
      if len(matching_files) > 0:
        pair.append(os.path.join(dirpath, matching_files[0]))
    if len(pair) == len(identifiers):
      pairs.append(pair)
  return pairs

if  __name__ =='__main__':
  main()
