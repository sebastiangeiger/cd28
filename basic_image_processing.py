import code
import cv2
import sys
import numpy as np
import fnmatch
import os
import re

def process_cd28_image(image_path):
  process = lambda image: shared_processing(image, gaussian_blur_radius = 7)
  read_process_save(image_path, process)

def process_cd8_image(image_path):
  process = lambda image: shared_processing(image, gaussian_blur_radius = 5)
  read_process_save(image_path, process)

def shared_processing(image, gaussian_blur_radius = 7, laplace_kernel_size = 5, threshold = 80, median_blur_radius = 3):
  image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  gaussian = cv2.GaussianBlur(image,(gaussian_blur_radius,gaussian_blur_radius),0)
  laplacian_of_gaussian = cv2.Laplacian(gaussian, cv2.CV_16S, ksize = laplace_kernel_size, scale = 1, delta = 0)
  absolute_values = cv2.convertScaleAbs(laplacian_of_gaussian)
  ret,thresholded = cv2.threshold(absolute_values,threshold,255,cv2.THRESH_BINARY)
  median = cv2.medianBlur(thresholded,median_blur_radius)
  return thresholded, median

def read_process_save(image_path, process):
  thresholded, median = process(cv2.imread(image_path))
  without_extension = os.path.splitext(image_path)[0]
  cv2.imwrite(without_extension + ' thresholded.png', thresholded)
  cv2.imwrite(without_extension + ' median.png', median)

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
    for filename in filenames:
      matches.append(os.path.join(root, filename))
  return matches

if  __name__ =='__main__':
  main()
