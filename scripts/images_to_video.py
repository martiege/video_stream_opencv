#! /usr/bin/env python2
# -*- coding: utf-8 -*-
"""

Copyright (c) 2020 NTNU Cybernetics.
Released under the BSD License.

Created on 4/13/20

@author: Martin Eek Gerhardsen

images_to_video.py contains
a testing code to see if opencv can open a video stream
useful to debug if video_stream does not work
"""

import cv2
import sys
import glob 


def dataset_to_video(image_path, video_path, fps=24):
    img_array = []
    image_path = image_path.strip()
    if image_path[-1] != '/':
        image_path += '/'
    for filename in sorted(glob.glob(image_path + "*.png")):
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width,height)
        img_array.append(img)
    
    
    out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'MP4V'), fps, size)
    
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()


if __name__ == "__main__":


    img_path = sys.argv[1] # "/home/martin/Downloads/rgbd_dataset_freiburg1_desk/rgb"
    vid_path = sys.argv[2] # "/home/martin/Downloads/rgbd_dataset_freiburg1_desk/vid.mp4"
    print "Converting dataset to video"
    dataset_to_video(img_path, vid_path, 30)