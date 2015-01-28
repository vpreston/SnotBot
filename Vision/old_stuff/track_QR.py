#Code used to identify a target, and roughly estimate the 3D and rotational coordinates of that target, in an attempt to build vision code for docking the vehicle

#May be adapted for use in 'interesting thing' identification and tracking

import cv2
import pickle
import numpy as np
from math import pi, cos, sin, ceil


#TODO: Identify Clusters of Objects, and Focus on Movement Velocities

class QRTracker:

	""" Object Tracker shows the basics of tracking an object based on keypoints """
	def __init__(self, descriptor_name):
		self.detector = cv2.FeatureDetector_create(descriptor_name)
		self.extractor = cv2.DescriptorExtractor_create(descriptor_name)
		self.matcher = cv2.BFMatcher()
		self.query_img = None
		self.query_roi = None
		self.last_detection = None

		self.corner_threshold = 0.0
		self.ratio_threshold = 1.0


	def set_ratio_threshold(self,thresh):
		self.ratio_threshold = thresh

	def set_corner_threshold(self,thresh):
		self.corner_threshold = thresh

	def get_query_keypoints(self):
		query_img_bw = cv2.cvtColor(self.query_img,cv2.COLOR_BGR2GRAY)
		kp = self.detector.detect(query_img_bw)
		kp = [pt
			  for pt in kp if (pt.response > self.corner_threshold and
							   self.query_roi[0] <= pt.pt[0] < self.query_roi[2] and
							   self.query_roi[1] <= pt.pt[1] < self.query_roi[3])]
		dc, des = self.extractor.compute(query_img_bw,kp)
		# remap keypoints so they are relative to the query ROI
		for pt in kp:
			pt.pt = (pt.pt[0] - self.query_roi[0], pt.pt[1] - self.query_roi[1])
		self.query_keypoints = kp
		self.query_descriptors = des

	def track(self,im):
		im_bw = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
		training_keypoints = self.detector.detect(im_bw)

		dc, training_descriptors = self.extractor.compute(im_bw,training_keypoints)

		matches = self.matcher.knnMatch(self.query_descriptors,training_descriptors,k=2)
		good_matches = []
		for m,n in matches:
			# make sure the distance to the closest match is sufficiently better than the second closest
			if (m.distance < self.ratio_threshold*n.distance and
				training_keypoints[m.trainIdx].response > self.corner_threshold):
				good_matches.append((m.queryIdx, m.trainIdx))

		self.matching_query_pts = np.zeros((len(good_matches),2))
		self.matching_training_pts = np.zeros((len(good_matches),2))

		track_im = np.zeros(im_bw.shape)
		for idx in range(len(good_matches)):
			match = good_matches[idx]
			self.matching_query_pts[idx,:] = self.query_keypoints[match[0]].pt
			self.matching_training_pts[idx,:] = training_keypoints[match[1]].pt
			track_im[training_keypoints[match[1]].pt[1],training_keypoints[match[1]].pt[0]] = 1.0

		track_im_visualize = track_im.copy()

		# convert to (x,y,w,h)
		track_roi = (self.last_detection[0],self.last_detection[1],self.last_detection[2]-self.last_detection[0],self.last_detection[3]-self.last_detection[1])

		# Setup the termination criteria, either 10 iteration or move by atleast 1 pt
		# this is done to plot intermediate results of mean shift
		box = None
		for max_iter in range(1,10):
			term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, max_iter, 1 )
			(ret, intermediate_roi) = cv2.CamShift(track_im,track_roi,term_crit)
			if max(intermediate_roi) == 0.0 or np.isnan(ret[0]).any() or np.isnan(ret[1]).any() or np.isnan(ret[2]).any():
				# expand ROI
				track_roi = (int(track_roi[0]),int(track_roi[1]),int(ceil(track_roi[2]*1.2)),int(ceil(track_roi[3]*1.2)))
			else:
				box = cv2.cv.BoxPoints(ret)
				box = np.int0(box)
				cv2.drawContours(track_im_visualize,[box],0,max_iter/10.0,2)

		if box == None:
			self.last_detection = [0,0,frame.shape[0],frame.shape[1]]
		else:
			self.last_detection = [intermediate_roi[0],intermediate_roi[1],intermediate_roi[0]+intermediate_roi[2],intermediate_roi[1]+intermediate_roi[3]]
			self.last_box = box

		cv2.imshow("track_win",track_im_visualize)

def set_corner_threshold_callback(thresh):
	""" Sets the threshold to consider an interest point a corner.  The higher the value
		the more the point must look like a corner to be considered """
	tracker.set_corner_threshold(thresh/1000.0)

def set_ratio_threshold_callback(ratio):
	""" Sets the ratio of the nearest to the second nearest neighbor to consider the match a good one """
	tracker.set_ratio_threshold(ratio/100.0)

def mouse_event(event,x,y,flag,im):
	if event == cv2.EVENT_FLAG_LBUTTON:
		tracker.query_img = cv2.imread('QR.jpg')
		row, col, channels = tracker.query_img.shape
		tracker.query_img_visualize = frame.copy()
		tracker.query_roi = [0,0,-1,-1]
		tracker.query_roi[2:] = [row,col]
		tracker.last_detection = tracker.query_roi
		tracker.get_query_keypoints()

if __name__ == '__main__':
	# descriptor can be: SIFT, SURF, BRIEF, BRISK, ORB, FREAK
	tracker = QRTracker('SIFT')

	cap = cv2.VideoCapture(0)

	cv2.namedWindow('UI')
	cv2.createTrackbar('Corner Threshold', 'UI', 0, 100, set_corner_threshold_callback)
	cv2.createTrackbar('Ratio Threshold', 'UI', 100, 100, set_ratio_threshold_callback)


	cv2.namedWindow("MYWIN")
	cv2.setMouseCallback("MYWIN",mouse_event)

	while True:
		ret, frame = cap.read()
		frame = np.array(cv2.resize(frame,(frame.shape[1]/2,frame.shape[0]/2)))

		if tracker.query_roi != None:
			tracker.track(frame)

			# add the query image to the side
			combined_img = np.zeros((frame.shape[0],frame.shape[1]+(tracker.query_roi[2]-tracker.query_roi[0]),frame.shape[2]),dtype=frame.dtype)
			combined_img[:,0:frame.shape[1],:] = frame
			combined_img[0:(tracker.query_roi[3]-tracker.query_roi[1]),frame.shape[1]:,:] = (
					tracker.query_img[tracker.query_roi[1]:tracker.query_roi[3],
									  tracker.query_roi[0]:tracker.query_roi[2],:])
			# plot the matching points and correspondences
			for i in range(tracker.matching_query_pts.shape[0]):
				cv2.circle(combined_img,(int(tracker.matching_training_pts[i,0]),int(tracker.matching_training_pts[i,1])),2,(255,0,0),2)
				cv2.line(combined_img,(int(tracker.matching_training_pts[i,0]), int(tracker.matching_training_pts[i,1])),
									  (int(tracker.matching_query_pts[i,0]+frame.shape[1]),int(tracker.matching_query_pts[i,1])),
									  (0,255,0))

			for pt in tracker.query_keypoints:
				cv2.circle(combined_img,(int(pt.pt[0]+frame.shape[1]),int(pt.pt[1])),2,(255,0,0),1)
			cv2.drawContours(combined_img,[tracker.last_box],0,(0,0,255),2)
			cv2.rectangle(combined_img,(tracker.last_detection[0],tracker.last_detection[1]),(tracker.last_detection[2],tracker.last_detection[3]),(0,255,0),2)


			cv2.imshow("MYWIN",combined_img)
		else:
			cv2.imshow("MYWIN",frame)
		cv2.waitKey(50)
	cv2.destroyAllWindows()
