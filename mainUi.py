from asyncio.windows_events import NULL
from itertools import count
from select import select
from threading import local
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog
import sys
from msilib.schema import File
import sys
import cv2
import time
from PyQt5.QtWidgets import  QApplication,QFileDialog,QTableWidgetItem,QHeaderView,QLabel,QWidget
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QMovie,QPixmap, QPainter, QPen,QColor,QBrush,QTransform,QCursor,QIntValidator
from cv2 import QT_PUSH_BUTTON
from matplotlib import image, widgets
from PyQt5.QtCore import Qt,QDateTime,QDate,QTime,QTimer,QPoint,Qt,QRect
from sympy import false
from PIL import ImageQt
import numpy as np
def cvImgtoQtImg(cvImg):  #Define the function of opencv image to PyQt image
    QtImgBuf = cv2.cvtColor(cvImg, cv2.COLOR_BGR2BGRA)
    QtImg = QtGui.QImage(QtImgBuf.data, QtImgBuf.shape[1], QtImgBuf.shape[0], QtGui.QImage.Format_RGB32)
    return QtImg 

class FinishingUi(QtWidgets.QWidget):#Finishing Loading UI
    screenLabel=QtCore.pyqtSignal()
    def __init__(self):
        super(FinishingUi, self).__init__()
        uic.loadUi('finishingUi.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.animation=QMovie('icon/loadingAnimated.gif')#animation Logo
        self.loading.setMovie(self.animation)
        self.animation.start()#animation Statrt
        self.show()
        QtCore.QTimer.singleShot(5000, self.closeWindow)#run the window for 5 seconds
    def closeWindow(self):
        self.screenLabel.emit()#calling screenlabel 
        self.close()#closing Widget


class roadSettingUp(QtWidgets.QWidget):#road Setting Up Loading
    screenLabel=QtCore.pyqtSignal()
    def __init__(self):
        super(roadSettingUp, self).__init__()
        uic.loadUi('settingUpRoad.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)#hide title bar
        self.animation=QMovie('icon/loadingAnimated.gif')#Animation Loading
        self.loading.setMovie(self.animation)
        self.animation.start()#start Animation
        self.show()
        QtCore.QTimer.singleShot(5000, self.closeWindow)#run the window for 5 seconds
    def closeWindow(self):
        self.screenLabel.emit()
        self.close()#cloase Window


class myQLabel(QWidget):
    def __init__(self,parent):
        super(myQLabel, self).__init__(parent)
        #self.verticalLayout = QtWidgets.QVBoxLayout(self)
        #self.image = QLabel(self)
        self.newWindowSize=self.resize(1080,720)
        self.image = QtGui.QImage("image 1.jpg")
        
        self.draw=QLabel(self)
        #self.image.setGeometry(QtCore.QRect(0, 0,parent.width(),parent.height()))
        self.draw.setGeometry(QtCore.QRect(0, 0,1080,720))
        #self.draw.setGeometry(0,0,parent.width(),parent.height())
        #self.labelDraw=QLabel()
        #self.labelDraw.setPixmap(QPixmap(self.width,self.height)) # width, height
        #self.labelDraw
        #self.labelDraw.fill(Qt.white)

        pixmap = QPixmap(parent.width(),parent.height()) # width, height
        newPixmap=pixmap.scaled(1080,720)
        newPixmap.fill(Qt.transparent)
        self.draw.setPixmap(newPixmap)
        #self.verticalLayout.addWidget(self.label)
        canvas =QPixmap("image 1.jpg")
        #canvas.scaled(1080,720)
        """self.image.setScaledContents(True)"""
        #self.image.setPixmap(canvas)
        self.drawAction=True
        self.last_x, self.last_y = None, None
        self.eraser_selected=False
        self._size=20
        "For Auto Segmentaion"
        roi=[[[[312,0]],[[311,1]],[[311,2]],[[310,3]],[[309,3]],[[308,4]],[[307,5]],[[306,6]],[[305,6]],[[304,7]]]]
        pm=QtGui.QPixmap(self.draw.pixmap()) 
        painter=QtGui.QPainter(pm)
        painter.setPen(QPen(QColor(0,255,0),100 ,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
        transform=QTransform().scale(pm.width()/self.draw.width(),
                                    pm.height()/self.draw.height())    
        #loop through roi location
        for i in range(1):
            for j in range(len(roi[0])):
                location=roi[i][j]
                painter.drawPoint(location[0][0],location[0][1])
                    
        painter.end()
        self.draw.setPixmap(pm)
        """End of Auto Segmentation"""
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
        self.last_x=None
        self.last_y=None
class RoadSetUpPaint(QtWidgets.QMainWindow):
    switch_window = QtCore.pyqtSignal() 
    def __init__(self):
        super().__init__()
        self.show()
        uic.loadUi('roadSetUp_paint.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.btnCancel.clicked.connect(self.close)#Button Cancel
        self.btnDone.clicked.connect(self.loading)#mouse Event
        self.verticalLayout = QtWidgets.QVBoxLayout(self.imageMainContainer)
        self.image_main=myQLabel(self.imageMainContainer)
        self.verticalLayout.addWidget(self.image_main)
        self.btnBrush.clicked.connect(self.enableDraw)
    def enableDraw(self):
        self.image_main.drawAction=True

    def loading(self):#funtion for loading 
        self.switch_window.emit()
        self.close()
        self.paintedImage= self.image_main.findChild(QLabel,"image")
        image = ImageQt.fromqpixmap(self.paintedImage.pixmap())
        image.save('test.jpg')
    
        
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
        uic.loadUi('logoutUi.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)#removing title bar
        self.btnLogout.clicked.connect(self.confirmLogout.emit)
        self.btnCancel.clicked.connect(self.close)
   
        

class RoadSetUp1(QtWidgets.QMainWindow):#Road Setting Up Ui
    switch_window = QtCore.pyqtSignal()
    selectImage=QtCore.pyqtSignal()
    settingUpRoad=QtCore.pyqtSignal()
    def __init__(self):
        super(RoadSetUp1, self).__init__()
        uic.loadUi('roadSetUp_phase1.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)      #removing Title bar
        #self.label.mousePressEvent = self.selectImage   #mouse Event for Qlabel
        #self.btnNew.clicked.connect(self.switch_window.emit)    #Showing Draw road Ui
        self.btnCancel.clicked.connect(self.close)          #close window
        self.btnConfirm.clicked.connect(self.settingUpRoad.emit)       #Loading Ui
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
                self.labelImage.setText("") #emptying text 
                self.labelImage.setPixmap(QtGui.QPixmap(str(data[x][1])))   #get show Image inside labelImage
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
    """def loading(self):
        self.settingUpRoad.emit()
        self.close()"""
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
        uic.loadUi('tableUi.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        _translate = QtCore.QCoreApplication.translate
        data=[['01','Violated','San Felipe','0:00:10','01/26/202290/000','01/26/202290/000'],
              ['02','Violated','SM Area','7 minutes','01/26/202290/000','01/26/202290/000'],
              ]
        #self.tableWidget.setRowCount(4) 
        #self.tableWidget.setItem(0,0, QTableWidgetItem("Name"))
        self.tableWidget.setRowCount(len(data))
        for i in range(len(data)):
            for j in range(6):
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
            icon1.addPixmap(QtGui.QPixmap("icon/playCircleArrow.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            icon2.addPixmap(QtGui.QPixmap("icon/deleteIcon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.newBtnPlay.setIcon(icon1)
            self.newBtnDelete.setIcon(icon2)
            self.newBtnPlay.setIconSize(QtCore.QSize(19, 19))
            self.newBtnDelete.setIconSize(QtCore.QSize(14,15))
            self.tableWidget.setCellWidget(i,j+1,self.newBtnPlay)
            self.tableWidget.setCellWidget(i,j+2,self.newBtnDelete)
            self.newBtnPlay.clicked.connect(lambda ch, i=i: self.buttonSome(i))
        self.btnDone.clicked.connect(self.close)
    
    def buttonSome(self,i):
        """print(i)"""
#main Window
class MainUi(QtWidgets.QMainWindow):
    switch_window = QtCore.pyqtSignal()
    roadSwitch=QtCore.pyqtSignal()
    logout=QtCore.pyqtSignal()
    addIp=QtCore.pyqtSignal()
    addCctv=QtCore.pyqtSignal()
    def __init__(self):
        super(MainUi, self).__init__()
        uic.loadUi('frontEndUi.ui', self)
        self.showMaximized()
        self.setWindowFlag(Qt.FramelessWindowHint) 
        self.btnRecord.clicked.connect(self.switch_window.emit)
        self.btnRoadSetup.clicked.connect(self.activeRoadSetUp)
        self.btnLogout.clicked.connect(self.logout.emit)
        self.btnAddVideo.clicked.connect(self.setUpVideo)
        self.btnIpAdd.clicked.connect(self.addIp.emit)
        self.btnCctv.clicked.connect(self.addCctv.emit)
        self.btnPlayback.clicked.connect(self.activePlayback)
        self.btnWatch.clicked.connect(self.activeWatch)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.roadSetUpImage)
        self.image_main=myQLabel(self.roadSetUpImage)
        self.verticalLayout.addWidget(self.image_main)
        self.eraserTool.clicked.connect(self.eraseSelected)
        self.drawTool.clicked.connect(self.drawSelected)
        self.addSize.clicked.connect(self.addSizeFunction)
        self.subSize.clicked.connect(self.subSizeFunction)
        validatorInt=QIntValidator()
        self.sizeLabel.setValidator(validatorInt)
        self.sizeLabel.returnPressed.connect(self.enterSize)
        timer = QTimer(self)
		# adding action to timer
        timer.timeout.connect(self.showTime)

		# update the timer every second
        timer.start(1000)
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
        self.stackedWidget.setCurrentWidget(self.playbackPage)
        self.btnWatch.setStyleSheet('background-color:none;border:none')
        self.btnRoadSetup.setStyleSheet('background-color:none;border:none')
        self.btnPlayback.setStyleSheet("color:white;font-size:14px;background-color:#1D1F32;border-left:3px solid #678ADD;")
    def activeWatch(self):
        self.stackedWidget.setCurrentWidget(self.watchingPage)
        self.btnPlayback.setStyleSheet('background-color:none;border:none')
        self.btnRoadSetup.setStyleSheet('background-color:none;border:none')
        self.btnWatch.setStyleSheet("color:white;font-size:14px;background-color:#1D1F32;border-left:3px solid #678ADD;")
    def activeRoadSetUp(self):
        self.stackedWidget.setCurrentWidget(self.roadSetupPage)
        self.btnPlayback.setStyleSheet('background-color:none;border:none')
        self.btnWatch.setStyleSheet('background-color:none;border:none')
        self.btnRoadSetup.setStyleSheet("color:white;font-size:14px;background-color:#1D1F32;border-left:3px solid #678ADD;")
        
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
         self.image_main.eraser_selected=False
         self.image_main.setCursor(QtGui.QCursor((QtCore.Qt.ArrowCursor)))

    def eraseSelected(self):
        self.image_main.eraser_selected=True
        self.cursorForEraser()
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
    def setUpVideo(self): #Initialize click event
        self.roadSwitch.emit()
    
       

class welcome(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal()
    def __init__(self):
        super(welcome, self).__init__()
        uic.loadUi('welcomeUi.ui', self)
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
        self.window = MainUi()
        self.window.switch_window.connect(self.showTable)
        self.window.roadSwitch.connect(self.showRoadSetup)
        self.window.addIp.connect(self.showUseIpAdd)
        self.window.logout.connect(self.show_logout)
        self.window.addCctv.connect(self.showUseCctv)
        self.window.show()
        self.login.close()

    def showUseCctv(self):
        self.cctvWidget=CctvWindow()
        self.cctvWidget.show()
        self.cctvWidget.btnDone.clicked.connect(self.setCctvSelected)
    def setCctvSelected(self):
        self.window.Selected.setText("CCTV is Active:")
        self.cctvWidget.close()

    def showUseIpAdd(self):
        self.IpAddWindow=IpAddWindow()
        self.IpAddWindow.btnDone.clicked.connect(self.setIpSetected)         
        self.IpAddWindow.show()
    def setIpSetected(self):
        ipAdd=self.IpAddWindow.textBox.text()
        if ipAdd==None:
            self.window.File.setText("")    
            return
        else:
            self.window.Selected.setText("IP Address Selected:")    
            self.window.File.setText(ipAdd)
            self.IpAddWindow.close()
          

    def showTable(self):
        self.newWin=TableUi()
        self.newWin.show()
    def showRoadSetup(self):
        self.road=RoadSetUp1()
        #self.road.switch_window.connect(self.show_RoadPaint)
        self.road.btnNew.clicked.connect(self.show_RoadPaint)
        #self.road.selectImage.connect(self.select)
        self.road.settingUpRoad.connect(self.showSettingUproad)
        self.road.show()

    def show_RoadPaint(self):
        self.road.close()
        self.window.activeRoadSetUp()
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
        self.windowFinishing=FinishingUi()
        self.windowFinishing.screenLabel.connect(self.showScreenImage)
        #self.windowRoadSettingUp.show()
    #this function whill display image    
    def showScreenImage(self):
        self.window.labelScreen.setPixmap(QtGui.QPixmap("images/image 1.jpg")) #setting image inside QLabel
        self.window.labelScreen.setMinimumSize(QtCore.QSize(0, 400))#setting minimum heigth
        self.window.label.setText("San Felipe")
        self.window.verticalLayout_11.addWidget(self.window.frameWatch)#removing center aligment of frameWatch
        self.window.frameButtons_2.hide()
        #Closing Road Setting 
    def select(self):
        print("Select Image")       
if __name__ == '__main__':
    app=QApplication(sys.argv)
    controller = Controller()
    controller.show_login()
    sys.exit(app.exec_())

