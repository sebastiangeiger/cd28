import code
import cv2
import sys
import numpy as np
import fnmatch
import os
import re
import csv
import overlap

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
  accumulated = {}
  for pair in pairs:
    overlaps = overlap.pearson_overlap(process_cd8_image(pair[0])["median"],
        process_cd28_image(pair[1])["median"])
    accumulated[pair[0]] = overlaps
  save_analysis(accumulated)

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

def save_analysis(results):
  with open('analysis.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='"',
        quoting=csv.QUOTE_MINIMAL)
    result_categories = results[results.keys()[0]].keys()
    writer.writerow(['filename']+result_categories)
    for file_name, result_for_file in results.iteritems():
      row = [file_name]
      for category in result_categories:
        row.append(result_for_file[category])
      writer.writerow(row)

if  __name__ =='__main__':
  main()
