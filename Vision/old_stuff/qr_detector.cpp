#include <stdio.h>
#include "opencv2/core/core.hpp"
#include "opencv2/features2d/features2d.hpp"
#include "opencv2/highgui/highgui.hpp"
#include "opencv2/nonfree/nonfree.hpp"
#include <iostream>

using namespace cv;
using namespace std;

int main(int argc, char** argv)
{
    VideoCapture capture(0);

    if (!capture.isOpened()) { 
        cout << " ERR: Unable find input Video source." << endl;
        return -1;
    }

    Mat img1 = imread(argv[1], CV_LOAD_IMAGE_GRAYSCALE);
    Mat img2;
    capture >> img2;

    if(img1.empty() || img2.empty())
    {
        printf("Can't read one of the images\n");
        return -1;
    }

    int key = 0;
    double min_dist, max_dist;

    while (key != 'q') {

        min_dist = 10;
        max_dist = 0;

        // detecting keypoints
        SurfFeatureDetector detector(400);
        vector<KeyPoint> keypoints1, keypoints2;
        detector.detect(img1, keypoints1);
        detector.detect(img2, keypoints2);

        // computing descriptors
        SurfDescriptorExtractor extractor;
        Mat descriptors1, descriptors2;
        extractor.compute(img1, keypoints1, descriptors1);
        extractor.compute(img2, keypoints2, descriptors2);

        // matching descriptors
        BFMatcher matcher(NORM_L2);
        vector<DMatch> matches;
        matcher.match(descriptors1, descriptors2, matches);

        // Computes the maximum and minimum distances between keypoints
        for (int i = 0; i < descriptors1.rows; i++) {
            double dist = matches[i].distance;
            if (dist < min_dist) min_dist = dist;
            if (dist > max_dist) max_dist = dist;
        }

        // Keeps the "good matches," whose distances are less than 2*min_dist
        vector<DMatch> good_matches;
        vector<Point2f> match_points;

        for (int i = 0; i < descriptors1.rows; i++) {
            if (matches[i].distance <= min(2*min_dist, 0.2)) {
                good_matches.push_back(matches[i]);
                match_points.push_back(keypoints2[matches[i].queryIdx].pt);
            }
        }

        // If there is at least one match, the QR code has been detected
        // if (good_matches.size() > 0) { cout << "QR Detected: " << good_matches.size() << endl; }

        // drawing the results
        namedWindow("matches", 1);
        Mat img_matches;
        drawMatches(img1, keypoints1, img2, keypoints2, good_matches, img_matches, Scalar::all(-1), Scalar::all(-1),
               vector<char>(), DrawMatchesFlags::NOT_DRAW_SINGLE_POINTS);
        imshow("matches", img_matches);
        capture >> img2;
        key = waitKey(1);
    }

    return 0;
}