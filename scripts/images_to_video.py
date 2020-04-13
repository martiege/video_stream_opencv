#! /usr/bin/env python2
# -*- coding: utf-8 -*-
"""

Copyright (c) 2020 NTNU Institute of Cybernetics.
Released under the BSD License.

Created on 4/13/20

@author: Martin Eek Gerhardsen

images_to_video.py contains
code to convert a directory of image sequences into a video.
images are assumed to be named sequentially, such that a sorted 
list of all the paths are compiled into a video. 
"""

import cv2
import sys
import glob 
try:
    from tqdm import tqdm1
except:
    print("Problems getting tqdm, is it installed?")
    class tqdm:
        # Dummy tqdm class
        def __init__(self, iterable=None, desc=None, total=None, leave=True, file=None, ncols=None, mininterval=0.1, maxinterval=10.0, miniters=None, ascii=None, disable=False, unit='it', unit_scale=False, dynamic_ncols=False, smoothing=0.3, bar_format=None, initial=0, position=None, postfix=None, unit_divisor=1000, write_bytes=None, lock_args=None, nrows=None, gui=False, **kwargs):
            self.total = total
            self.current = 0
            self.desc = desc
        
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def update(self, n=1):
            if self.total is not None: 
                self.current += n 
                print "\r" + self.desc + ": " + str(self.current) + "/" + str(self.total), 
                if self.total == self.current: 
                    print ""
            pass 


def dataset_to_video(image_path, file_type, video_path, fps):
    img_array = []
    paths = sorted(glob.glob(image_path + "*" + file_type))
    size = None
    with tqdm(total=len(paths), desc="Loading images") as pbar:
        for i, filename in enumerate(paths):
            img = cv2.imread(filename)
            height, width, layers = img.shape
            size = (width,height)
            img_array.append(img)
            pbar.update(1)
    
    out = cv2.VideoWriter(video_path, 0x00000021, fps, size)
    
    with tqdm(total=len(img_array), desc="Writing images") as pbar:
        for i in range(len(img_array)):
            out.write(img_array[i])
            pbar.update(1)
    out.release()


if __name__ == "__main__":
    print "\n"
    if len(sys.argv) == 3: 
        print "Two arguments given, assuming that the image file type is .png and fps is 30"
        img_path, vid_path = sys.argv[1:]
        file_type = ".png"
        fps = 30

    elif len(sys.argv) == 5: 
        print "Four arguments given"
        img_path, file_type, vid_path, fps = sys.argv[1:]
        fps = int(fps)
    else: 
        print "Needs at least 2 arguments, image_path and video_path. In this case the image file type is assumed .png"
        print "Four arguments can be used, image_path, file_type, video_path, fps"
        print "The image_path argument is the path to the directory containing all the images"
        exit(0)
    
    img_path = img_path.strip()
    if img_path[-1] != '/':
        img_path += '/'
    file_type = file_type.strip()
    if file_type[0] != ".":
        file_type = "." + file_type
    print "Images taken from:"
    print " " + img_path 
    print "Image file type is: " + file_type
    print "Video stored as:"
    print " " + vid_path 
    print "Using %i fps" % (fps)
    print "\n"

    print "Converting dataset to video"
    dataset_to_video(img_path, file_type, vid_path, fps)