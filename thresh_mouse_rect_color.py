import sys
import cv2
import numpy as np
from numba import jit

import ic_utils as ic


@jit
def threshold_impl(src, thresh, maxval):
    width = src.shape[1]
    height = src.shape[0]
    dest = np.zeros_like(src)
    for j in range(height):
        for i in range(width):
            if src[j, i] > thresh:
                dest[j, i] = maxval
            else:
                dest[j, i] = 0
    return dest


def main():
    cap = ic.select_capture_source(sys.argv)

    cv2.namedWindow('result')
    cv2.createTrackbar('thresh', 'result', 128, 255, ic.do_nothing)

    mstate = {
        'selection': 'invalid',
        'xybegin': (-1, -1),
        'xyend': (-1, -1),
    }
    cv2.setMouseCallback('result', ic.on_mouse_rect, mstate)

    while True:
        grabbed, frame = cap.read()
        if not grabbed:
            break
        
        img_color = frame.copy()
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        th = cv2.getTrackbarPos('thresh', 'result')
        xbegin, ybegin = mstate['xybegin']
        xend, yend = mstate['xyend']

        if mstate['selection'] == 'valid':
            roi_gray = img_gray[ybegin:yend, xbegin:xend]
            thresh_roi = threshold_impl(roi_gray, th, 255)
            thresh_roi_color = cv2.cvtColor(thresh_roi, cv2.COLOR_GRAY2BGR)
            img_color[ybegin:yend, xbegin:xend] = thresh_roi_color

        elif mstate['selection'] == 'ongoing':
            cv2.rectangle(img_color, (xbegin, ybegin), (xend, yend), 
                          color=(0, 0, 0), thickness=2)

        cv2.imshow('result', img_color)
        key = cv2.waitKey(30)
        if key == ord('q'):
            break

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
