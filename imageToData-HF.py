# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 13:34:34 2021

@author: Kianoosh Keshavarzian
"""

from PIL import Image
import datetime
import matplotlib.image as img
import numpy as np
import pandas as pd
from collections import Counter

#=======================================================================================================
#Converts image to bmp. Needs 'PIL'
def img_to_bmp(fileName):
    print('Working on image file: ' + str(fileName))
    img_open = Image.open(str(fileName))
    img_open.save("currentImage.bmp")
    img_open.close()

#=======================================================================================================
#Removes the logo
def remove_logo(img_open, x_upperLeft, y_upperLeft, x_lowerRight, y_lowerRight):
    pixelMap = img_open.load()
    for i in range(int(x_upperLeft), int(x_lowerRight)):
        for j in range(int(y_upperLeft), int(y_lowerRight)):
            pixelMap[i,j] = (255, 255, 255)
    img_open.save("currentImage.bmp")
    img_open.close()

#=======================================================================================================
#Find grid lines
def grid_lines(image):
        
    #Counts the number of gray pixels in each horizontal and vertical line. Needs 'Counter'
    hGrid = []
    vGrid = []
    
    #Finds grid pixels
    for i in range(0, image.shape[1]):
        for j in range(0, image.shape[0]):
            if ((image[j,i,0]==239 and image[j,i,1]==239 and image[j,i,2]==241) or (image[j,i,0]==216 and image[j,i,1]==216 and image[j,i,2]==220)):
                hGrid.extend([j])
                vGrid.extend([i])
    
    #Counts the number of gray pixels in each horizontal and vertical line. Needs 'Counter'
    hCount = Counter(hGrid)
    vCount = Counter(vGrid)
    
    hLinesY = []
    
    for i in range(0, len(hCount.most_common())):
        if hCount.most_common()[i][1]>(image.shape[1]/1.9):
           hLinesY.extend([hCount.most_common()[i][0]])
        else:
           break
    hLinesY.sort()
    
    vLinesX = []
    for j in range(0, len(vCount.most_common())):
        if vCount.most_common()[j][1]>(image.shape[0]/1.9):
           vLinesX.extend([vCount.most_common()[j][0]])
        else:
           break
    vLinesX.sort()

    return vLinesX, hLinesY

#=======================================================================================================
#Converts image to data, Needs 'numpy'
def img_data(image):
    data = np.zeros((image.shape[1], 3), dtype=int)
            
    #Finds vertical boundaries of candle sticks:
    
    for i in range(0, image.shape[1]):
        for j in range(0, image.shape[0]):
            if (image[j,i,0]==224 and image[j,i,1]==27 and image[j,i,2]==28): # 0 & 1: RED
               data[i, 1] = j
               for jj in range(j+1, image.shape[0]):
                   if (image[jj,i,0]!=224 or image[jj,i,1]!=27 or image[jj,i,2]!=28):
                       data[i, 0] = jj-1
                       data[i, 2] = -1
                       break
               break
            if (image[j,i,0]==59 and image[j,i,1]==164 and image[j,i,2]==59): # 1 & 2: GREEN
               data[i, 2] = j
               for jj in range(j+1, image.shape[0]):
                   if (image[jj,i,0]!=59 and image[jj,i,1]!=164 and image[jj,i,2]!=59):
                       data[i, 1] = jj-1
                       data[i, 0] = -1
                       break
               break
    
    return data

#=======================================================================================================
#Finds unused ends of img_data
def unused_ends():
    data = img_data(img.imread('currentImage.bmp'))
    vLinesX = grid_lines(img.imread('currentImage.bmp'))[0]
    
    for i in range(vLinesX[0], 0, -1):
        if (data[i, 0]==0 and data[i, 1]==0 and data[i, 2]==0):
            begin = i
            break
    del i
    for i in range(vLinesX[-1], 0, -1):
        if (data[i, 0]==0 and data[i, 1]==0 and data[i, 2]==0):
            end = i
            break
    
    return begin, end

#=======================================================================================================
#Cuts unused ends of img_data.
def img_data_trim():
    data = img_data(img.imread('currentImage.bmp'))
    begin = unused_ends()[0]
    end = unused_ends()[1]
    data_new = data[begin:end+1, :]
    
    return data_new

#=======================================================================================================
#Finds new positions of vertical lines based on trimmed data matrix
def grid_lines_new():
    vLinesX = grid_lines(img.imread('currentImage.bmp'))[0]
    begin = unused_ends()[0]
    vLinesX_new = []
    hLinesY = grid_lines(img.imread('currentImage.bmp'))[1]
    
    for i in range(len(vLinesX)):
        vLinesX_new.append(vLinesX[i] - begin)
    
    return vLinesX_new, hLinesY

#=======================================================================================================
#Finds horizontal boundaries of candle sticks
def start_end_raw():
    data_new = img_data_trim()
    i = 0
    startEnd = np.zeros((0, 4), dtype=int)
    
    while i < data_new.shape[0]:
          if (data_new[i, 0]!=0 and data_new[i, 1]!=0 and data_new[i, 2]!=0):
             start = i
             for ii in range(i, data_new.shape[0]):
                 if (data_new[ii, 0]==0 and data_new[ii, 1]==0 and data_new[ii, 2]==0):
                    end = ii
                    startEnd = np.append(startEnd, [[start, end, 0, 0]], 0)
                    break
             i = end
          else:
             i = i + 1
    
    return startEnd

#=======================================================================================================
def start_end():
    startEnd = start_end_raw()
    vLinesX_new = grid_lines_new()[0]
    n = 0
    
    for i in range(startEnd.shape[0]):
        if ((i>0) and (abs(startEnd[i, 0]-startEnd[i-1, 1])>abs(startEnd[i, 0]-startEnd[i, 1]))):
            startEnd[i, 3] = 1
        if ((i==0) and (startEnd[i, 0]>abs(startEnd[i, 0]-startEnd[i, 1]))):
            startEnd[i, 3] = 1
        if (startEnd[i, 1] > vLinesX_new[n]):
            startEnd[i, 2] = 1
            if n < len(vLinesX_new)-1:
                n = n + 1
            else:
                print('End of file vLinesX!!! Check the code.')
                break
    
    return startEnd

#=======================================================================================================
#Finds positions for open, close, high and low
def hloc_pos():
    
    hloc = []
    
    #The content of this function is hidden,
    #Please contact me to deliver it to you.
    
    return hloc

#=======================================================================================================
#Finds values for open, close, high and low
def hloc_values(upper_gridLine_value, lowe_gridLine_value):
    
    #The content of this function is hidden,
    #Please contact me to deliver it to you.
    
    hlocVal = 0
    
    return hlocVal

#=======================================================================================================
#Adds related date to dateTab variable for each candle stick
def date_table(yearLeft, monthLeft, dayLeft):
    
    dateTab = []
    
    #The content of this function is hidden,
    #Please contact me to deliver it to you.
    
    return dateTab

#=======================================================================================================
#Attaches date and hloc values tables as a unique data frame
def table_out():
    tabOut = []
    dateTab = date_table(int(2009), int(1), int(1))
    hlocVal = hloc_values(1020, 780)
    
    dateTab = pd.DataFrame(dateTab)
    tabOut = pd.DataFrame(tabOut)
    tabOut = tabOut.assign(Date = dateTab[0])
    hlocVal = pd.DataFrame(hlocVal)
    tabOut = tabOut.assign(Highest = hlocVal[0], Lowest = hlocVal[1], Open = hlocVal[2], Close = hlocVal[3])
    
    return tabOut

#=======================================================================================================
# Exports the final table as a .csv file
def main():
    img_to_bmp('2009(1).png')
    remove_logo(Image.open("currentImage.bmp"), 6, 6, 129, 41)
    tabFinal = table_out()
    tabFinal.to_csv ('HLOC'+'.csv', header=['Date', 'Highe', 'Lowe', 'Open', 'Close'], index=None)

if __name__ == "__main__":
    main()
