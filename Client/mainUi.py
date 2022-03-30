from asyncio.windows_events import NULL
from base64 import encode
from copy import deepcopy
from email import header
from encodings import utf_8
import encodings
from importlib import reload
from itertools import count
import json
import ctypes
import datetime as dtime
from itertools import count
import multiprocessing
from pathlib import Path
from queue import PriorityQueue
from operator import truediv
from select import select
from threading import local
import threading
from tkinter import Image
from functools import singledispatch
from typing import Any, overload
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog
import sys
from msilib.schema import Control, File
import sys
import cv2
import time
from PyQt5.QtWidgets import  QApplication,QFileDialog,QTableWidgetItem,QHeaderView,QLabel,QWidget
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QMovie,QPixmap, QPainter, QPen,QColor,QBrush,QTransform,QCursor,QIntValidator
from cv2 import QT_PUSH_BUTTON
from flask import Response, jsonify
from PyQt5.QtCore import Qt,QDateTime,QDate,QTime,QTimer,QThread, pyqtSignal, pyqtSlot, QThreadPool, QProcess, QPoint,Qt,QRect
import numpy
from sklearn.feature_selection import SelectFpr
from sympy import false
from api import baseURL
import requests 
import pandas as pd
from sys import *
import cv2 as cv
import dateutil.parser
import os.path
from os import path
from matplotlib import image, widgets
from sklearn.feature_selection import SelectFromModel
from PIL import ImageQt
import numpy as np

#NOTE: Si pag save kang road saka playback yaon igdi sa file, control F 'save road' saka 'save playback' ka nalang
# si pag save kang violation nasa track.py sa detection_module control-F 'save violation' ka nalang ulit


#adding the functinality features
#import classes
import sys
import os
sys.path.append("../")
from main import processRoad, detection # main function to run detection

PATH = os.getcwd()

def cvImgtoQtImg(cvImg):  #Define the function of opencv image to PyQt image
    """Convert from an opencv image to QPixmap"""
    rgb_image = cv2.cvtColor(cvImg, cv2.COLOR_BGR2RGB)
    # im_pil = Img.fromarray(rgb_image)
    h, w, ch = rgb_image.shape
    bytes_per_line = ch * w
    convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
    p = convert_to_Qt_format
    return p


class FinishingUi(QtWidgets.QWidget):#Finishing Loading UI
    screenLabel=QtCore.pyqtSignal()
    def __init__(self):
        super(FinishingUi, self).__init__()
        uic.loadUi(PATH+'/finishingUi.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.animation=QMovie(PATH+'/icon/loadingAnimated.gif')#animation Logo
        self.loading.setMovie(self.animation)
        self.animation.start()#animation Statrt
        self.show()
        QtCore.QTimer.singleShot(numpy.iinfo(numpy.int32).max, self.closeWindow)#run the window for max in value
    def closeWindow(self):
        self.screenLabel.emit()#calling screenlabel 
        self.close()#closing Widget
        
class ProcessingDataUi(QtWidgets.QWidget):#Retrieving Loading UI
    screenLabel=QtCore.pyqtSignal()
    def __init__(self):
        super(ProcessingDataUi, self).__init__()
        uic.loadUi(PATH+'/processingDataUi.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.animation=QMovie(PATH+'/icon/loadingAnimated.gif')#animation Logo
        self.loading.setMovie(self.animation)
        self.animation.start()#animation Statrt
        self.show()
        QtCore.QTimer.singleShot(numpy.iinfo(numpy.int32).max, self.closeWindow)#run the window for max in value
    def closeWindow(self):
        self.screenLabel.emit()#calling screenlabel 
        self.close()#closing Widget



class roadSettingUp(QtWidgets.QWidget):#road Setting Up Loading
    screenLabel=QtCore.pyqtSignal()
    def __init__(self):
        super(roadSettingUp, self).__init__()
        uic.loadUi(PATH+'/settingUpRoad.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)#hide title bar
        self.animation=QMovie(PATH+'/icon/loadingAnimated.gif')#Animation Loading
        self.loading.setMovie(self.animation)
        self.animation.start()#start Animation
        self.show()
        QtCore.QTimer.singleShot(numpy.iinfo(numpy.int32).max, self.closeWindow)#run the window for 5 mins
    def closeWindow(self):
        self.screenLabel.emit()
        self.close()#cloase Window


class myQLabel(QWidget):
    def __init__(self,parent):
        super(myQLabel, self).__init__(parent)
        self.newWindowSize=self.resize(1280,720)
        self.image = QtGui.QImage("image 1.jpg")
        self.draw=QLabel(self)
        self.draw.setGeometry(QtCore.QRect(0, 0,1280,720))
        pixmap = QPixmap(parent.width(),parent.height()) # width, height
        newPixmap=pixmap.scaled(1280,720)#scaled the Pixmap
        newPixmap.fill(Qt.transparent)
        self.draw.setPixmap(newPixmap)
        #self.verticalLayout.addWidget(self.label)
        #canvas.scaled(1080,720)
        """self.image.setScaledContents(True)"""
        #self.image.setPixmap(canvas)
        self.drawAction=True
        self.last_x, self.last_y = None, None
        self.eraser_selected=False
        self._size=50
        self.parentDraw = parent
        
        
    def drawROI(self, roi, im, roadload):
        self.roadload = roadload
        "For Auto Segmentaion"
        for r in roi:
            bg = np.zeros_like(im)  
            cv2.drawContours(bg, [r], -1, (0,0,255), thickness= -1)
            pts = np.where(bg == 255)

            pm=QtGui.QPixmap(self.draw.pixmap()) 
            painter=QtGui.QPainter(pm)
            painter.setPen(QPen(QColor(255,0,0),20 ,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
            transform=QTransform().scale(pm.width()/self.draw.width(),
                                        pm.height()/self.draw.height())    
            #loop through roi location
            pts = [pts[0],pts[1]]
            pts = np.transpose(pts)
            
            self.drawThread = QThread()
            self.drawThreadObject = Drawer(pts, painter, pm) # fetch all roads but only ids
            self.drawThreadObject.moveToThread(self.drawThread)
            self.drawThread.started.connect(self.drawThreadObject.draw)
            self.drawThreadObject.finished.connect(self.finishedDrawingROI)
            self.drawThread.start()
            
        """End of Auto Segmentation"""
    def finishedDrawingROI(self, painter, pm):
        self.drawThread.quit()
        self.roadload.closeWindow()
        painter.end()
        self.draw.setPixmap(pm)
    def paintEvent(self, event):
        """Create QPainter object.This is to prevent
            the chance of the painting being
            lostif the user changes windows."""
        pm=QtGui.QPixmap(self.draw.pixmap()) 
        painter=QtGui.QPainter(pm)
        painter.end()
        self.draw.setPixmap(pm)
        canvasPainter = QtGui.QPainter(self)
        canvasPainter.drawImage(self.rect(), self.image, self.image.rect())
    

    def mousePressEvent(self, event):
        """Handle when mouse is pressed."""
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()
            
    def mouseMoveEvent(self,point):
        painter = QPainter(self.draw.pixmap())
        if self.eraser_selected == False:
            self.last_x=point.x()
            self.last_y=point.y()
            painter.setPen(QPen(QColor(255,0,0),self._size ,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
            painter.drawPoint(point.pos())
            # Update the mouse's position for next movement
            """self.last_mouse_pos = point.pos()
            self.last_x=point.x()
            self.last_y=point.y()"""
        elif self.eraser_selected == True:
            # Use the eras
            eraser = QRect(point.x(), point.y(), self._size, self._size)
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.eraseRect(eraser)
    def mouseReleaseEvent(self,e):
        print(e.pos())
        self.last_x=None
        self.last_y=None
class CctvWindow(QtWidgets.QWidget):
    def __init__(self):
        super(CctvWindow,self).__init__()
        uic.loadUi('cctvWindow.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)


class IpAddWindow(QtWidgets.QWidget):
    def __init__(self):
        super(IpAddWindow, self).__init__()
        uic.loadUi('addIP_add.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)#removing title bar
        self.btnCancel.clicked.connect(self.close)
        


class LogoutUi(QtWidgets.QWidget):#Logout Ui
    confirmLogout=QtCore.pyqtSignal()
    def __init__(self):
        super(LogoutUi, self).__init__()
        uic.loadUi(PATH+'/logoutUi.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)#removing title bar
        self.btnLogout.clicked.connect(self.confirmLogout.emit)
        self.btnCancel.clicked.connect(self.close)
   
        

class RoadSetUp1(QtWidgets.QMainWindow):#Road Setting Up Ui
    switch_window = QtCore.pyqtSignal()
    settingUpRoad=QtCore.pyqtSignal()
    def __init__(self, w):
        super(RoadSetUp1, self).__init__()
        uic.loadUi(PATH+'/roadSetUp_phase1.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)      #removing Title bar
        #self.label.mousePressEvent = self.selectImage   #mouse Event for Qlabel
        self.btnNew.clicked.connect(self.switch_window.emit)    #Showing Draw road Ui
        self.btnCancel.clicked.connect(self.close)          #close window
        self.btnConfirm.clicked.connect(self.loading)       #Loading Ui
        self.btnDelete.clicked.connect(self.dropRoad)
        
        
        # self.rThread.start()
        # self.loadingRetrieve = ProcessingDataUi()
        # use threading when retrieving data so that gui won't freeze if there's a slow network bandwith
        
        self.rThread = QThread()
        self.roadRet = ProcessData(action= '/RoadFetchIds', type=1) # fetch all roads but only ids
        self.roadRet.moveToThread(self.rThread)
        self.rThread.started.connect(self.roadRet.ret)
        self.roadRet.finished.connect(self.check_if_road_exists)
        self.rThread.start()
        self.loadingRetrieve = ProcessingDataUi()
        
        # data = res.json()
        # self.dataRoadGlobal = res.json()
        
    # check if those fetch id's are existing
    def check_if_road_exists(self, response):
        self.data = response.json() # all road infos, but without road-captured
        self.ids_to_be_fetched = []
        self.existing_roads = []
        for x in range(len(self.data)):
            if not path.exists("images/"+ self.data[x]['roadID']+".jpg"): # check if image is missing/not existing in local
                self.ids_to_be_fetched.append(self.data[x]['roadID']) # append to list of ids to be fetched
            else:
                self.existing_roads.append(self.data[x])
        self.data = self.existing_roads
        self.rThread.quit() # end Qthread
        
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        # thread for fetching only roads that doesn't exist in ROOT/Client/images/
        self.newThread = QThread()
        self.gRoad = ProcessData(action= '/RoadFetch', type=4, ids_to_be_fetched= json.dumps(self.ids_to_be_fetched), h=headers)
        self.gRoad.moveToThread(self.newThread)
        self.newThread.started.connect(self.gRoad.ret)
        self.gRoad.finished.connect(self.getAllRoad)
        self.newThread.start()
    
    # execute when all roads were fetched 
    def getAllRoad(self, response):
        self.newThread.quit()
        # print('done retrieve')
        toAppend = self.data
        if len(response.json()) >= 1 : # if response has something to append
            for r in response.json():
                toAppend.append(r)
                
        self.data = self.dataRoadGlobal = toAppend
        self.prevSelectedImage=NULL
        
        
        self.roadAddress = []
        self.dThread = QThread()
        self.dRoad = Decoder(self, len(self.data), self.data)
        self.dRoad.moveToThread(self.dThread)
        self.dThread.started.connect(self.dRoad.roadCapturedDecoder)
        self.dRoad.finished.connect(self.roadDisplay)
        self.dThread.start()
        
        
    
    def roadDisplay(self):
        if ((len(self.data)%2)==0):
            row = self.roadCard(self.data,len(self.data))
        else:
            length=len(self.data)-1
            # print(length)
            row = self.roadCard(self.data,length)
            self.frame= QtWidgets.QFrame(self.mainArea)    #create a Qframe for container
            self.frame.setObjectName(str(self.data[len(self.data)-1]['roadID']))       #set Qframe objectName or class
            self.objName=self.frame.objectName() 
            #print(self.objName)
            self.frame.setMaximumSize(QtCore.QSize(301, 1000))  #maximum size of container
            self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)  
            self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
            self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
            self.verticalLayout.setObjectName("verticalLayout")
            self.labelImage = QtWidgets.QLabel(self.frame)
            self.labelImage.setMaximumSize(QtCore.QSize(16777215, 167))
            self.labelImage.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.labelImage.setMouseTracking(True)
            self.labelImage.setFocusPolicy(QtCore.Qt.ClickFocus)
            self.labelImage.setText("") #emptying text 
            self.labelImage.setPixmap(QtGui.QPixmap(self.roadAddress[-1]))   #get show Image inside labelImage
            self.labelImage.setScaledContents(True)
            self.labelImage.setObjectName("label")  #set 
            self.verticalLayout.addWidget(self.labelImage)
            self.label = QtWidgets.QLabel(self.frame)
            self.label.setText(str(self.data[len(self.data)-1]['roadName']))#Assign file label
            self.labelImage.mousePressEvent =lambda event, data=self.data: self.selectImage(event,data[len(data)-1])  #mouse Event 
            self.verticalLayout.addWidget(self.label, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
            self.gridLayout.addWidget(self.frame,row+1,0,1,1) #added the frame inside grid layout   \
        
        # show window here if done
        self.dThread.quit()
        self.loadingRetrieve.closeWindow()
        self.show()
        
    
    def roadCard(self,data,length):
        # print(length)
        x=0     #initialize x for items in each row
        row=0   #initialize row
        while x < length:
                for y in range(2):                
                    self.frame= QtWidgets.QFrame(self.mainArea)    #create a Qframe for container
                    self.frame.setObjectName(str(data[x]['roadID']))       #set Qframe objectName or class
                    self.objName=self.frame.objectName() 
                    #print(self.objName)
                    self.frame.setMaximumSize(QtCore.QSize(301, 1000))  #maximum size of container
                    self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)  
                    self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
                    self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
                    self.verticalLayout.setObjectName("verticalLayout")
                    self.labelImage = QtWidgets.QLabel(self.frame)
                    self.labelImage.setMaximumSize(QtCore.QSize(16777215, 167))
                    self.labelImage.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                    self.labelImage.setMouseTracking(True)
                    self.labelImage.setFocusPolicy(QtCore.Qt.ClickFocus)
                    self.labelImage.setText("") #emptying text 
                    self.labelImage.setPixmap(QtGui.QPixmap(self.roadAddress[x]) )  #get show Image inside labelImage
                    self.labelImage.setScaledContents(True)
                    self.labelImage.setObjectName("label")  #set 
                    self.verticalLayout.addWidget(self.labelImage)
                    self.label = QtWidgets.QLabel(self.frame)
                    self.label.setText(str(data[x]['roadName']))#Assign file label
                    self.labelImage.mousePressEvent =lambda event, x=x: self.selectImage(event,data[x])  #mouse Event 
                    self.verticalLayout.addWidget(self.label, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
                    self.gridLayout.addWidget(self.frame,row,y,1,1) #added the frame inside grid layout
                    x=x+1       #iterate x
                row=row+1       #iterate row
        return row
    
    def loading(self):
        self.flagRoad= True
         # saving roi to txt file for evaluation
        f = open("roi.txt", "w")
        f.write(self.selected['roadBoundaryCoordinates'])
        f.close()
        self.selectedROI= json.loads(self.selected['roadBoundaryCoordinates'])
        self.selectedROI= numpy.asarray(self.selectedROI,dtype=numpy.int32)
        roadAddressReading = "images/"+ self.selected['roadID'] + ".jpg"
        self.selectedRoadImage  = roadAddressReading
        self.selectedRoadID = self.selected['roadID']
        self.selectedRoadName = self.selected['roadName']
        self.settingUpRoad.emit()
        self.close()
 
    def selectImage(self,event,x):
        if self.prevSelectedImage != NULL:         #border of previous selected image is set to none  
            self.newFrame=self.mainArea.findChild(QtWidgets.QFrame,self.prevSelectedImage)
            self.newFrame.setStyleSheet("#label{border:none}")

        
        self.newFrame=self.mainArea.findChild(QtWidgets.QFrame,x['roadID'])#find child in mainArea with object name 
        self.newFrame.setStyleSheet("#label{border:2px solid white}")  #add border to image
        self.btnConfirm.setEnabled(True)                    #btnConfirm enable
        self.btnDelete.setEnabled(True)
        self.btnDelete.setStyleSheet("color:white;border:2px solid white") #add css on btnConfirm
        self.btnConfirm.setStyleSheet("color:white;border:2px solid white") #add css on btnConfirm
        self.mainArea.setStyleSheet("QFrame 2{\n"
            "border:5px solid white;}\n")
        self.prevSelectedImage= x['roadID']
        self.selected = x
        # print(x)
        

    def dropRoad(self):
        a=str(self.selected['roadID'])
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {"roadID": a}

        self.delThread = QThread()
        self.delRoad = ProcessData(action= '/RoadDelete', type=3, d= data, h = headers )
        self.delRoad.moveToThread(self.delThread)
        self.delThread.started.connect(self.delRoad.ret)
        self.delRoad.finished.connect(self.finishedDelRoad)
        self.delThread.start()
        self.loadData = ProcessingDataUi()
        os.remove('images/' + a+'.jpg')
    
    def finishedDelRoad(self, response):
        self.delThread.quit()
        #reload ui and buttons
        uic.loadUi(PATH+'/roadSetUp_phase1.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)      #removing Title bar
        #self.label.mousePressEvent = self.selectImage   #mouse Event for Qlabel
        self.btnNew.clicked.connect(self.switch_window.emit)    #Showing Draw road Ui
        self.btnCancel.clicked.connect(self.close)          #close window
        self.btnConfirm.clicked.connect(self.loading)       #Loading Ui
        self.btnDelete.clicked.connect(self.dropRoad)

        self.check_if_road_exists(response) # add new roads
        self.update()
        self.repaint()
        
        self.loadData.closeWindow()
        
        


#violation Record table
class TableUi(QtWidgets.QMainWindow):
    switch_window = QtCore.pyqtSignal()


    def __init__(self, window):
        super(TableUi, self).__init__()
        uic.loadUi(PATH+'/tableUi.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
       
        _translate = QtCore.QCoreApplication.translate
        self.w = window
        self.vioThread = QThread()
        self.getVio = ProcessData(action= '/ViolationFetchAll', type=1)
        self.getVio.moveToThread(self.vioThread)
        self.vioThread.started.connect(self.getVio.ret)
        self.getVio.finished.connect(self.finishedGetVio)
        self.vioThread.start()
        self.loadData = ProcessingDataUi()
        
        # res = requests.get(url = baseURL + "/ViolationFetchAll")
        # data = res.json()
        # self.dataViolationGlobal = res.json()
    
    def finishedGetVio(self, response, f = None):
        self.vioThread.quit()
        self.loadData.closeWindow()
        if f:
            self.data = response
            self.dataViolationGlobal = response
        else:
            self.data = response.json()
            self.dataViolationGlobal = response.json()
        # self.tableWidget.setRowCount(5) 
        # self.tableWidget.setItem(0,0, QTableWidgetItem("Name"))
        self.tableWidget.setRowCount(len(self.data))
        for i in range(len(self.data)):
            self.tableWidget.setItem(i,0, QTableWidgetItem(self.data[i]['vehicleID']))
            self.tableWidget.item(i,0).setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
            self.tableWidget.setItem(i,1, QTableWidgetItem(self.data[i]['violationID']))
            self.tableWidget.item(i,1).setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
            self.tableWidget.setItem(i,2, QTableWidgetItem(self.data[i]['roadName']))
            self.tableWidget.item(i,2).setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
            self.tableWidget.setItem(i,3, QTableWidgetItem(self.data[i]['lengthOfViolation']))
            self.tableWidget.item(i,3).setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)        
            self.tableWidget.setItem(i,4, QTableWidgetItem(str(self.data[i]['startDateAndTime'])))
            self.tableWidget.item(i,4).setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
            self.tableWidget.setItem(i,5, QTableWidgetItem(str(self.data[i]['endDateAndTime'])))
            self.tableWidget.item(i,5).setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
            #Adding BUtton in each row  
            self.newPlayPanel=QtWidgets.QLabel(self.tableWidget)
            self.newPlayPanel.setMaximumHeight(100)
            #self.newPlayPanel.setStyleSheet("border:2px solid red")
            self.newPlayPanel.setPixmap(QtGui.QPixmap(self.data[i]['vehicleCrop']))#image of detected vehicle
            self.newPlayPanel.setScaledContents(True)
            self.newBtnPlay=QtWidgets.QPushButton(self.newPlayPanel)
            self.newBtnDelete=QtWidgets.QPushButton(self.tableWidget)
            self.verticalLayout = QtWidgets.QVBoxLayout(self.newPlayPanel)
            self.verticalLayout.addWidget(self.newBtnPlay, alignment=QtCore.Qt.AlignCenter)
            self.newBtnPlay.setText("")
            self.newBtnDelete.setText("")
            self.newBtnPlay.setStyleSheet("background-color:none;border:none;color:white;")
            self.newBtnDelete.setStyleSheet("background-color:none;border:none;color:white;")
            ##
            #Adding PLay icon and Delete icon 
            icon1 = QtGui.QIcon()
            icon2 = QtGui.QIcon()
            icon1.addPixmap(QtGui.QPixmap(PATH+"/icon/playCircleArrow.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            icon2.addPixmap(QtGui.QPixmap(PATH+"/icon/deleteIcon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.newBtnPlay.setIcon(icon1)
            self.newBtnDelete.setIcon(icon2)
            self.newBtnPlay.setIconSize(QtCore.QSize(25, 25))
            self.newBtnDelete.setIconSize(QtCore.QSize(14,15))
            self.tableWidget.setCellWidget(i,6,self.newPlayPanel)
            # self.tableWidget.setCellWidget(i,6,self.newBtnPlay)
            self.tableWidget.setCellWidget(i,7,self.newBtnDelete)
            self.newBtnDelete.clicked.connect(lambda ch, i=i: self.dropViolation(self.data[i]['violationID']))
            self.newBtnPlay.clicked.connect(lambda ch, i=i: self.replayViolation(i))
        self.btnDone.clicked.connect(self.close)
        self.tableWidget.resizeRowsToContents()
        self.show()
    
    def dropViolation(self,violation_ID):
        a=str(violation_ID)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {"violationID": a}
        
        self.delThread = QThread()
        self.delVio = ProcessData(action= '/ViolationDelete', type=3, d = data, h = headers)
        self.delVio.moveToThread(self.delThread)
        self.delThread.started.connect(self.delVio.ret)
        self.delVio.finished.connect(self.finishedDelViolation)
        self.delThread.start()
        self.loadData = ProcessingDataUi()
        # r = requests.delete(url = baseURL + "/ViolationDelete",json=data,headers=headers )
        # print(r)
        # self.update

        
    def finishedDelViolation(self, response):
        self.delThread.quit()
        #reload ui and buttons
        uic.loadUi(PATH+'/tableUi.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        _translate = QtCore.QCoreApplication.translate

        self.finishedGetVio(response)
        self.update()
        self.loadData.closeWindow()

    def replayViolation(self,i):
        # self.close()
        self.w.window.isViolation = True
        self.w.window.violationIndex = i
        self.w.window.activePlayback()
        
        
#main Window
class MainUi(QtWidgets.QMainWindow):
    switch_window = QtCore.pyqtSignal()
    roadSwitch=QtCore.pyqtSignal()
    logout=QtCore.pyqtSignal()
    addIp=QtCore.pyqtSignal()
    addCctv=QtCore.pyqtSignal()
    actPlayBack=QtCore.pyqtSignal()
    actWatch = QtCore.pyqtSignal()
    
    def __init__(self, window):
        super(MainUi, self).__init__()
        uic.loadUi(PATH+'/frontEndUi.ui', self)
        self.showMaximized()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.topInfo.hide()
        self.selected="" 
        self.isViolation = False
        self.vidFile = ''
        self.tempfile = ''
        self.w = window
        self.violationIndex = -12345678
        self.btnRecord.clicked.connect(self.switch_window.emit)
        self.btnLogout.clicked.connect(self.logout.emit)
        self.btnIpAdd.clicked.connect(self.addIp.emit)
        self.btnCctv.clicked.connect(self.addCctv.emit)
        self.btnPlayback.clicked.connect(self.activePlayback)
        self.btnWatch.clicked.connect(self.activeWatch)
       
        #self.date=QDateTime.currentDateTime()
        #self.dateDay.setDate(self.date.date()
        self.roadSetUpImage.setMaximumSize(1280,720)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.roadSetUpImage)
        self.image_main=myQLabel(self.roadSetUpImage)
        self.verticalLayout.addWidget(self.image_main)
        self.eraserTool.clicked.connect(self.eraseSelected)
        self.drawTool.clicked.connect(self.drawSelected)
        self.drawTool.setStyleSheet("background-color:#1D1F32")
        self.addSize.clicked.connect(self.addSizeFunction)
        self.subSize.clicked.connect(self.subSizeFunction)
        validatorInt=QIntValidator(0,500)
        self.sizeLabel.setValidator(validatorInt)
        self.sizeLabel.returnPressed.connect(self.enterSize)
        self.shortcut_DecreaseSize=QtWidgets.QShortcut(QtGui.QKeySequence("["),self)
        self.shortcut_DecreaseSize.activated.connect(self.subSizeFunction)
        self.shortcut_IncreaseSize=QtWidgets.QShortcut(QtGui.QKeySequence("]"),self)
        self.shortcut_IncreaseSize.activated.connect(self.addSizeFunction)
        timer = QTimer(self)
		# adding action to timer
        timer.timeout.connect(self.showTime)

		# update the timer every second
        timer.start(1000)
        self.playbackKeys = ['playbackID', 'playbackVideo','duration', 'roadName', 'dateAndTime']
        self.playbackInfo = {k: [] for k in self.playbackKeys}
        
	# method called by timer
    def showTime(self):

		# getting current time
        current_time = QTime.currentTime()
        current_date=QDate.currentDate()
		# converting QTime object to string
        label_time = current_time.toString('h:mm AP')

		# showing it to the label
        self.dateTime.setText(label_time)
        self.dateDay.setDate(current_date)
        self.dateMonthYear.setDate(current_date)

    
    
    def activePlayback(self):
        self.image.setMinimumSize(QtCore.QSize(0, 400))
        self.image.setMaximumSize(QtCore.QSize(1280, 720))
        self.stackedWidget.setCurrentWidget(self.playbackPage)
        self.btnWatch.setStyleSheet('background-color:none;border:none')
        self.btnRoadSetup.setStyleSheet('background-color:none;border:none')
        self.btnPlayback.setStyleSheet("color:white;font-size:14px;background-color:#1D1F32;border-left:3px solid #678ADD;")
        self.actPlayBack.emit()
        
    def activeWatch(self):
        self.stackedWidget.setCurrentWidget(self.watchingPage)
        self.btnPlayback.setStyleSheet('background-color:none;border:none')
        self.btnRoadSetup.setStyleSheet('background-color:none;border:none')
        self.btnWatch.setStyleSheet("color:white;font-size:14px;background-color:#1D1F32;border-left:3px solid #678ADD;")
        self.actWatch.emit()
    #Function display Video    
    def setUpVideo(self): #Initialize click event
        temp = self.vidFile
        self.vidFile=QFileDialog.getOpenFileName(None,'Select a video', PATH+'/../','video (*.mp4);;(*.avi);;(*.mov);;(*.mkv);;(*.wmv);;(*.mpg);;(*.mpeg);;(*.m4v)')
        
        if self.vidFile[0] != '':
            self.tempfile = temp
            self.vidFile = self.vidFile[0]
            self.roadSwitch.emit()
        else:
            self.vidFile = temp
        
    def activeRoadSetUp(self, roadLoad):
        self.stackedWidget.setCurrentWidget(self.roadSetupPage)
        self.btnPlayback.setStyleSheet('background-color:none;border:none')
        self.btnWatch.setStyleSheet('background-color:none;border:none')
        self.btnRoadSetup.setStyleSheet("color:white;font-size:14px;background-color:#1D1F32;border-left:3px solid #678ADD;")
        self.image_main.image = QtGui.QImage("images/road.jpg") 
        self.image_main.drawROI(self.w.ROI, self.w.roadImage, roadLoad)
        
        
    def enterSize(self):
        value=self.sizeLabel.text()
        self.image_main._size=int(value)
        if self.image_main.eraser_selected==True:
            self.cursorForEraser()
    def subSizeFunction(self):
        self.image_main._size=self.image_main._size-1
        self.sizeLabel.setText(str(self.image_main._size))
        if self.image_main.eraser_selected==True:
            self.cursorForEraser()
    def addSizeFunction(self):
        self.image_main._size=self.image_main._size+1
        self.sizeLabel.setText(str(self.image_main._size))
        if self.image_main.eraser_selected==True:
            self.cursorForEraser()
    def drawSelected(self):
        self.drawTool.setStyleSheet("background-color:#1D1F32")
        self.eraserTool.setStyleSheet("background-color:none")
        self.image_main.eraser_selected=False
        self.image_main.setCursor(QtGui.QCursor((QtCore.Qt.ArrowCursor)))

    def eraseSelected(self):
        self.image_main.eraser_selected=True
        self.cursorForEraser()
        self.eraserTool.setStyleSheet("background-color:#1D1F32")
        self.drawTool.setStyleSheet("background-color:none")
        #self.image_main.setOverrideCursor(cursor)
    def cursorForEraser(self):
        
        pixmap = QtGui.QPixmap(QtCore.QSize(1, 1)*self.image_main._size)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 2))
        painter.drawRect(pixmap.rect())
        painter.end()
        cursor = QtGui.QCursor(pixmap)
        self.image_main.setCursor(cursor)

        

    #Function display Video    
    
       

    def savePlayback(self,data):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        
        self.saveThread = QThread()
        self.savePlay = ProcessData(action= '/PlaybackInsert', type=2, d= json.dumps(data), h = headers )
        self.savePlay.moveToThread(self.saveThread)
        self.saveThread.started.connect(self.savePlay.ret)
        self.savePlay.finished.connect(self.finishedSavePlay)
        self.saveThread.start()
        self.loadData = ProcessingDataUi()
        # r = requests.post(url = baseURL + "/PlaybackInsert",data=json.dumps(data),headers=headers)
        # print(r)
    
    def finishedSavePlay(self, _):
        self.saveThread.quit()
        self.loadData.closeWindow()
        
class welcome(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal()
    def __init__(self):
        super(welcome, self).__init__()
        uic.loadUi(PATH+'/welcomeUi.ui', self)
        self.btnLogin.clicked.connect(self.goToLogin)
        self.btnCancel.clicked.connect(self.closeWindow)
        self.setWindowFlag(Qt.FramelessWindowHint)      
    def goToLogin(self):
        self.switch_window.emit()
    def closeWindow(self):
        self.close()
        exit()

"""Class for navigating"""      
class Controller:
    EXIT_CODE_REBOOT = -12345678
    def __init__(self):
        pass

    def restart(self): # restart app
        try:
            self.detthread.quit()
        except:
            print('not running det')
        app.exit(Controller.EXIT_CODE_REBOOT)
        
    def show_login(self):
        self.login =welcome()
        self.login.switch_window.connect(self.show_main)
        self.login.show()
        
    def show_main(self):
        self.window = MainUi(self)
        self.window.switch_window.connect(self.showTable)
        self.window.roadSwitch.connect(self.showRoadSetup)
        self.window.addIp.connect(self.showUseIpAdd)
        self.window.btnRoadSetup.clicked.connect(self.showRoadSetup)
        self.window.btnT_ipAdd.clicked.connect(self.showUseIpAdd)
        self.window.btnT_insertVideo.clicked.connect(self.addVideo)
        self.window.btnT_cctv.clicked.connect(self.showUseCctv)
        self.window.logout.connect(self.show_logout)
        self.window.addCctv.connect(self.showUseCctv)
        self.window.btnAddVideo.clicked.connect(self.addVideo)
        self.window.btnDone_paint.clicked.connect(self.settingUpRoad_From_paint)
        self.window.btnCancel_paint.clicked.connect(self.showRoadSetup)
        self.window.actPlayBack.connect(self.playBack)
        self.window.actWatch.connect(self.watch)
        # check login info here
        self.check_credentials()
            
    def check_credentials(self):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {
            'username' : self.login.userName.text(),
            'password' : self.login.password.text(),
        }
        self.login_thread = QThread()
        self.user_login = ProcessData(action= '/UserFetch', type=5, credentials=json.dumps(data), h = headers)
        self.user_login.moveToThread(self.login_thread)
        self.login_thread.started.connect(self.user_login.ret)
        self.user_login.finished.connect(self.is_credentials_exist)
        self.login_thread.start()
        self.load_login = ProcessingDataUi()
        
        
    def is_credentials_exist(self, response):
        self.load_login.close()
        self.login_thread.quit()
        res = response.json()
        if res['result']:
            self.window.show()
            self.login.close()
            
            # check if path exists for road images to be saved
            newpath = str(PATH)+"/images/" 
            if not os.path.exists(newpath):
                os.makedirs(newpath)
                
        else:
            ctypes.windll.user32.MessageBoxW(0, "Wrong Credentials", "Login Error", 0)
    def watch(self):
        try:
            self.getVid.stop()
            self.nthread.quit()
            self.pause = True
            self.window.btnPlay.disconnect()
            self.initDet.det.dets.view_img = True
        except Exception as er:
            pass
        
    def playBack(self):
        try:
            try:
                self.window.btnPlay.disconnect()
                self.getVid.stop()
                self.nthread.quit()
                self.nthread.wait()
                self.pause = True
                print('aaaaaaaaaa',self.window.violationIndex)
            except Exception as er:
                print('error ini', er)
                pass
            
            currFile = str(self.window.vidFile).split('/')[-1]
            try:
                vioFile = str(self.newWin.data[self.window.violationIndex]['violationRecord']).split('\\')[-1]
            except:
                vioFile = None
            if self.window.isViolation and currFile != vioFile:
                # playback from violation record
                print('in violation')
                try:
                    self.initDet.det.dets.view_img = False
                except:
                    pass
                self.pause = True
                self.nthread = QThread()
                self.getVid = videoGet(self)
                self.getVid.moveToThread(self.nthread)
                self.nthread.started.connect(self.getVid.runFromViolation)
                self.getVid.finished.connect(self.nthread.quit)
                self.nthread.finished.connect(self.finishedPlayBack) # execute when the task in thread is finised
                self.getVid.imgUpdate.connect(self.update_pb_image)
                self.getVid.fileNotExistSignal.connect(self.missingVideo)
                self.nthread.start()
  
                
            else: 
                print('in live')
                # playback from currently playing video
                self.frameStart = int(self.newWin.data[self.window.violationIndex]['frameStart']) if vioFile is not None else 0
                self.initDet.det.dets.view_img = False
                self.vQueue = self.initDet.det.dets.vidFrames.copy()
                self.pause = True
                self.nthread = QThread()
                self.getVid = videoGet(self)
                self.getVid.moveToThread(self.nthread)
                self.nthread.started.connect(self.getVid.run)
                self.getVid.finished.connect(self.nthread.quit)
                self.nthread.finished.connect(self.finishedPlayBack) # execute when the task in thread is finised
                self.getVid.imgUpdate.connect(self.update_pb_image)
                self.nthread.start()
        except Exception as er:
            print('error this',er)
            pass
        
        self.window.btnPlay.clicked.connect(self.pauseOrPlay)
    
    def missingVideo(self):
        self.window.isViolation = False
        self.window.violationIndex = -12345678
        ctypes.windll.user32.MessageBoxW(0, "File not Found", "Nothing to play", 0)
    
    def pauseOrPlay(self):
        print('pause or play have been called')
        try:
            self.pause = not self.pause
            # print('Pause = ',  self.pause)
            self.getVid.playOrPause(self.pause)
        except AttributeError:
            self.window.btnPlay.disconnect()
            ctypes.windll.user32.MessageBoxW(0, "Please insert a video first", "Nothing to play", 0)
            
    def finishedPlayBack(self):
        self.window.isViolation = False
        self.window.violationIndex = -12345678
        print('finished playing video')
        
        

    def update_pb_image(self, qim):
        self.window.image.setPixmap(qim)
     
    def settingUpRoad_From_paint(self):
        #change roi here [..]
        img_orig = self.QImageToCvMat(self.window.image_main.draw.pixmap().toImage())
        img = cv2.cvtColor(img_orig, cv2.COLOR_BGR2GRAY)
        cnts, _ = cv2.findContours(img,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        self.ROI = cnts
        
        #change road image here
        alpha = 0.25
        self.roadImage = cv2.addWeighted(self.roadImage,1-alpha, img_orig, alpha, 0)
        self.showFinishingUi()
    
    def QImageToCvMat(self,incomingImage):

        incomingImage = incomingImage.convertToFormat(QtGui.QImage.Format.Format_RGB32)

        width = incomingImage.width()
        height = incomingImage.height()

        assert incomingImage.depth() == 32, "unexpected image depth: {}".format(incomingImage.depth())
        
        ptr = incomingImage.bits().asstring(width * height * incomingImage.depth()//8)
        arr = np.frombuffer(ptr, dtype=np.uint8).reshape((height, width, incomingImage.depth()//8)) 
        
        arr = cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)
        return arr

    def showUseCctv(self):
        self.cctvWidget=CctvWindow()
        self.window.selected=1
        self.cctvWidget.show()
        self.cctvWidget.btnDone.clicked.connect(self.setCctvSelected)
    def setCctvSelected(self):
        self.showRoadSetup()
        self.cctvWidget.close()

    def showUseIpAdd(self):
        self.IpAddWindow=IpAddWindow()
        self.IpAddWindow.btnDone.clicked.connect(self.setIpSetected)         
        self.IpAddWindow.show()
    def addVideo(self):
        self.window.selected=3
        # self.showRoadSetup()
        self.window.setUpVideo()

    def setIpSetected(self):
        self.ipAdd=self.IpAddWindow.textBox.text()
        self.window.selected=2
        
        self.checkIP = QThread()
        self.checkIPObject = ProcessData(action= self.ipAdd, type=6)
        self.checkIPObject.moveToThread(self.checkIP)
        self.checkIP.started.connect(self.checkIPObject.ret)
        self.checkIPObject.finishedIP.connect(self.finishedCheckingIP)
        self.checkIP.start()
        self.loadingIP = ProcessingDataUi()
     
        
    def finishedCheckingIP(self, response): 
        print('finsished checing ip')
        self.checkIP.quit()
        self.loadingIP.close() 
        temp = self.window.vidFile
        if response == 1:
            self.window.tempfile = temp
            self.window.vidFile = self.ipAdd
            self.IpAddWindow.close()
            self.showRoadSetup()
        else:
            ctypes.windll.user32.MessageBoxW(0, "Invalid IP address or Connection Problem", "Invalid Input", 0)       

    def showTable(self):
        self.newWin=TableUi(self)
        # self.newWin.show()
    def showRoadSetup(self):
        # before showing road, execute background modelling and automatic road detection, must be loading
        
        self.road = RoadSetUp1(self)
        self.road.switch_window.connect(self.show_RoadPaint) # for btn new
        # disable new if vidfile has value
        # # self.road.selectImage.connect(self.select)
        self.road.settingUpRoad.connect(self.showFinishingUi) # for btn confirm new
    def show_RoadPaint(self):
        if self.window.vidFile:
            self.road.close()
            self.road.disconnect()
            self.roadLoad = roadSettingUp() # for loading setting up road
            
            # run extraction of bg and road
            self.roadThread = QThread()
            self.bgAndRoad = Worker(self)
            self.bgAndRoad.moveToThread(self.roadThread)
            self.roadThread.started.connect(self.bgAndRoad.runBG)
            self.bgAndRoad.finished.connect(self.roadThread.quit)
            self.roadThread.finished.connect(self.finishedInBGModelAndRoad) # execute when the task in thread is finised
            self.roadThread.start()
            # print("started")
            # print(threading.active_count())
        else:
            ctypes.windll.user32.MessageBoxW(0, "Please insert a video first", "Empty Video file", 0)
    
    # function to call when the process of bg modelling and road extraction is done using thread
    def finishedInBGModelAndRoad(self):
        
        self.roadImage, self.ROI =  self.bgAndRoad.bgImage,  self.bgAndRoad.ROI
        if self.roadImage is not NULL:
            self.window.activeRoadSetUp(self.roadLoad)
            # self.roadPaint=RoadSetUpPaint()
            # self.roadPaint.switch_window.connect(self.showFinishingUi) # for btn done
            # self.roadPaint.show()
        else:
            print("ERROR: An error occure while extracting the road and background model")
            exit()
            
    def show_logout(self):
        self.logout_Ui=LogoutUi()
        self.logout_Ui.show()
        self.logout_Ui.confirmLogout.connect(self.closeWindow)
    def closeWindow(self):
        # stop detection
        try:
            self.initDet.det.dets.stop()
            self.thread.wait()
        except:
            pass
        self.restart()

    def showFinishingUi(self):
        if self.window.vidFile: # check if there's a current vid file
            # initialize detection
            try:
                # fot btn confirm
                if self.road.flagRoad:
                    self.ROI = self.road.selectedROI
                    self.road.flagRoad = False
                    self.roadImage = cv.imread(self.road.selectedRoadImage)
                    self.roadIDGlobal = self.road.selectedRoadID
                    try:
                        # if detection is currently running
                        self.initDet.det.dets.changeROI(self.road.selectedROI)
                        self.window.label.setText(self.road.selectedRoadName)
                        # since topInfo only shows if detection is running, check if there is a file changed here...
                        if self.window.vidFile != self.window.tempfile and self.window.tempfile != '': #file changed
                            print(f'file changed in confirm {self.window.vidFile}  and {self.window.tempfile}')
                            self.initDet.det.dets.stop()
                            self.initializeDetection()
                            self.window.tempfile = ''
                        
                        print('ROI has been changed in running confirm')
                    except:
                        self.initializeDetection()
                        self.window.activeWatch()
                        pass
                    # print('selected road image shape', self.roadImage.shape)
            except:
                # for btn new
                self.ROI = self.expandROI()
                try:
                    # if detection is currently running
                    self.initDet.det.dets.changeROI(self.ROI)
                    self.window.label.setText(self.window.roadNameTextbox.text())
                    print('ROI has been changed in running new')
                except:
                    # if it is not running, pass then execute code below
                    pass
                #setting up the roadID
                if self.road.dataRoadGlobal: #determining if the dataRoadGlobal is empty
                    roadIDLatest=str(self.road.dataRoadGlobal[len(self.road.dataRoadGlobal)-1]['roadID']).split("-")
                    # print(roadIDLatest)
                    intRoadID=int(roadIDLatest[1]) + 1
                    roadID="R-" + str(intRoadID).zfill(7)
                    # print(roadID)
                    
                else:
                    roadID = "R-0000001"
                    
                cv.imwrite(str(PATH)+"/images/{}.jpg".format(roadID), self.roadImage) #writing the image with ROI to Client/images path
                data = {
                    'roadID' : roadID,
                    'roadName' : self.window.roadNameTextbox.text(),
                    'roadCaptured' :  self.roadImage.tolist(),
                    'roadBoundaryCoordinates' : pd.Series(self.ROI).to_json(orient='values')
                }
                
                # print(data['roadCaptured'])
                self.roadIDGlobal = roadID
                self.saveRoad(data)
        else:
            ctypes.windll.user32.MessageBoxW(0, "Please insert a video first", "Empty Video file", 0)
    
    def expandROI(self):
        min_size = int(self.roadImage.shape[0]*self.roadImage.shape[1]*0.05)
        contours = self.ROI
        bg = np.zeros_like(self.roadImage) 
        
        for contour in contours:
            area = cv2.contourArea(contour) 
            print(f'area {area} < {min_size*0.5} : {area<min_size*0.5}')
            if area < min_size:
                continue
             # draw the contours that are larger than 5% of img size 
            if area > (0.5*self.roadImage.shape[0]*self.roadImage.shape[1]) or len(contours) > 1:
                kernel_size = 35
            else:
                kernel_size = 80
            cv2.drawContours(bg, [contour], -1, (255,255,255), thickness= -1)

        # road_surface = cv2.addWeighted(self.roadImage, 1-0.25, bg, 0.25, 0)
        bg = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)
        kernel  = np.ones((kernel_size,kernel_size), np.uint8)
        dilated = cv2.dilate(bg, kernel, iterations=1)
            
        # pass 1
        smooth_mask_blurred   = cv2.GaussianBlur(dilated, (21,21), 0)
        _, smooth_mask_threshed1  = cv2.threshold(smooth_mask_blurred, 128, 255, cv2.THRESH_BINARY)
        
        # pass 2
        smooth_mask_blurred   = cv2.GaussianBlur(smooth_mask_threshed1, (21,21), 0)
        _, smooth_mask_threshed2 =  cv2.threshold(smooth_mask_blurred, 128, 255, cv2.THRESH_BINARY)
            
        cnts, _ = cv2.findContours(smooth_mask_threshed2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        return cnts
    
    #this function will request post to save the data to the database
    def saveRoad(self,data):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        self.saveRoadThread = QThread()
        self.sRoad = ProcessData(action= '/RoadInsert', type=2, d= json.dumps(data), h = headers )
        self.sRoad.moveToThread(self.saveRoadThread)
        self.saveRoadThread.started.connect(self.sRoad.ret)
        self.sRoad.finished.connect(self.finishedSaveRoad)
        self.saveRoadThread.start()
        self.loadData = ProcessingDataUi()
        # save road to local
        # r = requests.post(url = baseURL + "/RoadInsert",data=json.dumps(data),headers=headers)
        # print(r)

    def finishedSaveRoad(self,_):
        # print('road saved')
        self.saveRoadThread.quit()
        
        # resetting pixmap
        pixmap = QPixmap(self.window.image_main.parentDraw.width(),self.window.image_main.parentDraw.height()) # width, height
        newPixmap=pixmap.scaled(1280,720)#scaled the Pixmap
        newPixmap.fill(Qt.transparent)
        self.window.image_main.draw.setPixmap(newPixmap)
        self.loadData.closeWindow()
        self.window.activeWatch()
        try:
            if not self.initDet.det.dets.stopped: # if detection is not stopped
                if self.window.vidFile != self.window.tempfile and self.window.tempfile != '': #file changed
                    print('file changed in new', self.window.vidFile, self.window.tempfile)
                    self.initDet.det.dets.stop()
                    self.initializeDetection()
                    self.window.tempfile = ''

                pass
        except:
            self.initializeDetection()
        
        
    def initializeDetection(self):
        self.windowFinishing=FinishingUi()
        self.thread = QThread()
        self.initDet = Worker(self)
        self.initDet.moveToThread(self.thread)
        self.thread.started.connect(self.initDet.initDet)
        self.initDet.finishedInitDet.connect(self.finishedInitDet) # execute when the task in thread is finised
        self.thread.start()
    # this function will be executed when finished initializing detection and tracking models
    def finishedInitDet(self, response):
        if self.initDet.det.dets.nflag:
            self.thread.quit()
            self.windowFinishing.closeWindow() # close loading
            self.getViolationRecord = response.json()
            print("finished initializing detection models")
            try:
                self.window.label.setText(self.road.selectedRoadName)
            except:
                self.window.label.setText(self.window.roadNameTextbox.text())
            self.window.verticalLayout_11.addWidget(self.window.frameWatch)#removing center aligment of frameWatch
            self.window.btnAddVideo.hide()
            self.window.labelScreen.setMinimumSize(QtCore.QSize(0, 400))
            self.window.frameButtons_2.hide()
            self.window.topInfo.show()
            self.activeButton()
            
            

            # run detection here on separate thread
            self.detthread = QThread()
            self.runDets = Worker(self)
            self.runDets.moveToThread(self.detthread)
            self.detthread.started.connect(self.runDets.runDet)
            self.runDets.finished.connect(self.detthread.quit)
            self.detthread.finished.connect(self.finishedrunDet) # execute when the task in thread is finised
            self.runDets.imgUpdate.connect(self.update_image)
            self.detthread.start()
            
        else:
            print("ERROR: An error occured while performing detection")
            exit()
            
    def update_image(self, qim):
        self.window.labelScreen.setPixmap(qim)
           
    # this function will execute when the detection is finished with the video
    def finishedrunDet(self):        
        print("finished detection for this file")
    

        #Closing Road Setting
    def activeButton(self):
        print(self.window.selected)
        if self.window.selected==1:
            self.window.btnT_cctv.setStyleSheet("background-color:#678ADD")
            self.window.btnT_ipAdd.setStyleSheet("background-color:none")
            self.window.btnT_insertVideo.setStyleSheet("background-color:none")
            self.window.Selected.setText("Live CAM Selected:")
            self.window.File.setText("Live")
            self.window.File.setStyleSheet("color:red")
        elif self.window.selected==2:
            self.window.btnT_cctv.setStyleSheet("background-color:none")
            self.window.btnT_ipAdd.setStyleSheet("background-color:#678ADD")
            self.window.btnT_insertVideo.setStyleSheet("background-color:none")
            self.window.Selected.setText("IP Address Selected:")    
            self.window.File.setText(self.ipAdd)
            self.window.File.setStyleSheet("color:#678ADD;")
        elif self.window.selected==3:
            self.window.btnT_cctv.setStyleSheet("background-color:none")
            self.window.btnT_ipAdd.setStyleSheet("background-color:none")
            self.window.btnT_insertVideo.setStyleSheet("background-color:#678ADD")
            self.window.Selected.setText("Video File Selected:")
            self.window.File.setText(self.window.vidFile)
            self.window.File.setStyleSheet("color:#678ADD;")
            

    def select(self):
        print("Select Image")


# classes for worker threads
class Worker(QtCore.QObject):
    finishedInitDet = QtCore.pyqtSignal(requests.models.Response)
    finished = QtCore.pyqtSignal()
    imgUpdate = QtCore.pyqtSignal(QtGui.QPixmap)
    
    def __init__(self, window):
        super(Worker, self).__init__()
        self.w = window
        self.vid = self.w.window.vidFile     

    def runBG(self):
        print('processing road')
        self.bgImage, self.ROI = processRoad(self.vid, PATH)
        self.finished.emit()
        
    def initDet(self):
        self.det = detection(self.vid, self.w)
        response = requests.get(url = baseURL + "/ViolationFetchAll")
        self.finishedInitDet.emit(response)

    def runDet(self):
        # run/start detection
        self.w.initDet.det.dets.run()
        f = 1
        # wait for detection to finish one frame
        while self.w.initDet.det.dets.f == 0:
            print(end='\r')
        # print(threading.active_count())
        while not self.w.initDet.det.dets.stopped:
            if self.w.initDet.det.dets.view_img:
                if f == self.w.initDet.det.dets.f:
                    img = numpy.copy(self.w.initDet.det.dets.frame) #make a copy of frame
                    QtImg = cvImgtoQtImg(img)# Convert frame data to PyQt image format
                    qim = QtGui.QPixmap.fromImage(QtImg)
                    self.imgUpdate.emit(qim)
                    f +=1
                else:
                    print(end='\r')
            else:
                f = self.w.initDet.det.dets.f + 1
                print(end='\r')

        self.finished.emit()
        
        

# class for video playback getting
class videoGet(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    imgUpdate = QtCore.pyqtSignal(QtGui.QPixmap)
    fileNotExistSignal = QtCore.pyqtSignal()
    
    def __init__(self, window):
        super(videoGet, self).__init__()
        self.w = window
        self.pause = self.w.pause
        self.stopped = False
        try:
            self.index = window.window.violationIndex
        except:
            pass
     
        
    def run(self):
        replayVideo = self.w.vQueue[self.w.frameStart:]
        for frame in replayVideo:
            now = time.time()
            if not self.stopped:
                QtImg = cvImgtoQtImg(frame)# Convert frame data to PyQt image format
                qim = QtGui.QPixmap.fromImage(QtImg)
                timediff = time.time() - now
                if (timediff<(1.0/(self.w.initDet.det.dets.sfps))):
                    time.sleep((1.0/(self.w.initDet.det.dets.sfps)) - timediff)

                self.imgUpdate.emit(qim)
            else:
                break
            while self.pause:
                # loop here until pause is lifted
                print('paused',end='\r')
        self.finished.emit()   
        
    def runFromViolation(self):
        file = self.w.newWin.data[self.index]['violationRecord']
        cap = cv2.VideoCapture(file)
        if not cap.isOpened():
            self.fileNotExistSignal.emit()
            return
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(self.w.newWin.data[self.index]['frameStart']))
        
        while True:
            if not self.stopped:
                # Capture frame-by-frame
                ret, frame = cap.read()
                # if frame is read correctly ret is True
                if not ret:
                    print("Can't receive frame (stream end?). Exiting ...")
                    break
                
                # Display the resulting frame
                QtImg = cvImgtoQtImg(frame)# Convert frame data to PyQt image format
                qim = QtGui.QPixmap.fromImage(QtImg)
                time.sleep(1/fps)
                self.imgUpdate.emit(qim)            
            else:
                break
            
            while self.pause:
                # loop here until pause is lifted
                print('paused', end='\r')
        self.finished.emit()  
           
    def stop(self):
        print('stopped')
        self.pause = False
        self.stopped = True  
        
    
    def playOrPause(self, val):
        self.pause = val
            
    
class ProcessData(QtCore.QObject):
    """
    For retrieving \n
    action = 'RoadFetch' / 'RoadDelete'/ etc\n
    type = 1: retrieve, 2: post, 3: delete\n
    \n
    For posting or deleting \n
    action = 'RoadFetch' / 'RoadDelete'/ etc\n
    type = 1: retrieve, 2: post, 3: delete\n
    d = data(json)\n
    h = headers\n
    """
    finished = QtCore.pyqtSignal(requests.models.Response)
    finishedIP = QtCore.pyqtSignal(int)
    
    
    #overloading constructor
    def __init__(self, action, type, d = None, h = None, ids_to_be_fetched = None, credentials = None):
        super(ProcessData, self).__init__()
        if d and h:
            self.data = d
            self.headers = h
        if ids_to_be_fetched and h:
            self.ids_to_be_fetched = ids_to_be_fetched
            self.headers = h
        if credentials and h:
            self.credentials = credentials
            self.headers = h
        self.action = action
        self.type = type
      
        
    def ret(self):
        if self.type == 1: # retrieve
            response = requests.get(url = baseURL + self.action)
            self.finished.emit(response)
        elif self.type == 2: # post
            response = requests.post(url = baseURL + self.action, data=self.data,headers=self.headers)
            self.finished.emit(response)
        elif self.type == 3: # delete
            response = requests.delete(url = baseURL + self.action, json=self.data,headers=self.headers )
            self.finished.emit(response)
        elif self.type == 4: # retrieve with params
            response = requests.get(url = baseURL + self.action, data = self.ids_to_be_fetched , headers=self.headers)
            self.finished.emit(response)
        elif self.type == 5: # retrieve with params
            response = requests.get(url = baseURL + self.action, data = self.credentials , headers=self.headers)
            self.finished.emit(response)
        elif self.type == 6: # retrieve with params
            if 'youtube.com/' in self.action or 'youtu.be/' in self.action:  # if source is YouTube video
                # check_requirements(('pafy', 'youtube_dl==2020.12.2'))
                import pafy
                self.action = pafy.new(self.action).getbest(preftype="mp4").url  # YouTube URL
            cap = cv2.VideoCapture(self.action)
            if cap.isOpened():
                self.finishedIP.emit(1) 
                return
            self.finishedIP.emit(0)
            
        # emit result when done
 
class Decoder(QtCore.QObject):  
    finished = QtCore.pyqtSignal()
    
    def __init__(self, window, len, data):
        super(Decoder, self).__init__()
        self.window = window
        self.len = len
        self.data = data
    
    def roadCapturedDecoder(self):
        for x in range(self.len):
            self.window.roadAddress.append("images/" + self.data[x]['roadID'] + ".jpg")
            if not path.exists("images/"+ self.data[x]['roadID']+".jpg"): #verifying if the file is exist in the directory
                roadReplaced=str(self.data[x]['roadCaptured'].replace("[", "").replace("]","").replace(" ", "")) #eliminating the none number except comma
                roadConverted=numpy.fromstring(roadReplaced, dtype=int, sep=',') #converting from string to number and making it a numpy array
                # print(len(roadConverted))
                roadArr=roadConverted.reshape(720,1280, 3) #reshaping the array to 720xx1280
                # print(numpy.array(roadArr,dtype=numpy.uint32))
                # print(numpy.array(data[0]['roadCaptured'],dtype=numpy.int32))
                
                cv2.imwrite(r'images/{}.jpg'.format(self.data[x]['roadID']),  numpy.array(roadArr,dtype=numpy.int32)) #writing the array to image with datatype int32
        self.finished.emit() 

class Drawer(QtCore.QObject):  
    finished = QtCore.pyqtSignal(QtGui.QPainter, QtGui.QPixmap)
    
    def __init__(self, pts, painter, pm):
        super(Drawer, self).__init__()
        self.pts = pts
        self.painter = painter
        self.pm = pm
        
        
    def draw(self):
        for pt in self.pts:
                self.painter.drawPoint(pt[1],pt[0])
        self.finished.emit(self.painter, self.pm)
if __name__ == '__main__':

    currentExitCode = Controller.EXIT_CODE_REBOOT
    while currentExitCode == Controller.EXIT_CODE_REBOOT:
        app=QApplication(sys.argv)
        # app.processEvents()
        controller = Controller()
        controller.show_login()
        currentExitCode = app.exec_()
        app = None
        # sys.exit(app.exec_())
    # return currentExitCode
