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

class imagePrep:
    def __init__(self, fName):
        self.fileName = fName
    
    #=======================================================================================================
    #Converts image to bmp. Needs 'PIL'
    def convbmp(self):
        print('Working on image file: ' + str(self.fileName))
        img_open = Image.open(str(self.fileName))
        img_open.save("currentImage.bmp")
        img_open.close()
    
    #=======================================================================================================
    #Whites out unused parts of the image
    def whiteout(self, xUpperLeft=6, yUpperLeft=6, xLowerRight=129, yLowerRight=41):
        img_open = Image.open("currentImage.bmp")
        pixelMap = img_open.load()
        for i in range(int(xUpperLeft), int(xLowerRight)):
            for j in range(int(yUpperLeft), int(yLowerRight)):
                pixelMap[i,j] = (255, 255, 255)
        img_open.save("currentImage.bmp")
        img_open.close()
        
    #=======================================================================================================
    #Reads numbers on vertical axes
    def readVaxes(self, xUpperLeft=1300, yUpperLeft=1, xLowerRight=1363, yLowerRight=600):
        img_open = Image.open("currentImage.bmp")
        vAxis_img = img_open.crop((xUpperLeft, yUpperLeft, xLowerRight, yLowerRight))
        img_open.close()
        vAxis_img.save("vAxis.bmp")
        vAxis_img = Image.open("vAxis.bmp")
        
        pixelMap = vAxis_img.load()

        for i in range(vAxis_img.size[0]):
            for j in range(vAxis_img.size[1]):
                if (pixelMap[i,j][0]-15 > (pixelMap[i,j][1]+pixelMap[i,j][2])/2 or
                    pixelMap[i,j][1]-15 > (pixelMap[i,j][0]+pixelMap[i,j][2])/2):
                    pixelMap[i,j] = (255, 255, 255)

        vAxis_img.save("vAxis.bmp")
        
        import pytesseract
        #Change this to the location of tesseract.exe in your machine
        pytesseract.pytesseract.tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        from pytesseract import image_to_string
        
        myText = image_to_string(vAxis_img)
        
        headstr = ''
        for i in range(len(myText)):
            if myText[i] in ".1234567890":
                headstr = headstr + myText[i]
                if myText[i+1] not in ".1234567890":
                    break

        tailstr = ''
        for i in range(len(myText)-1, 0, -1):
            if myText[i] in ".1234567890":
                tailstr = myText[i] + tailstr
                if myText[i-1] not in ".1234567890":
                    break
        
        top = input('Is UPPER grid line = '+headstr+' ? Yes => ENTER; No => enter the value: ')
        bot = input('Is LOWER grid line = '+tailstr+' ? Yes => ENTER; No => enter the value: ')
        
        if top != '':
            topValue = float(top)
        else:
            topValue = float(headstr)
        
        if bot != '':
            botValue = float(bot)
        else:
            botValue = float(tailstr)
            
        return topValue, botValue

class digitize:
    def __init__(self, imageRead):
        self.img = imageRead
    
    #=======================================================================================================
    #If the number of gray pixels in each line is greater than half of image dimensions then
    #it assumes that it is a grid line and saves its position into 'hLinesY' and 'vLinesX'
    def grid(self, grdcolor=[[239, 239, 241],[216, 216, 220]]):
            
        #Counts the number of gray pixels in each horizontal and vertical line. Needs 'Counter'
        hGrid = []
        vGrid = []
        
        #Finds grid pixels
        for i in range(0, self.img.shape[1]):
            for j in range(0, self.img.shape[0]):
                if ((self.img[j,i,0]==grdcolor[0][0] and
                     self.img[j,i,1]==grdcolor[0][1] and
                     self.img[j,i,2]==grdcolor[0][2]) or
                    (self.img[j,i,0]==grdcolor[1][0] and
                     self.img[j,i,1]==grdcolor[1][1] and
                     self.img[j,i,2]==grdcolor[1][2])):
                    hGrid.extend([j])
                    vGrid.extend([i])
        
        #Counts the number of gray pixels in each horizontal and vertical line. Needs 'Counter'
        hCount = Counter(hGrid)
        vCount = Counter(vGrid)
        
        hLinesY = []
        for i in range(0, len(hCount.most_common())):
            if hCount.most_common()[i][1]>(self.img.shape[1]/1.9):
               hLinesY.extend([hCount.most_common()[i][0]])
            else:
               break
        hLinesY.sort()
        
        vLinesX = []
        for j in range(0, len(vCount.most_common())):
            if vCount.most_common()[j][1]>(self.img.shape[0]/1.9):
               vLinesX.extend([vCount.most_common()[j][0]])
            else:
               break
        vLinesX.sort()
    
        return vLinesX, hLinesY

    #=======================================================================================================
    #Converts image to data, Needs 'numpy'
    def digitImg(self, stkcolor=[[224, 27, 28],[59, 164, 59]]):
        data = np.zeros((self.img.shape[1], 3), dtype=int)
                
        #Finds vertical boundaries of candle sticks:
        
        for i in range(0, self.img.shape[1]):
            for j in range(0, self.img.shape[0]):
                if (self.img[j,i,0]==stkcolor[0][0] and
                    self.img[j,i,1]==stkcolor[0][1] and
                    self.img[j,i,2]==stkcolor[0][2]): # 0 & 1: RED
                   data[i, 1] = j
                   for jj in range(j+1, self.img.shape[0]):
                       if (self.img[jj,i,0]!=stkcolor[0][0] or
                           self.img[jj,i,1]!=stkcolor[0][1] or
                           self.img[jj,i,2]!=stkcolor[0][2]):
                           data[i, 0] = jj-1
                           data[i, 2] = -1
                           break
                   break
                if (self.img[j,i,0]==stkcolor[1][0] and
                    self.img[j,i,1]==stkcolor[1][1] and
                    self.img[j,i,2]==stkcolor[1][2]): # 1 & 2: GREEN
                   data[i, 2] = j
                   for jj in range(j+1, self.img.shape[0]):
                       if (self.img[jj,i,0]!=stkcolor[1][0] and
                           self.img[jj,i,1]!=stkcolor[1][1] and
                           self.img[jj,i,2]!=stkcolor[1][2]):
                           data[i, 1] = jj-1
                           data[i, 0] = -1
                           break
                   break
        
        return data

    #=======================================================================================================
    #Returns the positions of the first candle stick after the first vertical grid line ('begin')
    #as well as the positions of the last candle stick before the last vertical grid line ('end')
    #We need them to cut unused ends of digitImg
    def trimPos(self, data, vLinesX, bcgndclr=[0, 0, 0]):
                
        for i in range(vLinesX[0], 0, -1):
            if (data[i, 0]==bcgndclr[0] and data[i, 1]==bcgndclr[1] and data[i, 2]==bcgndclr[2]):
                begin = i
                break

        for j in range(vLinesX[-1], 0, -1):
            if (data[j, 0]==bcgndclr[0] and data[j, 1]==bcgndclr[1] and data[j, 2]==bcgndclr[2]):
                end = j
                break
        
        return begin, end

    #=======================================================================================================
    #Cuts unused ends of digitImg.
    #This makes reading the candlestick tips procedure, which includes a lot of 'if' statements, faster 
    def trimDigitImg(self, data, begin, end):
        
        data_new = data[begin : end + 1, :]
        
        return data_new

    #=======================================================================================================
    #Finds new positions of vertical lines based on trimmed data matrix
    def newVgrid(self, vLinesX, begin):
        
        vLinesX_new = []
        for i in range(len(vLinesX)):
            vLinesX_new.append(vLinesX[i] - begin)
        
        return vLinesX_new

    #=======================================================================================================
    
    def stkEnds(self, data_new, vLinesX_new):
                
        #Finds horizontal boundaries of candle sticks
        
        # Wow wow wow !!! This method is hidden. Now You have two options:
        # 1- Figure out how it should be and try to write it
            #If you could write it successfully you can email it to me with the results and I will give away $100 AUD to you
            #No cheating !!!
        # 2- Email me with your GitHub account and I will hand it over to you
        #My email: kshvzn@gmail.com

        return startEnd

    #=======================================================================================================
    #Finds positions for open, close, high and low
    def ohlcPos(self, startEnd, data_new):
        ohlc = np.zeros((startEnd.shape[0], 4), dtype=int)
        
        for i in range(0, ohlc.shape[0]):
            if (min(data_new[startEnd[i, 0]:startEnd[i, 1], 0])!=-1): 

               ohlc[i, 0] = max(data_new[startEnd[i, 0]:startEnd[i, 1], 1]) #Red_Open
               ohlc[i, 1] = min(data_new[startEnd[i, 0]:startEnd[i, 1], 1]) #Red_High
               ohlc[i, 2] = max(data_new[startEnd[i, 0]:startEnd[i, 1], 0]) #Red_Low
               ohlc[i, 3] = min(data_new[startEnd[i, 0]:startEnd[i, 1], 0]) #Red_Close
               
            else:
               
               ohlc[i, 0] = min(data_new[startEnd[i, 0]:startEnd[i, 1], 1]) #Green_Open
               ohlc[i, 1] = min(data_new[startEnd[i, 0]:startEnd[i, 1], 2]) #Green_High
               ohlc[i, 2] = max(data_new[startEnd[i, 0]:startEnd[i, 1], 1]) #Green_Low
               ohlc[i, 3] = max(data_new[startEnd[i, 0]:startEnd[i, 1], 2]) #Green_Close
        
        return ohlc

    #=======================================================================================================
    #Finds values for open, close, high and low
    def ohlcVal(self, ohlc, hLinesY, up_grid_val, low_grid_val):
                
        ohlcValues = ((low_grid_val-up_grid_val)/(hLinesY[-1]-hLinesY[0]))*(ohlc-hLinesY[0]) + up_grid_val
        
        return ohlcValues

    #=======================================================================================================
    #Adds related date to dateTab variable for each candle stick
    def dateTable(self, ohlc, startEnd, yearLeft, monthLeft, dayLeft):
        dateTab = []
        dt = datetime.timedelta(days=1, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
        runningDate = datetime.date(yearLeft, monthLeft, dayLeft)
        lastDate = runningDate - dt
        
        while len(dateTab) < ohlc.shape[0]:
            if ((runningDate.strftime("%A")=='Sunday')):
                runningDate = runningDate + dt
            
            elif ((runningDate.strftime("%A")=='Saturday') and (startEnd[len(dateTab),3]==1)):
                runningDate = runningDate + dt
            
            elif ((runningDate.month==lastDate.month) and (startEnd[len(dateTab),2]==1)):
                runningDate = runningDate + dt
            
            elif ((runningDate.month!=lastDate.month) and (startEnd[len(dateTab),2]==1)):
                dateTab.append(runningDate)
                lastDate = runningDate
                runningDate = runningDate + dt
            
            elif ((runningDate.month==lastDate.month) and (startEnd[len(dateTab),2]==0)):
                dateTab.append(runningDate)
                lastDate = runningDate
                runningDate = runningDate + dt
            
            elif ((runningDate.month!=lastDate.month) and (startEnd[len(dateTab),2]==0)):
                dateTab.append(lastDate)
            
            else:
                runningDate = runningDate + dt
        
        return dateTab

    #=======================================================================================================
    #Attaches date and hloc values tables as a unique data frame
    def finalTable(self, dateTab, ohlcVal):
        tabOut = []
                
        dateTab = pd.DataFrame(dateTab)
        tabOut = pd.DataFrame(tabOut)
        tabOut = tabOut.assign(Date = dateTab[0])
        ohlcVal = pd.DataFrame(ohlcVal)
        tabOut = tabOut.assign(Open=ohlcVal[0], High=ohlcVal[1], Low=ohlcVal[2], Close=ohlcVal[3])
        print (tabOut)
        return tabOut

#=======================================================================================================
# Exports the final table as a .csv file
def main():
    imgp = imagePrep ("2009(1).png")
    imgp.convbmp()
    imgp.whiteout()
    
    topbotVal = imgp.readVaxes()
    topVal, botVal = topbotVal[0], topbotVal[1]
    
    dgz = digitize(img.imread('currentImage.bmp'))
    data = dgz.digitImg()
    
    lines = dgz.grid()
    vLinesX, hLinesY = lines[0], lines[1]
    
    trim = dgz.trimPos(data, vLinesX)
    begin, end = trim[0], trim[1]
    
    newData = dgz.trimDigitImg(data, begin, end)
    new_vLinesX = dgz.newVgrid(vLinesX, begin)
    stickEnds = dgz.stkEnds(newData, new_vLinesX)
    ohlcPosition = dgz.ohlcPos(stickEnds, newData)
    ohlcValues = dgz.ohlcVal(ohlcPosition, hLinesY, topVal, botVal)
    datetab = dgz.dateTable(ohlcPosition, stickEnds, int(2009), int(1), int(1))
    tabFinal = dgz.finalTable(datetab, ohlcValues)
    
    tabFinal.to_csv ('OHLC'+'.csv', header=['Date', 'Open', 'High', 'Low', 'Close'], index=None)

if __name__ == "__main__":
    main()
