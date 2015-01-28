import zbar
import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while cap.isOpened():
	scanner = zbar.ImageScanner()
	scanner.parse_config('enable')
	ret, frame = cap.read()
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	raw = gray.tostring()
	image = zbar.Image(gray.shape[0], gray.shape[1], 'Y800', raw)

	scanner.scan(image)

	for symbol in image:
		print 'decoded', symbol.type, 'sy,bol', '"%s"' % symbol.data

	cv2.imshow('Video', gray)


	if cv2.waitKey(30) & 0xFF == ord('q'):
		break

if cv2.waitKey(30) & 0xFF == ord('q'):
	cap.release()
	cv2.destroyAllWindows()
