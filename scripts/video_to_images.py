#! /usr/bin/env python2
# -*- coding: utf-8 -*-
"""

Copyright (c) 2020 NTNU Institute of Cybernetics.
Released under the BSD License.

Created on 4/13/20

@author: Amund Fjøsne and Martin Eek Gerhardsen

images_to_video.py contains
code to convert a video into a directory of image sequences.
"""

import os
import cv2
import sys
import argparse


def video_to_images(output_path, image_folder, timestamp_file, video_path, file_type, start_frame = 0, end_frame = -1, fps = 30.0, start_time = 0.0, verbose = False):
    vidcap = cv2.VideoCapture(video_path)
    vidcap.set(2, start_frame)
    success,image = vidcap.read()
    count = 0
    if verbose: 
        print 'Output path ' + output_path
        print 'Image folder ' + image_folder 
        print 'Timestamp file ' + timestamp_file
        print 'Video path ' + video_path 
        print 'File type ' + file_type 
        print 'Start frame ' + str(start_frame)
        print 'End frame ' + str(end_frame)
        print 'FPS ' + str(fps)
        print '\n'

    f = open(output_path + timestamp_file, 'w+')
    if verbose:
        print 'File opened'
    f.write('# timestamp filename\n')   
    if not os.path.exists(output_path + image_folder):
        if verbose:
            print 'Creating image directory'
        os.makedirs(output_path + image_folder)
    else:
        if verbose:
            print 'Image directory already existed'
    
    for element in os.listdir(output_path + image_folder):
        if verbose: 
            print 'Removing existing file: ' + element
        os.remove(os.path.join(output_path + image_folder, element))
 
    while success:
        image_path = output_path  + image_folder + '/frame' + str(count) + file_type
        if verbose: 
            print 'Current image path: ' + image_path
        timestamp = start_time + count/fps 

        f.write(str(timestamp) + ' ' + image_path + '\n')
        cv2.imwrite(image_path, image)

        success,image = vidcap.read()
        if verbose:
            print 'Read frame ' + str(count) + ' success: ' + str(success)
        count += 1
        if count == end_frame:
            break

    f.close()

    if verbose:
        print 'File closed'


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Converting a video into a directory of image sequences.")
    parser.add_argument("-i", "--image_folder", default="rgb", help="The name of the folder the images are to be placed in (inside output_path)")
    parser.add_argument("-t", "--timestamp_file", default="rgb.txt", help="The name of the file of timestamps")
    parser.add_argument("-s", "--start_frame", default=0, help="The starting frame of the video sequence (useful to skip starting part of video)")
    parser.add_argument("-e", "--end_frame", default=-1, help="The ending frame of the video sequence (useful to skip ending part of video)")
    parser.add_argument("--fps", default=30.0, help="The desired FPS (frames per second) of the input video (to give correct timestamps)")
    parser.add_argument("-f", "--file_type", default=".png", help="The filetype of the output images")
    parser.add_argument("-S", "--start_time", default=0.0, help="The starting time for the image sequence (useful if you need a specific starting time for the timestamps)")
    parser.add_argument("--verbose", action='store_true', help="Print some useful information")

    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument("-o", "--output_path", required=True, help="The path of the directory where the timestamps and directory of images are placed")
    requiredNamed.add_argument("-v", "--video_path",  required=True, help="The path of the video file which is to be converted to a directory of images")
    args = parser.parse_args()

    file_type   = args.file_type
    img_folder  = args.image_folder
    ts_file     = args.timestamp_file
    s_frame     = args.start_frame
    e_frame     = args.end_frame
    fps         = args.fps
    s_time      = args.start_time
    verbose     = args.verbose

    out_path    = args.output_path # "/home/martin/video_stream_opencv/test/"
    vid_path    = args.video_path  # "/home/martin/video_stream_opencv/test/small.mp4"

    out_path = out_path.strip()
    if out_path[-1] != '/':
        out_path += '/'
    vid_path = vid_path.strip()
    if vid_path[-4:] != '.mp4':
        print 'Only .mp4 files allowed! This is ' + vid_path[-4:]
        exit(0)
    file_type = file_type.strip()
    if file_type[0] != ".":
        file_type = "." + file_type
    ts_file = ts_file.strip()
    if ts_file[-4:] != ".txt":
        ts_file += ".txt"
    if s_time < 0.0: 
        s_time = 0.0
    if s_frame < 0: 
        s_frame = 0 
    if e_frame < 0:
        e_frame = -1

    video_to_images(out_path, img_folder, ts_file, vid_path, file_type, s_frame, e_frame, fps, s_time, verbose)
