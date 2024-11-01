
import numpy as np
from PIL import Image
import random
import numpy as np
import cv2
import random
from scipy import ndimage, misc
from skimage import transform

class Masks():

    @staticmethod
    def get_ff_mask(h, w, num_v = None):
        #Source: Generative Inpainting https://github.com/JiahuiYu/generative_inpainting

        mask = np.zeros((h,w))
        if num_v is None:
            num_v = 15+np.random.randint(9) #5

        for i in range(num_v):
            start_x = np.random.randint(w)
            start_y = np.random.randint(h)
            for j in range(1+np.random.randint(5)):
                angle = 0.01+np.random.randint(4.0)
                if i % 2 == 0:
                    angle = 2 * 3.1415926 - angle
                length = 10 + np.random.randint(60) # 40
                brush_w = 5 + np.random.randint(20) # 10
                end_x = (start_x + length * np.sin(angle)).astype(np.int32)
                end_y = (start_y + length * np.cos(angle)).astype(np.int32)

                cv2.line(mask, (start_y, start_x), (end_y, end_x), 1.0, brush_w)
                start_x, start_y = end_x, end_y

        return mask.astype(np.float32)


    @staticmethod
    def get_box_mask(h,w):
        height, width = h, w

        mask = np.zeros((height, width))

        mask_width = random.randint(int(0.3 * width), int(0.7 * width)) 
        mask_height = random.randint(int(0.3 * height), int(0.7 * height))
 
        mask_x = random.randint(0, width - mask_width)
        mask_y = random.randint(0, height - mask_height)

        mask[mask_y:mask_y + mask_height, mask_x:mask_x + mask_width] = 1
        return mask


    @staticmethod
    def generate_free_form_mask(h, w, maxVertex=16, maxLength=80, maxBrushWidth=20, maxAngle=360):

        mask = np.zeros((h, w), np.float32)
        numVertex = np.random.randint(maxVertex + 1)
        startY = np.random.randint(h)
        startX = np.random.randint(w)
        brushWidth = 0
        for i in range(numVertex):
            angle = np.random.randint(maxAngle + 1)
            angle = angle / 360.0 * 2 * np.pi
            if i % 2 == 0:
                angle = 2 * np.pi - angle
            length = np.random.randint(maxLength + 1)
            brushWidth = np.random.randint(10, maxBrushWidth + 1) // 2 * 2
            nextY = startY + length * np.cos(angle)
            nextX = startX + length * np.sin(angle)

            nextY = np.maximum(np.minimum(nextY, h - 1), 0).astype(np.int32)
            nextX = np.maximum(np.minimum(nextX, w - 1), 0).astype(np.int32)

            cv2.line(mask, (startY, startX), (nextY, nextX), 1, brushWidth)
            cv2.circle(mask, (startY, startX), brushWidth // 2, 1)

            startY, startX = nextY, nextX
        cv2.circle(mask, (startY, startX), brushWidth // 2, 1)
        return mask

    @staticmethod
    def get_ca_mask(h, w, scale = None, r = None):

        if scale is None:
            scale = random.choice([1, 2, 4])
        if r is None:
            r = random.randint(2, 5) # repeat median filter r times

        height = h
        width = w
        mask = np.random.randint(2, size = (height//scale, width//scale))

        for _ in range(r):
            mask = ndimage.median_filter(mask, size=3, mode='constant')

        # mask = misc.imresize(mask, (h, w), interp='nearest')
        mask = cv2.resize(mask, dsize=(w, h), interpolation=cv2.INTER_NEAREST)
     
        if scale > 1:
            struct = ndimage.generate_binary_structure(2, 1)
            mask = ndimage.morphology.binary_dilation(mask, struct)
        elif scale > 3:
            struct = np.array([[ 0.,  0.,  1.,  0.,  0.],
                            [ 0.,  1.,  1.,  1.,  0.],
                            [ 1.,  1.,  1.,  1.,  1.],
                            [ 0.,  1.,  1.,  1.,  0.],
                            [ 0.,  0.,  1.,  0.,  0.]])

        return mask

    @staticmethod
    def get_random_mask(h,w):
        f = random.choice([Masks.get_box_mask, Masks.get_ff_mask, Masks.get_ca_mask, Masks.generate_free_form_mask]) 
        return f(h,w)
    



def create_mask():
    mask_ = Masks()
    random_int = random.randint(0, 3)
    if (random_int == 0):
        num_v = random.randint(10, 24)
        ff_mask = mask_.get_ff_mask(256, 256, num_v)
        ff_mask = (255 * ff_mask).astype(np.uint8)
        image = Image.fromarray(ff_mask)
    if (random_int == 1):
        box_mask = mask_.get_box_mask(256, 256)
        box_mask = (255 * box_mask).astype(np.uint8)
        image = Image.fromarray(box_mask)
    if (random_int == 2):
        maxVertex = random.randint(10, 18)
        maxLength = random.randint(30, 100)
        maxBrushWidth = random.randint(12, 20)
        maxAngle= random.randint(30, 360)
        free_form_mask = mask_.generate_free_form_mask(256, 256, maxVertex, maxLength, maxBrushWidth, maxAngle)
        free_form_mask = (255 * free_form_mask).astype(np.uint8)
        image = Image.fromarray(free_form_mask)
    if (random_int == 3):
        scale = random.choice([1, 2, 4])
        r = random.randint(2, 5)
        ca_mask  = mask_.get_ca_mask(256, 256, scale, r)
        ca_mask = (255 * ca_mask).astype(np.uint8)
        image = Image.fromarray(ca_mask)
    return np.array(image)


