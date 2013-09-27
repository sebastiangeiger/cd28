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
  processed_images = process(cv2.imread(image_path))
  without_extension = os.path.splitext(image_path)[0]
  for processing_step, image in processed_images.iteritems():
    cv2.imwrite(without_extension + ' ' + processing_step + '.png', image)
  return processed_images

def main():
  files = list_of_files(sys.argv[1])
  for file in files:
    basename = os.path.basename(file)
    if basename.endswith(".tif"):
      if "CD28" in basename:
        print "Processing {0} as CD28".format(basename)
        process_cd28_image(file)
      elif "CD8" in basename:
        print "Processing {0} as CD8".format(basename)
        process_cd8_image(file)
      else:
        print "Skipping " + basename
    else:
      print "Skipping " + basename

def list_of_files(folder):
  matches = []
  for root, dirnames, filenames in os.walk(folder):
    filenames = [f for f in filenames if not f[0] == '.']
    dirnames[:] = [d for d in dirnames if not d[0] == '.']
    for filename in filenames:
      matches.append(os.path.join(root, filename))
  return matches

if  __name__ =='__main__':
  main()
