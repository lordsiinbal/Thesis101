from asyncio.windows_events import NULL
import ctypes
from itertools import count
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
from matplotlib import widgets
from PyQt5.QtCore import Qt,QDateTime,QDate,QTime,QTimer,QThread, pyqtSignal, pyqtSlot
from sympy import false
import numpy as np
from PIL.ImageQt import ImageQt
from PIL.Image import Image as ImagePil
from PIL import Image as Img

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
        if w.window.vidFile is None or not w.window.vidFile:
            self.btnNew.setEnabled(False)
        else:
            self.btnNew.setEnabled(True)
            
        data=[
            [0,"images/image 1.jpg","FileName1"],[1,"images/image 1.jpg","FileName2"],
            [2,"images/image 1.jpg","FileName3"],[3,"images/image 1.jpg","FileName4"],
            [4,"images/image 1.jpg","FileName5"],[5,"images/image 1.jpg","FileName6"]
            ]   
        x=0     #initialize x for items in each row
        row=0   #initialize row
        self.prevSelectedImage=NULL
        while x< len(data):
            for y in range(2):                
                self.frame= QtWidgets.QFrame(self.mainArea)    #create a Qframe for container
                self.frame.setObjectName("id"+str(data[x][0]))       #set Qframe objectName or class
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
                self.labelImage.setText("")
                self.labelImage.setPixmap(QtGui.QPixmap(PATH+"/images/image 1.jpg"))
                
                # self.labelImage.setText("") #emptying text 
                # self.labelImage.setPixmap(QtGui.QPixmap(str(data[x][1])))   #get show Image inside labelImage
                self.labelImage.setScaledContents(True)
                self.labelImage.setObjectName("label")  #set 
                self.verticalLayout.addWidget(self.labelImage)
                self.label = QtWidgets.QLabel(self.frame)
                self.label.setText(str(data[x][2]))#Assign file label
                self.labelImage.mousePressEvent =lambda event, x=x: self.selectImage(event,str(data[x][0]))  #mouse Event 
                self.verticalLayout.addWidget(self.label, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
                self.gridLayout.addWidget(self.frame,row,y,1,1) #added the frame inside grid layout
                x=x+1       #iterate x
            row=row+1       #iterate row
    def loading(self):
        self.settingUpRoad.emit()
        self.close()
    def selectImage(self,event,x):
        if self.prevSelectedImage != NULL:         #border of previous selected image is set to none  
            self.newFrame=self.mainArea.findChild(QtWidgets.QFrame,self.prevSelectedImage)
            self.newFrame.setStyleSheet("#label{border:none}")

        self.newFrame=self.mainArea.findChild(QtWidgets.QFrame,"id"+x)#find child in mainArea with object name "id"+x 
        self.newFrame.setStyleSheet("#label{border:2px solid white}")  #add border to image
        self.btnConfirm.setEnabled(True)                    #btnConfirm enable
        self.btnConfirm.setStyleSheet("color:white;border:2px solid white") #add css on btnConfirm
        self.mainArea.setStyleSheet("QFrame 2{\n"
            "border:5px solid white;}\n")
        self.prevSelectedImage="id"+x

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
        data=[['01','Violated','San Felipe','5 minutes','01/26/22'],
              ['02','Violated','SM Area','7 minutes','01/29/22'],
              ['03','Violated','Terminal 2','10 minutes','01/27/22'],
              ['04','Violated','Terminal 1','6 minutes','02/06/22'],
              ['01','Violated','San Felipe','5 minutes','01/26/22'],
              ['02','Violated','SM Area','7 minutes','01/29/22'],
              ['03','Violated','Terminal 2','10 minutes','01/27/22'],
              ['04','Violated','Terminal 1','6 minutes','02/06/22'],
              ['01','Violated','San Felipe','5 minutes','01/26/22'],
              ['02','Violated','SM Area','7 minutes','01/29/22'],
              ['03','Violated','Terminal 2','10 minutes','01/27/22'],
              ['04','Violated','Terminal 1','6 minutes','02/06/22'],
              ['01','Violated','San Felipe','5 minutes','01/26/22'],
              ['02','Violated','SM Area','7 minutes','01/29/22'],
              ['03','Violated','Terminal 2','10 minutes','01/27/22'],
              ['04','Violated','Terminal 1','6 minutes','02/06/22'],
              ['01','Violated','San Felipe','5 minutes','01/26/22'],
              ['02','Violated','SM Area','7 minutes','01/29/22'],
              ['03','Violated','Terminal 2','10 minutes','01/27/22'],
              ['04','Violated','Terminal 1','6 minutes','02/06/22']
              ]
        
        #self.tableWidget.setRowCount(4) 
        #self.tableWidget.setItem(0,0, QTableWidgetItem("Name"))
        self.tableWidget.setRowCount(len(data))
        for i in range(len(data)):
            for j in range(5):
                self.tableWidget.setItem(i,j, QTableWidgetItem(data[i][j]))
                self.tableWidget.item(i,j).setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
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
            self.tableWidget.setCellWidget(i,j+1,self.newBtnPlay)
            self.tableWidget.setCellWidget(i,j+2,self.newBtnDelete)
            self.newBtnPlay.clicked.connect(lambda ch, i=i: self.buttonSome(i))
        self.btnDone.clicked.connect(self.close)
    
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
        self.roadKeys = ['roadId', 'roadName','roadCaptured', 'roadBoundaryCoordinates']
        self.roadInfos = {k: [] for k in self.roadKeys}
        self.violationKeys = ['violationID', 'vehicleID','roadName', 'lengthOfViolation','startDateAndTime', 'endDateAndTime']
        self.violationInfos = {k: [] for k in self.violationKeys}
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
        self.w.initDet.det.dets.stop() # for now, stop detection, but main purpose of this is to continue detection and view the recorded
        self.stackedWidget.setCurrentWidget(self.playbackPage)
        self.btnWatch.setStyleSheet('background-color:none;border:none')
        self.btnPlayback.setStyleSheet("color:white;font-size:14px;background-color:#1D1F32;border-left:3px solid #678ADD;")
    def activeWatch(self):
        self.stackedWidget.setCurrentWidget(self.watchingPage)
        self.btnPlayback.setStyleSheet('background-color:none;border:none')
        self.btnWatch.setStyleSheet("color:white;font-size:14px;background-color:#1D1F32;border-left:3px solid #678ADD;")
    #Function display Video    
    def setUpVideo(self): #Initialize click event
        
        # run(vid = '../data/drive-download-20220119T020939Z-002/CCTV San Francisco/XVR_ch5_main_20220114100004_20220114110004.mp4')
        self.vidFile=QFileDialog.getOpenFileUrl()[0].toString()
        self.vidFile = self.vidFile[8:]

        self.roadSwitch.emit()
      
class welcome(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal()
    def __init__(self):
        super(welcome, self).__init__()
        uic.loadUi(PATH+'/welcomeUi.ui', self)
        self.btnLogin.clicked.connect(self.goToLogin)
        self.btnCancel.clicked.connect(self.close)
        self.setWindowFlag(Qt.FramelessWindowHint)      
    def goToLogin(self):
        self.switch_window.emit()

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
        self.window.close()
        self.logout_Ui.close()
        self.login.show()
    def showSettingUproad(self):
        self.windowRoadSettingUp=roadSettingUp()
        self.windowRoadSettingUp.screenLabel.connect(self.showScreenImage)
    def showFinishingUi(self):
        self.roadPaint.close()
        type = 'road'
        # initialize detection
        self.windowFinishing=FinishingUi()# loading for finishing 
        
        # save road to db
        self.window.roadInfos['roadId'].append(read(type)+1)
        self.window.roadInfos['roadName'].append('something')
        self.window.roadInfos['roadCaptured'].append(str(list(self.roadImage)))
        self.window.roadInfos['roadBoundaryCoordinates'].append(str(list(self.ROI)))
        save(type, self.window.roadInfos)
        
        self.thread = QThread()
        self.initDet = Worker(self)
        self.initDet.moveToThread(self.thread)
        self.thread.started.connect(self.initDet.initDet)
        self.initDet.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.finishedInitDet) # execute when the task in thread is finised
        # self.thread.start()
        print("started init det")
        
    # this function will be executed when finished initializing detection and tracking models
    def finishedInitDet(self):
        if self.initDet.det.dets.flag:
            self.windowFinishing.closeWindow() # close loading
            print("finished initializing detection models")
            
            # run detection here
            self.window.label.setText("San Felipe") # name of video
            self.window.verticalLayout_11.addWidget(self.window.frameWatch)#removing center aligment of frameWatch
            self.window.btnAddVideo.hide()
            self.window.labelScreen.setMinimumSize(QtCore.QSize(0, 400))
            
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
        cv2.imshow("aa",self.initDet.det.dets.frame)
        if cv2.waitKey(1) == ord('q'):
            self.initDet.det.dets.stop()
            
    def select(self):
        print("Select Image")

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
        self.det = detection(self.vid, self.w.ROI)
        self.finished.emit()

    def runDet(self):
        # run/start detection
        self.w.initDet.det.dets.t.start()
        # wait for 1 sec
        time.sleep(0.3)
        while not self.w.initDet.det.dets.stopped:
            #BUG: SLOW DETECTION, MAYBBE IN THREADS, I REALLY DONT KNOW
            img = np.copy(self.w.initDet.det.dets.frame) #make a copy of frame
            QtImg = cvImgtoQtImg(img)# Convert frame data to PyQt image format
            qim = QtGui.QPixmap.fromImage(QtImg)
            self.imgUpdate.emit(qim) # fix threading, slow detection bug
            # self.w.showScreenImage()
        self.finished.emit()


if __name__ == '__main__':
    app=QApplication(sys.argv)
    app.processEvents()
    controller = Controller()
    controller.show_login()
    sys.exit(app.exec_())
