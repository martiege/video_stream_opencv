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

def calibrate(image_path, file_type, n_frames_max = -1, n_c = (7,6)):
    # termination criteria

    n_c = (7,6) # Number of internal chess board corners

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

    for fname in images:
        img = cv.imread(fname)
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        # Find the chess board corners
        ret, corners = cv.findChessboardCorners(gray, n_c, None)
        # If found, add object points, image points (after refining them)
        image_count += 1
        print("Img " + str(image_count) + "\t Image " + str(fname) + "\t returned: " + str(ret) + "  \t" + str(round(image_count*100/len(images),2))+"% complete", end='\r')
        if ret == True:
            image_used_count += 1
            objpoints.append(objp)
            corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners)
            # Draw and display the corners
            cv.drawChessboardCorners(img, n_c, corners2, ret)
            cv.imshow('img', img)
            cv.waitKey(500)
    print()
    cv.destroyAllWindows()
    print(str(image_used_count) + " used in calibration")
    if image_used_count != 0:
        ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
        print('\n---------- Raw calibration output ----------')
        print("Ret " + str(ret))        # Reprojection error
        print("Mtx " + str(mtx))        # Camera Matrix [fx 0 cx; 0 fy cy; 0 0 1]
        print("Dist " + str(dist))      # Distorion vector (k1, k2, p1, p2, k3)
        print("Rvecs " + str(rvecs))    # Rotation vector 
        print("Tvecs " + str(tvecs))    # Transalation vector

        mean_error = 0
        for i in range(len(objpoints)):
            imgpoints2, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
            error = cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2)/len(imgpoints2)
            mean_error += error
        print('\n---------- Calibration deviation ----------')
        print("Total error: {}".format(mean_error/len(objpoints)) )

        print('\n---------- Formatted calibration output for orbslam yaml ----------')
        print("Camera.fx: " + str(mtx[0][0]))
        print("Camera.fy: " + str(mtx[1][1]))
        print("Camera.cx: " + str(mtx[0][2]))
        print("Camera.cy: " + str(mtx[1][2]))

        print("Camera.k1: " + str(dist[0][0]))
        print("Camera.k2: " + str(dist[0][1]))
        print("Camera.p1: " + str(dist[0][2]))
        print("Camera.p2: " + str(dist[0][3]))
        print("Camera.k3: " + str(dist[0][4]))
        return mtx,dist
    else:
        print('Calibration failed')
        return None, None

if __name__ == "__main__":
    internal_chessboard_corners = (7,6)
    M, v = calibrate(movie = 'IMG_3393.mp4', n_frames_max = 10, n_c = internal_chessboard_corners)