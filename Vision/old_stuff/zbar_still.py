import zbar
import cv2
import numpy as np

cap = cv2.imread('superheroQR.png')


scanner = zbar.ImageScanner()
scanner.parse_config('enable')
gray = cv2.cvtColor(cap, cv2.COLOR_BGR2GRAY)
raw = gray.tostring()
image = zbar.Image(gray.shape[0], gray.shape[1], 'Y800', raw)

scanner.scan(image)

for symbol in image:
	print 'decoded', symbol.type, 'sy,bol', '"%s"' % symbol.data

cv2.imshow('Super', cap)
cv2.imshow('Gray', gray)

if cv2.waitKey(50) & 0xFF == ord('q'):
	cap.release()
	cv2.destroyAllWindows()