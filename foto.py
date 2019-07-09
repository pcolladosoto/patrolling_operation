#!/usr/bin/python2

import cv2, os, fnmatch

def foto(w_res, h_res):
	camara = 0
	fotogramas = 1
	camera = cv2.VideoCapture(camara)
	camera.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, w_res)
	camera.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, h_res)
	for i in xrange(fotogramas):
		temp = camera.read()
	retval, camera_capture = camera.read()
	archivos = len(fnmatch.filter(os.listdir("/home/lola/Documents/libvot/Pedro/capturas"),'*.jpg'))
	#archivos = len(os.walk("./Pedro/capturas").next()[2])
	file_ = "/home/lola/Documents/libvot/Pedro/capturas/captura%d.jpg" % archivos
	cv2.imwrite(file_, camera_capture)
	#cv2.imshow('img',camera_capture)
	del(camera)
	file2 = "/home/lola/Documents/libvot/Pedro/capturas/captura%d.jpg" % archivos
	return file2
