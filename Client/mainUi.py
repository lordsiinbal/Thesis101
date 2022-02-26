from asyncio.windows_events import NULL
from base64 import encode
from email import header
from encodings import utf_8
import encodings
from importlib import reload
from itertools import count
import json
import ctypes
import datetime as dtime
from itertools import count
from queue import PriorityQueue
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
from PyQt5.QtWidgets import  QApplication,QFileDialog,QTableWidgetItem,QHeaderView
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QMovie
from cv2 import QT_PUSH_BUTTON
from flask import Response, jsonify
from matplotlib import widgets
from PyQt5.QtCore import Qt,QDateTime,QDate,QTime,QTimer,QThread, pyqtSignal, pyqtSlot, QThreadPool, QProcess
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
class RoadSetUpPaint(QtWidgets.QMainWindow):
    switch_window = QtCore.pyqtSignal() 
    def __init__(self):
        super(RoadSetUpPaint, self).__init__()
        uic.loadUi(PATH+'/roadSetUp_paint.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.btnCancel.clicked.connect(self.close)#Button Cancel
        self.btnDone.clicked.connect(self.loading)#mouse Event

        
    def loading(self):#funtion for loading 
        self.roadNameValue=self.roadTextBox.text()
        self.switch_window.emit()

        # print(self.roadNameValue)
        self.close()

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
    selectImage=QtCore.pyqtSignal()
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
        if len(response.json()) >= 1 : # uif response has something to append
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
        self.rThread.quit()
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
        
        # r = requests.delete(url = baseURL + "/RoadDelete",json=data,headers=headers )
        # print(r)
        # print (r.json())
    
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
        # self.setParent(None)# remove contents
        # e = "{}"
        # j = json.loads(e)
        # self.getAllRoad(j, f=True) # remove first contents 
        # self.update()
        # self.repaint()
        response = response.json()
        self.getAllRoad(response) # add new roads
        self.update()
        # self.repaint()
        
        self.loadData.closeWindow()
        # super(RoadSetUp1, self).__init__()
        


#violation Record table
class TableUi(QtWidgets.QMainWindow):
    switch_window = QtCore.pyqtSignal()


    def __init__(self):
        super(TableUi, self).__init__()
        uic.loadUi(PATH+'/tableUi.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        _translate = QtCore.QCoreApplication.translate
        
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
        self.tableWidget.setRowCount(4) 
        self.tableWidget.setItem(0,0, QTableWidgetItem("Name"))
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
            # for j in range(5):
            #     self.tableWidget.setItem(i,j, QTableWidgetItem(data[i][j]))
            #     self.tableWidget.item(i,j).setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
            #Adding BUtton in each row  
            self.newBtnPlay=QtWidgets.QPushButton(self.tableWidget)
            self.newBtnDelete=QtWidgets.QPushButton(self.tableWidget)
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
            self.newBtnPlay.setIconSize(QtCore.QSize(19, 19))
            self.newBtnDelete.setIconSize(QtCore.QSize(14,15))
            self.tableWidget.setCellWidget(i,6,self.newBtnPlay)
            self.tableWidget.setCellWidget(i,7,self.newBtnDelete)
            self.newBtnDelete.clicked.connect(lambda ch, i=i: self.dropViolation(self.data[i]['violationID']))
            self.newBtnPlay.clicked.connect(lambda ch, i=i: self.buttonSome(i))
        self.btnDone.clicked.connect(self.close)
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
        # e = "{}"
        # j = json.loads(e)
        # self.finishedGetVio(j, f =True) # remove first contents
        # self.update()
        # self.repaint()
        # response = response.json()
        self.finishedGetVio(response) # add new roads
        self.update()
        # self.repaint()
        self.loadData.closeWindow()
        # self.finishedGetVio(response)
        

    def buttonSome(self,i):
        print(i)
#main Window
class MainUi(QtWidgets.QMainWindow):
    switch_window = QtCore.pyqtSignal()
    roadSwitch=QtCore.pyqtSignal()
    logout=QtCore.pyqtSignal()
    def __init__(self, window):
        super(MainUi, self).__init__()
        uic.loadUi(PATH+'/frontEndUi.ui', self)
        self.showMaximized()
        self.setWindowFlag(Qt.FramelessWindowHint) 
        self.btnRecord.clicked.connect(self.switch_window.emit)
        self.btnRoadSetup.clicked.connect(self.roadSwitch.emit)
        self.btnLogout.clicked.connect(self.logout.emit)
        self.btnAddVideo.clicked.connect(self.setUpVideo)
        self.btnPlayback.clicked.connect(self.activePlayback)
        self.btnWatch.clicked.connect(self.activeWatch)
        self.vidFile = None
        self.w = window
        #self.date=QDateTime.currentDateTime()
        #self.dateDay.setDate(self.date.date()
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
        try:
            self.w.initDet.det.dets.view_img = False
            # self.w.initDet.det.dets.stop()
            self.saveVid()
            self.vQueue = self.w.initDet.det.dets.vidFrames.copy()
            # play playback video here
            # creat a thread object for playing video
            isViolation = False
            # if from violation record 
            if isViolation:
                pass
                # playback from violation record
            else:
                # playback from currently playing video
                self.pause = True
                self.nthread = QThread()
                self.getVid = videoGet(self)
                self.getVid.moveToThread(self.nthread)
                self.nthread.started.connect(self.getVid.run)
                self.getVid.finished.connect(self.nthread.quit)
                self.nthread.finished.connect(self.finishedPlayBack) # execute when the task in thread is finised
                self.getVid.imgUpdate.connect(self.update_image)
                self.nthread.start()
        except Exception as er:
            print(er)
            pass
        
        
        self.image.setMinimumSize(QtCore.QSize(0, 400))
        self.image.setMaximumSize(QtCore.QSize(1280, 720))
        self.stackedWidget.setCurrentWidget(self.playbackPage)
        self.btnWatch.setStyleSheet('background-color:none;border:none')
        self.btnPlayback.setStyleSheet("color:white;font-size:14px;background-color:#1D1F32;border-left:3px solid #678ADD;")
        self.btnPlay.clicked.connect(self.pauseOrPlay)
        
    def pauseOrPlay(self):
        try:
            self.pause = False
            print('Pause = ',  self.pause)
            self.getVid.playOrPause(self.pause)
        except AttributeError:
            ctypes.windll.user32.MessageBoxW(0, "Please insert a video first", "Nothing to play", 1)
            

    
    
    def update_image(self, qim):
        self.w.window.image.setPixmap(qim)
        
    def finishedPlayBack(self):
        print('finished playing video')
        
    def activeWatch(self):
        try:
            self.getVid.stop()
            self.nthread.quit()
            self.pause = True
            self.w.initDet.det.dets.view_img = True
        except Exception as er:
            print(er)
            pass
        self.stackedWidget.setCurrentWidget(self.watchingPage)
        self.btnPlayback.setStyleSheet('background-color:none;border:none')
        self.btnWatch.setStyleSheet("color:white;font-size:14px;background-color:#1D1F32;border-left:3px solid #678ADD;")
        
    #Function display Video    
    def setUpVideo(self): #Initialize click event
        self.vidFile=QFileDialog.getOpenFileUrl()[0].toString()
        self.vidFile = self.vidFile[8:]
        self.roadSwitch.emit()
        
    def saveVid(self):
        
        # save playback here
        # self.playbackInfo['playbackID'].append(read('playback')+1)
        self.playbackInfo['playbackID'].append(1)
        self.playbackInfo['playbackVideo'].append(self.w.initDet.det.dets.vid_path) # si path ini kang video playback nasa detection_module/runs/
        duration = self.w.initDet.det.dets.frm_id / self.w.initDet.det.dets.vid_fps
        duration = str(dtime.timedelta(seconds=float(int(duration))))
        self.playbackInfo['duration'].append(duration)
        self.playbackInfo['roadName'].append(self.w.road.label.text())
        self.playbackInfo['dateAndTime'].append(str(dtime.datetime.fromtimestamp(float(int(time.time()))).strftime("%m/%d, %I:%M:%S %p")))
        # save('playBack', self.playbackInfo) # saved to records/playBackDb.csv
        self.savePlayback(self.playbackInfo)
        self.playbackKeys = ['playbackID', 'playbackVideo','duration', 'roadName', 'dateAndTime']
        self.playbackInfo = {k: [] for k in self.playbackKeys}

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
        app.exit(Controller.EXIT_CODE_REBOOT)
        
    def show_login(self):
        self.login =welcome()
        self.login.switch_window.connect(self.show_main)
        self.login.show()
        
    def show_main(self):
        self.window = MainUi(self)
        self.window.switch_window.connect(self.showTable)
        self.window.roadSwitch.connect(self.showRoadSetup)
        self.window.logout.connect(self.show_logout)
        self.window.show()
        self.login.close()
       
    def showTable(self):
        self.newWin=TableUi()
        # self.newWin.show()
    def showRoadSetup(self):
        # before showing road, execute background modelling and automatic road detection, must be loading
        self.road = RoadSetUp1(self)
        self.road.switch_window.connect(self.show_RoadPaint) # for btn new
        # disable new if vidfile has value
        # # self.road.selectImage.connect(self.select)
        self.road.settingUpRoad.connect(self.showFinishingUi) # for btn confirm new
    def show_RoadPaint(self):
        if self.window.vidFile is not None:
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
            ctypes.windll.user32.MessageBoxW(0, "Please insert a video first", "Empty Video file", 1)
    
    # function to call when the process of bg modelling and road extraction is done using thread
    def finishedInBGModelAndRoad(self):
        
        self.roadImage, self.ROI =  self.bgAndRoad.bgImage,  self.bgAndRoad.ROI
        if self.roadImage is not NULL:
            self.roadLoad.closeWindow()
            self.roadPaint=RoadSetUpPaint()
            self.roadPaint.switch_window.connect(self.showFinishingUi) # for btn done
            self.roadPaint.show()
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
            time.sleep(0.2)
        except:
            pass
        self.restart()
        # self.window.vidFile = None
        # self.window.close()
        # self.logout_Ui.close()
        # self.login.show()
    # def showSettingUproad(self):
    #     self.windowRoadSettingUp=roadSettingUp()
    #     self.windowRoadSettingUp.screenLabel.connect(self.showScreenImage)
    def showFinishingUi(self):
        if self.window.vidFile is not None: # hcheck if there's a current vid file
            # initialize detection
            try:
                # fot btn confirm
                if self.road.flagRoad:
                    self.ROI = self.road.selectedROI
                    try:
                        # if detection is currently running
                        self.initDet.det.dets.changeROI(self.road.selectedROI)
                        self.window.label.setText(self.road.selectedRoadName)
                        
                        print('ROI has been changed in running confirm')
                    except:
                        self.initializeDetection()
                        pass
                    self.road.flagRoad = False
                    self.roadImage = cv.imread(self.road.selectedRoadImage)
                    # print('selected road image shape', self.roadImage.shape)
                    self.roadIDGlobal = self.road.selectedRoadID
            except AttributeError:
                # for btn new
                try:
                    # if detection is currently running
                    self.initDet.det.dets.changeROI(self.ROI)
                    self.window.label.setText(self.roadPaint.roadNameValue)
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
                # roadCapturedJPG = str(PATH)+"\\\images\\\\"+roadID+".jpg"
                #making the data a json type

                
                data = {
                    'roadID' : roadID,
                    'roadName' : self.roadPaint.roadNameValue,
                    'roadCaptured' :  self.roadImage.tolist(),
                    'roadBoundaryCoordinates' : pd.Series(self.ROI).to_json(orient='values')
                    # 
                }
               
                # print(data['roadCaptured'])
                self.roadIDGlobal = roadID
                self.roadPaint.close()
                self.saveRoad(data)
        else:
            ctypes.windll.user32.MessageBoxW(0, "Please insert a video first", "Empty Video file", 1)
        
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
        self.loadData.closeWindow()
        try:
            if not self.initDet.det.dets.stopped: # if detection is not stopped
                #if detection is running, do nothing, don't reinitialize the detection
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
                self.window.label.setText(self.roadPaint.roadNameValue)
            self.window.verticalLayout_11.addWidget(self.window.frameWatch)#removing center aligment of frameWatch
            self.window.btnAddVideo.hide()
            self.window.labelScreen.setMinimumSize(QtCore.QSize(0, 400))

            # run detection here on separate thread
            self.thread = QThread()
            self.runDets = Worker(self)
            self.runDets.moveToThread(self.thread)
            self.thread.started.connect(self.runDets.runDet)
            self.runDets.finished.connect(self.thread.quit)
            self.thread.finished.connect(self.finishedrunDet) # execute when the task in thread is finised
            self.runDets.imgUpdate.connect(self.update_image)
            self.thread.start()
            
        else:
            print("ERROR: An error occured while performing detection")
            exit()
            
    def update_image(self, qim):
        self.window.labelScreen.setPixmap(qim)
           
    # this function will execute when the detection is finished with the video
    def finishedrunDet(self):        
        print("finished detection for this file")
    
    
    # #this function will display image    
    # def showScreenImage(self):
    #     data = self.road.selected
    #     # print(data)

    #     self.window.labelScreen.setPixmap(QtGui.QPixmap("images/image 1.jpg")) #setting image inside QLabel
    #     self.window.labelScreen.setMinimumSize(QtCore.QSize(0, 400))#setting minimum heigth
    #     self.window.label.setText(data['roadName'])
    #     self.window.verticalLayout_11.addWidget(self.window.frameWatch)#removing center aligment of frameWatch
    #     self.window.btnAddVideo.hide()#hiding button Insert Video
        #Closing Road Setting 
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
    
    def __init__(self, window):
        super(videoGet, self).__init__()
        self.w = window
        self.pause = self.w.pause
        # vid = window.initDet.det.dets.vid_path
        # # print(vid)
        # self.stream = cv2.VideoCapture(vid)
        # (self.grabbed, self.frame) = self.stream.read()
        # self.fps = int(self.stream.get(cv2.CAP_PROP_FPS))
        self.stopped = False
     
        
    def run(self):
        for frame in self.w.vQueue:
            now = time.time()
            if not self.stopped:
                QtImg = cvImgtoQtImg(frame)# Convert frame data to PyQt image format
                qim = QtGui.QPixmap.fromImage(QtImg)
                timediff = time.time() - now
                if (timediff<(1.0/(self.w.w.initDet.det.dets.sfps))):
                    time.sleep((1.0/(self.w.w.initDet.det.dets.sfps)) - timediff)

                self.imgUpdate.emit(qim)
                
            while self.pause:
                # loop here until pause is lifted
                pass
            
        self.stop()
        
    def stop(self):
        print('stopped')
        self.stopped = True  
        self.finished.emit()   
    
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
    
    #overloading constructor
    def __init__(self, action, type, d = None, h = None, ids_to_be_fetched = None):
        super(ProcessData, self).__init__()
        if d and h:
            self.data = d
            self.headers = h
        if ids_to_be_fetched and h:
            self.ids_to_be_fetched = ids_to_be_fetched
            self.headers = h
        self.action = action
        self.type = type
      
        
    def ret(self):
        if self.type == 1: # retrieve
            response = requests.get(url = baseURL + self.action)
            self.finished.emit(response)
        if self.type == 2: # post
            response = requests.post(url = baseURL + self.action, data=self.data,headers=self.headers)
            self.finished.emit(response)
        if self.type == 3: # delete
            response = requests.delete(url = baseURL + self.action, json=self.data,headers=self.headers )
            self.finished.emit(response)
        if self.type == 4: # retrieve with params
            response = requests.get(url = baseURL + self.action, data = self.ids_to_be_fetched , headers=self.headers)
            self.finished.emit(response)
            
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
