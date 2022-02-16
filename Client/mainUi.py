from asyncio.windows_events import NULL
from email import header
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
from flask import jsonify
from matplotlib import widgets
from PyQt5.QtCore import Qt,QDateTime,QDate,QTime,QTimer,QThread, pyqtSignal, pyqtSlot, QThreadPool
import numpy
from sympy import false
from api import baseURL
import requests 
import pandas as pd
from sys import *

#NOTE: Si pag save kang road saka playback yaon igdi sa file, control F 'save road' saka 'save playback' ka nalang
# si pag save kang violation nasa track.py sa detection_module control-F 'save violation' ka nalang ulit


#adding the functinality features
#import classes
import sys
import os
sys.path.append("../")
from main import getBgModelAndRoad, detection # main function to run detection
from records.dbProcess import save, read

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
        QtCore.QTimer.singleShot(500000, self.closeWindow)#run the window for 5 mins
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
        QtCore.QTimer.singleShot(500000, self.closeWindow)#run the window for 5 mins
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
        self.switch_window.emit()
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
        res = requests.get(url = baseURL + "/RoadFetchAll")
        data = res.json()
        self.prevSelectedImage=NULL
        
        if ((len(data)%2)==0):
            row = self.roadCard(data,len(data))
        else:
            
            length=len(data)-1
            print(length)
            row = self.roadCard(data,length)
            self.frame= QtWidgets.QFrame(self.mainArea)    #create a Qframe for container
            self.frame.setObjectName(str(data[len(data)-1]['roadID']))       #set Qframe objectName or class
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
            self.labelImage.setPixmap(QtGui.QPixmap(str(data[len(data)-1]['roadCaptured'])))   #get show Image inside labelImage
            self.labelImage.setScaledContents(True)
            self.labelImage.setObjectName("label")  #set 
            self.verticalLayout.addWidget(self.labelImage)
            self.label = QtWidgets.QLabel(self.frame)
            self.label.setText(str(data[len(data)-1]['roadName']))#Assign file label
            self.labelImage.mousePressEvent =lambda event, data=data: self.selectImage(event,data[len(data)-1])  #mouse Event 
            self.verticalLayout.addWidget(self.label, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
            self.gridLayout.addWidget(self.frame,row+1,0,1,1) #added the frame inside grid layout   \
            
                
    
    def roadCard(self,data,length):
        print(length)
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
                    self.labelImage.setPixmap(QtGui.QPixmap(str(data[x]['roadCaptured'])))   #get show Image inside labelImage
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

    def dropRoad(self):
        a=str(self.selected['roadID'])
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {"roadID": a}

        r = requests.delete(url = baseURL + "/RoadDelete",json=data,headers=headers )
        print(r)
        reload(RoadSetUp1)
        # print (r.json())


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

        res = requests.get(url = baseURL + "/ViolationFetchAll")
        data = res.json()
        
        self.tableWidget.setRowCount(4) 
        self.tableWidget.setItem(0,0, QTableWidgetItem("Name"))
        self.tableWidget.setRowCount(len(data))
        for i in range(len(data)):
            self.tableWidget.setItem(i,0, QTableWidgetItem(data[i]['violationID']))
            self.tableWidget.item(i,0).setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
            self.tableWidget.setItem(i,1, QTableWidgetItem(data[i]['vehicleID']))
            self.tableWidget.item(i,1).setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
            self.tableWidget.setItem(i,2, QTableWidgetItem(data[i]['roadName']))
            self.tableWidget.item(i,2).setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
            self.tableWidget.setItem(i,3, QTableWidgetItem(data[i]['lengthOfViolation']))
            self.tableWidget.item(i,3).setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
            self.tableWidget.setItem(i,4, QTableWidgetItem(data[i]['lengthOfViolation']))
            self.tableWidget.item(i,4).setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
            self.tableWidget.setItem(i,5, QTableWidgetItem(data[i]['lengthOfViolation']))
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
            self.newBtnDelete.clicked.connect(lambda ch, i=i: self.dropViolation(data[i]['violationID']))
            self.newBtnPlay.clicked.connect(lambda ch, i=i: self.buttonSome(i))
        self.btnDone.clicked.connect(self.close)
    
    def dropViolation(self,violation_ID):
        a=str(violation_ID)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {"violationID": a}

        r = requests.delete(url = baseURL + "/ViolationDelete",json=data,headers=headers )
        print(r)
        reload(TableUi)

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
        # self.roadKeys = ['roadID', 'roadName','roadCaptured', 'roadBoundaryCoordinates']
        # self.roadInfos = {k: [] for k in self.roadKeys}
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
        # self.w.initDet.det.dets.stop() # for now, stop detection, but main purpose of this is to continue detection and save and view the recorded
        try:
            self.saveVid()
            self.w.initDet.det.dets.show_vid = False
        except:
            pass
        # cv2.destroyAllWindows()
        self.stackedWidget.setCurrentWidget(self.playbackPage)
        self.btnWatch.setStyleSheet('background-color:none;border:none')
        self.btnPlayback.setStyleSheet("color:white;font-size:14px;background-color:#1D1F32;border-left:3px solid #678ADD;")
        
    def activeWatch(self):
        try:
            self.w.initDet.det.dets.show_vid = True
        except:
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
        self.playbackInfo['playbackID'].append(read('playback')+1)
        self.playbackInfo['playbackVideo'].append(self.w.initDet.det.dets.vid_path) # si path ini kang video playback nasa detection_module/runs/
        duration = self.w.initDet.det.dets.frm_id / self.w.initDet.det.dets.vid_fps
        duration = str(dtime.timedelta(seconds=float(int(duration))))
        self.playbackInfo['duration'].append(duration)
        self.playbackInfo['roadName'].append('road name')
        self.playbackInfo['dateAndTime'].append(dtime.date.today())
        # save('playBack', self.playbackInfo) # saved to records/playBackDb.csv
        self.savePlayback(self.playbackInfo)

    def savePlayback(self,data):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}


        r = requests.post(url = baseURL + "/PlaybackInsert",data=json.dumps(data),headers=headers)
        print(r)
        
        
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
    def __init__(self):
        pass

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
        self.newWin.show()
    def showRoadSetup(self):
        # before showing road, execute background modelling and automatic road detection, must be loading
        self.road = RoadSetUp1(self)
        self.road.switch_window.connect(self.show_RoadPaint) # for btn new
        # disable new if vidfile has value
        # # self.road.selectImage.connect(self.select)
        self.road.settingUpRoad.connect(self.showSettingUproad) # for btn confirm new
        self.road.show()
    def show_RoadPaint(self):
        if self.window.vidFile is not None:
            self.road.close()
            self.road.disconnect()
            self.roadLoad = roadSettingUp() # for loading setting up road
            
            # run extraction of bg and road
            self.thread = QThread()
            self.bgAndRoad = Worker(self)
            self.bgAndRoad.moveToThread(self.thread)
            self.thread.started.connect(self.bgAndRoad.runBG)
            self.bgAndRoad.finished.connect(self.thread.quit)
            self.thread.finished.connect(self.finishedInBGModelAndRoad) # execute when the task in thread is finised
            self.thread.start()
            print("started")
        else:
            ctypes.windll.user32.MessageBoxW(0, "Please insert a video first", "Empty Video file", 1)
    
    # function to call when the process of bg modelling and road extraction is done using thread
    def finishedInBGModelAndRoad(self):
        self.roadImage, self.ROI =  self.bgAndRoad.bgImage,  self.bgAndRoad.ROI
        if self.roadImage is not NULL:
            self.roadLoad.closeWindow()
            self.roadPaint=RoadSetUpPaint()
            self.roadPaint.switch_window.connect(self.showFinishingUi) # for btn confirm
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
        except:
            pass
        self.window.close()
        self.logout_Ui.close()
        self.login.show()
    def showSettingUproad(self):
        self.windowRoadSettingUp=roadSettingUp()
        self.windowRoadSettingUp.screenLabel.connect(self.showScreenImage)
    def showFinishingUi(self):
        self.roadPaint.close()
        
        # initialize detection
        self.windowFinishing=FinishingUi()# loading for finishing 
        # save road to db here
        # BUG: the saved arrays are separated by ... means the'yre too large
        # roadImage and ROI are large arrays, dai ko aram if pag tg save sa db complete sya, sa csv kaya putol sya
        
        
        # self.window.roadInfos['roadID'].append(str(read(type)+1))
        # self.window.roadInfos['roadName'].append('something') # get the txt from textbox
        # self.window.roadInfos['roadCaptured'].append(str(self.roadImage)) 
        # self.window.roadInfos['roadBoundaryCoordinates'].append(str(self.ROI))
        # save(type, self.window.roadInfos) # saved to records/roadDb.csv

        type = 'road'
        roadID = str(read(type)+1)
        roadCapturedTxt = "image/"+roadID+".jpg"
        data = {
            'roadID' : str(read(type)+1),
            'roadName' : "San Felipe",
            'roadCaptured' : roadCapturedTxt,
            'roadBoundaryCoordinates' : str(pd.Series(self.ROI).to_json(orient='values'))
        }
    
        self.saveRoad(data)
        # self.saveViolation()
        

        
        self.thread = QThread()
        self.initDet = Worker(self)
        self.initDet.moveToThread(self.thread)
        self.thread.started.connect(self.initDet.initDet)
        self.initDet.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.finishedInitDet) # execute when the task in thread is finised
        self.thread.start()
        print("started init det")

  
    def saveRoad(self,data):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}


        r = requests.post(url = baseURL + "/RoadInsert",data=json.dumps(data),headers=headers)
        print(r)


    # this function will be executed when finished initializing detection and tracking models
    def finishedInitDet(self):
        if self.initDet.det.dets.nflag:
            self.windowFinishing.closeWindow() # close loading
            print("finished initializing detection models")
            
           
            self.window.label.setText("San Felipe") # name of video
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
    def showScreenImage(self):
        data = self.road.selected
        print(data)

        self.window.labelScreen.setPixmap(QtGui.QPixmap("images/image 1.jpg")) #setting image inside QLabel
        self.window.labelScreen.setMinimumSize(QtCore.QSize(0, 400))#setting minimum heigth
        self.window.label.setText(data['roadName'])
        self.window.verticalLayout_11.addWidget(self.window.frameWatch)#removing center aligment of frameWatch
        self.window.btnAddVideo.hide()#hiding button Insert Video
        #Closing Road Setting 
    def select(self):
        print("Select Image")


# classes for worker threads
class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    imgUpdate = QtCore.pyqtSignal(QtGui.QPixmap)
    
    def __init__(self, window):
        super(Worker, self).__init__()
        self.w = window
        self.vid = self.w.window.vidFile     

    def runBG(self):
        self.bgImage, self.ROI = getBgModelAndRoad(self.vid)
        self.finished.emit()
        
    def initDet(self):
        self.det = detection(self.vid, self.w.ROI, self.w.roadImage)
        self.finished.emit()

    def runDet(self):
        # run/start detection
        self.w.initDet.det.dets.run()
        f = 1
        # wait for detection to finish one frame
        while self.w.initDet.det.dets.f == 0:
            print('wait', end="\r")
            pass
        while not self.w.initDet.det.dets.stopped:
            if self.w.initDet.det.dets.show_vid:
                if f == self.w.initDet.det.dets.f:
                    img = numpy.copy(self.w.initDet.det.dets.frame) #make a copy of frame
                    QtImg = cvImgtoQtImg(img)# Convert frame data to PyQt image format
                    qim = QtGui.QPixmap.fromImage(QtImg)
                    self.imgUpdate.emit(qim)
                    f +=1
                else:
                    print(' ', end='\r')
            else:
                f = self.w.initDet.det.dets.f + 1
                print(' ', end='\r')
            
        self.finished.emit()

if __name__ == '__main__':
    app=QApplication(sys.argv)
    # app.processEvents()
    controller = Controller()
    controller.show_login()

    sys.exit(app.exec_())

