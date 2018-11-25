from cv2 import *
import cv2
import numpy as np

#HYPERPARAMETERS
DEBUG = True
BLUE_SENS = 30 
RED_SENS = 30
GREEN_SENS = 5  


def showimg(img):
    namedWindow("cam-test")
    imshow("cam-test",img)
    waitKey(0)
    destroyWindow("cam-test")
    imwrite("current.jpg",img) #save image

# initialize the camera
def take_photo():
    cam = VideoCapture(0)   # 0 -> index of camera
    s, img = cam.read()
    if s:
        return img
    else:
        print("ERROR, COULD NOT TAKE PICTURE")

#crop image
def crop(img, pos_x=0, pos_y=0):
    size = img.shape
    size = [int(size[0]/100)*100, int(size[1]/100)*100]
    img = img[pos_x:size[0]+pos_x,pos_y:size[1]+pos_y,0:3]

    return img

def resize(img, times_divided = 3):
    x = img.shape[1]
    y = img.shape[0]
    for _ in range(times_divided):
        x = x/2
        y = y/2
    img = cv2.resize(img, dsize=(int(x), int(y)), interpolation=cv2.INTER_CUBIC)
    return img

def enhance_colors(img):
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            pixel = img[i,j]
            blue = pixel[0]
            green = pixel[1]
            red = pixel[2]

            if(blue-BLUE_SENS > green):
                if (blue-BLUE_SENS > red):
                    img[i,j] = [255,0,0]
            if(green-GREEN_SENS > blue):
                if(green-GREEN_SENS > red):
                    img[i,j] = [0,255,0]
            if(red-RED_SENS > blue):
                if(red-RED_SENS > green):
                    img[i,j] = [0,0,255]
    return img

def enhance_BW(img):
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            pixel = img[i,j]
            sum = 0
            for x in pixel:
                sum = sum + x
            if (sum > 300):
                img[i,j] = [255,255,255]
            elif (sum < 200):
                img[i,j] = [0,0,0]
    return img

def make_grid(img):
    grid = np.zeros((4,6))
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            pixel = img[i,j]
            #blue
            if pixel[0] == 255 and pixel[1] != 255:
                grid[i,j] = 3
            #green
            elif pixel[1]== 255 and pixel[2] != 255:
                grid[i,j] = 2
            #red
            elif pixel[2] == 255 and pixel[1] != 255:
                grid[i,j] = 1
            #black
            elif pixel[1] == 0 and pixel[2] ==0:
                grid[i,j] = 4
            #ground
            else:
                grid[i,j] = 0
    return grid

def output():
    img= take_photo()
    if DEBUG: showimg(img)


      #TEST
   # for i in range(100,img.shape[1]):
    #    pixel = img[0,i]
    #    sum = 0
     #   for x in pixel:
     #       sum = sum + x
     #   if sum < 300:
      #      print(i)
       #     break
    
    ##
    
    img = crop(img, pos_x = 20, pos_y=20)
    if DEBUG: showimg(img)

  


    img = resize(img,times_divided=2)
    if DEBUG: showimg(img)
    img = enhance_colors(img)
    if DEBUG: showimg(img)
    
    

    img = cv2.resize(img, dsize=(6, 4), interpolation=cv2.INTER_CUBIC)
    if DEBUG: showimg(img)

    #TEST2
    #img = enhance_colors(img)
    #showimg(img)
    ##
    img = enhance_BW(img)
    if DEBUG: showimg(img)
    grid = make_grid(img)
    #if DEBUG: print(grid)
    return grid

if __name__ == "__main__":
    g = output()
    print(g)
