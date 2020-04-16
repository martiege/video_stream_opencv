#! /usr/bin/env python2
# -*- coding: utf-8 -*-
"""

Copyright (c) 2020 NTNU Institute of Cybernetics.
Released under the BSD License.

Created on 4/13/20

@author: Amund Fjøsne and Martin Eek Gerhardsen

images_calibration.py contains
code to convert a video into a directory of image sequences.
Adapted from from https://docs.opencv.org/3.4/dc/dbb/tutorial_py_calibration.html
"""

import glob
import argparse
import cv2 as cv
import numpy as np
try:
    from tqdm import tqdm
except:
    print "Problems getting tqdm, is it installed? Try it for nice progressbar :)" 
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

def calibrate(image_path, file_type, n_c = (7,6), verbose=False, visualise=False):
    # termination criteria
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((n_c[0]*n_c[1],3), np.float32)
    objp[:,:2] = np.mgrid[0:n_c[0],0:n_c[1]].T.reshape(-1,2)
    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.
    images = glob.glob(image_path + '*' + file_type)
    image_count = 0
    image_used_count = 0

    if verbose:
        print "Number of images " + str(len(images))
    with tqdm(total=len(images), desc="Calibrating") as pbar:
        for fname in images:
            img = cv.imread(fname)
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            # Find the chess board corners
            ret, corners = cv.findChessboardCorners(gray, n_c, None)
            # If found, add object points, image points (after refining them)
            image_count += 1
            # if verbose:
            #     print "Img " + str(image_count) + "\t Image " + str(fname) + "\t returned: " + str(ret) + "  \t" + str(round(image_count*100/len(images),2))+"% complete\r"
            if ret:
                image_used_count += 1
                objpoints.append(objp)
                corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
                imgpoints.append(corners)
                # Draw and display the corners
                if visualise:
                    cv.drawChessboardCorners(img, n_c, corners2, ret)
                    cv.imshow('img', img)
                    cv.waitKey(500)
            pbar.update(1)
    if verbose:
        print ''
    cv.destroyAllWindows()
    if verbose:
        print str(image_used_count) + " used in calibration"
    if image_used_count != 0:
        ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
        if verbose:
            print '\n---------- Raw calibration output ----------'
            print "Ret " + str(ret)        # Reprojection error
            print "Mtx " + str(mtx)        # Camera Matrix [fx 0 cx; 0 fy cy; 0 0 1]
            print "Dist " + str(dist)      # Distorion vector (k1, k2, p1, p2, k3)
            print "Rvecs " + str(rvecs)    # Rotation vector 
            print "Tvecs " + str(tvecs)    # Transalation vector

        mean_error = 0
        with tqdm(total=len(objpoints), desc="Measuring errors") as pbar:
            for i in range(len(objpoints)):
                imgpoints2, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
                error = cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2)/len(imgpoints2)
                mean_error += error
                pbar.update(1)
        print '\n---------- Calibration deviation ----------'
        print "Total error: {}".format(mean_error/len(objpoints)) 

        print '\n---------- Formatted calibration output for orbslam yaml ----------'
        print "Camera.fx: " + str(mtx[0][0])
        print "Camera.fy: " + str(mtx[1][1])
        print "Camera.cx: " + str(mtx[0][2])
        print "Camera.cy: " + str(mtx[1][2])

        print "Camera.k1: " + str(dist[0][0])
        print "Camera.k2: " + str(dist[0][1])
        print "Camera.p1: " + str(dist[0][2])
        print "Camera.p2: " + str(dist[0][3])
        print "Camera.k3: " + str(dist[0][4])

        print "mtx: "  + str(mtx)
        print "dist: " + str(dist)
        return mtx,dist
    else:
        print 'Calibration failed'
        return None, None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Using images from a specified folder to calibrate. Very basic calibration implementation. ")
    parser.add_argument("--verbose", action='store_true', help="Print some useful information")
    parser.add_argument("--visualise", action='store_true', help="Show the images used during the calibration")
    parser.add_argument("-f", "--file_type", default=".png", help="The filetype of the input images")

    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument("-i", "--image_path", required=True, help="The path to the folder of the images used for this calibration")
    requiredNamed.add_argument("-c", "--chessboard_corners", nargs=2, required=True, help="A tuple of the internal chessboard corners (so if the chessboard is 10x8 the tuple should be -c 9 7))")
    args = parser.parse_args()

    verbose    = args.verbose 
    visualise  = args.visualise
    file_type  = args.file_type 
    img_path   = args.image_path 
    cb_corners = tuple(int(x) for x in args.chessboard_corners)

    if verbose:
        print "file_type: " + file_type 
        print "image_path: " + img_path 
        print "cb_corners: " + str(cb_corners)

    # "/home/martin/video_stream_opencv/test/rgb/"
    M, v = calibrate(img_path, file_type, cb_corners, verbose=verbose, visualise=visualise)