#include <iostream>
#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"

using namespace cv;
using namespace std;

int main(int argc, char** argv) {
	VideoCapture cap(0);  // Captures video from webcam

	if(!cap.isOpened()) {
		cout << "Cannot open the web cam :(" << endl;
		return -1;
	}

	namedWindow("Control", CV_WINDOW_AUTOSIZE);  // Create a window called "Control"

	int iLowH = 1;  // HSV values for a light shade of purple
	int iHighH = 11;

	int iLowS = 154;
	int iHighS = 232;

	int iLowV = 70;
	int iHighV = 205;

	//Create trackbars in "Control" window

	// cvCreateTrackbar("LowH", "Control", &iLowH, 179);
	// cvCreateTrackbar("HighH", "Control", &iHighH, 179);

	// cvCreateTrackbar("LowS", "Control", &iLowS, 255);
	// cvCreateTrackbar("HighS", "Control", &iHighS, 255);

	// cvCreateTrackbar("LowV", "Control", &iLowV, 255);
	// cvCreateTrackbar("HighV", "Control", &iHighV, 255);

	int iLastX = -1; // Tracks where the object is
	int iLastY = -1;

	Mat imgTmp;
	cap.read(imgTmp);

	Mat imgLines = Mat::zeros(imgTmp.size(), CV_8UC3);

	while (true) {
		Mat imgOriginal;

		bool bSuccess = cap.read(imgOriginal); // Read a new frame from the video

		if(!bSuccess) {
			cout << "Cannot read a frame from video stream" << endl;
			break;
		}


		Mat imgHSV;

		cvtColor(imgOriginal, imgHSV, COLOR_BGR2HSV);

		Mat imgThresholded;

		inRange(imgHSV, Scalar(iLowH, iLowS, iLowV), Scalar(iHighH, iHighS, iHighV), imgThresholded);

		// Morphological opening (removes small objects from the foreground)
		erode(imgThresholded, imgThresholded, getStructuringElement(MORPH_ELLIPSE, Size(5,5)));
		dilate(imgThresholded, imgThresholded, getStructuringElement(MORPH_ELLIPSE, Size(5,5)));

		// Morphological closing (removes small holes from the foreground)
		dilate(imgThresholded, imgThresholded, getStructuringElement(MORPH_ELLIPSE, Size(5,5)));
		erode(imgThresholded, imgThresholded, getStructuringElement(MORPH_ELLIPSE, Size(5,5)));

		// Calculates the moments of the thresholded image
		Moments oMoments = moments(imgThresholded);

		double dM01 = oMoments.m01;
		double dM10 = oMoments.m10;
		double dArea = oMoments.m00;

		if(dArea > 10000) {
			int posX = dM10 / dArea;
			int posY = dM01 / dArea;

			if(iLastX >= 0 && iLastY >= 0 && posX >= 0 && posY >= 0) {
				line(imgLines, Point(posX, posY), Point(iLastX, iLastY), Scalar(0,0,255), 2);
			}

			iLastX = posX;
			iLastY = posY;
		}

		imgOriginal = imgOriginal + imgLines;

		imshow("Thresholded Image", imgThresholded);
		imshow("Original", imgOriginal);

		if(waitKey(30) == 27) { // Wait for 'esc' key press to break loop
			cout << "ESC key is pressed by user" << endl;
			break;
		}
	}

	return 0;
}