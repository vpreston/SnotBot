import zbar
import numpy as np
import cv2

 
class QRCode():
 
    data = None
    proc = None
    scanner = None
 
    def qr_handler(self,proc,image,closure):
        # extract results
        for symbol in image:
            if not symbol.count:
                self.data = symbol.data
 
    def __init__(self):
        self.proc = zbar.Processor()
        self.scanner = zbar.ImageScanner()
        self.scanner.parse_config('enable')
 
        self.proc.init("/dev/video0")
        self.proc.set_data_handler(self.qr_handler)
        #self.proc.visible = True
#display cam window if True,  hide if False
        #self.proc.active = True
        self.quitter = 1
 
    def get_data(self):
        while (1):
            try:
                self.proc.process_one()
                #self.quitter = input("1 to keep going:   ")
                print self.data
            except KeyboardInterrupt:
                break
        return(self.data)

    def image_display(self):
        cap = cv2.VideoCapture(0)
        while(True):
            # Capture frame-by-frame
            ret, frame = cap.read()

            # Our operations on the frame come here
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Display the resulting frame
            cv2.imshow('frame',gray)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()
 
#if(QRCode().get_data() == "test"):
#	print "DATA IS test"
 
# data = QRCode().get_data()
# if (data == "test"):
# 	print "data is test"
 
if __name__ == '__main__':
    data = QRCode().get_data()


