#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 17:39:44 2020

@author: juliengautier
"""
import qdarkstyle 
from pyqtgraph.Qt import QtCore,QtGui 
from PyQt5.QtWidgets import QApplication,QMessageBox,QVBoxLayout,QHBoxLayout,QMainWindow,QLabel,QDockWidget,QSlider,QInputDialog,QCheckBox
from PyQt5.QtWidgets import QMenu,QWidget,QTabWidget,QComboBox,QToolButton,QSpinBox
import sys,time,os

from PyQt5.QtCore import Qt

from PyQt5.QtGui import QIcon

from visu.WinCut import GRAPHCUT

import pathlib
import numpy as np

from oneMotorSimpleFrog import ONEMOTOR
from scanMotor import SCAN

from visualResult import SEERESULT
from seabreeze.spectrometers import Spectrometer, list_devices

version='2021.09'

class FROG(QMainWindow) :
    
    isrunning=QtCore.pyqtSignal(bool)
    
    def __init__(self,parent=None):
        super().__init__(parent)
        
        self.confFrog=QtCore.QSettings('confFrog.ini', QtCore.QSettings.IniFormat)
        p = pathlib.Path(__file__)
        sepa=os.sep
        self.icon=str(p.parent) + sepa+'icons'+sepa
        self.setWindowIcon(QIcon(self.icon+'LOA.png'))
        self.left=30
        self.top=30
        self.width=1200
        self.height=750
        self.setGeometry(self.left,self.top,self.width,self.height)
        self.iconPlay=self.icon+'Play.png'
        self.iconSnap=self.icon+'Snap.png'
        self.iconStop=self.icon+'Stop.png'
        self.iconBg=self.icon+'coin.png'
        self.iconPlay=pathlib.Path(self.iconPlay)
        self.iconPlay=pathlib.PurePosixPath(self.iconPlay)
        self.iconStop=pathlib.Path(self.iconStop)
        self.iconStop=pathlib.PurePosixPath(self.iconStop)
        self.iconSnap=pathlib.Path(self.iconSnap)
        self.iconSnap=pathlib.PurePosixPath(self.iconSnap)
        
        self.iconBg=pathlib.Path(self.iconBg)
        self.iconBg=pathlib.PurePosixPath(self.iconBg)
        
        self.setWindowIcon(QIcon(self.icon+'LOA.png'))
        self.setWindowTitle('FROG ')
        
        self.motorName="moteurTest"#"Moteur0A"
        self.motorType='MotorTest'#"A2V"
        self.configPath="./fichiersConfig/"
        self.configMotName='configMoteurTest.ini'#'configMoteurA2V.ini'
        
        self.confpath=str(p.parent) + sepa
        # print('confpath',self.confpath)
        
        self.bg=0
        self.motor=ONEMOTOR(mot0=self.motorName,motorTypeName0=self.motorType,unit=3,jogValue=1)
        self.motor.startThread2()
        
        MOT=self.motor.MOT
        self.scanWidget=SCAN(MOT=MOT,motor=self.motorName,configMotName=self.configPath+self.configMotName) # for the scan)
        
        
        
        listdevice=list_devices() ## open device flame spectrometer 
        try : 
            self.spectrometer=Spectrometer(listdevice[0])
            sh=int(self.confFrog.value('VISU'+'/shutter'))
            try:
                self.spectrometer.integration_time_micros(sh*1000) # en micro
            except: 
                self.spectrometer.integration_time_micros(100*1000)
        except :
            self.spectrometer=[]
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error connexion Spectrometer")
            msg.setInformativeText("Try to reconnect the USB or resart the program")
            msg.setWindowTitle("Spectrometer not connected...")
            msg.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            msg.exec_()
            pass
        print('__________  F R O G  __________')
        print('')
        print('  Version  : ',version)
        print("  Spectrometer connected @ ",self.spectrometer)
        self.wavelengths=self.spectrometer.wavelengths() # array Wavelengths of the spectrometer 
        print("  Wavelength : " ,self.wavelengths.min(),self.wavelengths.max())
        print('  Motor name: ',self.motorName,'  Type: ',self.motorType)
        print('')
        self.MatData=[]
        self.MatFs=[]
        self.position=0
        self.moyenne=1
        self.nbShot=1
        self.row=0
        self.setup()
        self.actionButton()
        
    def setup(self):
        
        hbox1=QHBoxLayout() # horizontal layout pour run snap stop
        self.sizebuttonMax=30
        self.sizebuttonMin=30
        self.runButton=QToolButton(self)
        self.runButton.setMaximumWidth(self.sizebuttonMax)
        self.runButton.setMinimumWidth(self.sizebuttonMax)
        self.runButton.setMaximumHeight(self.sizebuttonMax)
        self.runButton.setMinimumHeight(self.sizebuttonMax)
        self.runButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: green;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"% (self.iconPlay,self.iconPlay) )
        self.runButton.setToolTip("Free Run")
        self.snapButton=QToolButton(self)
        self.snapButton.setPopupMode(0)
        menu=QMenu()
        # menu.addAction('acq',self.oneImage)
        menu.addAction('set nb of shot',self.nbShotAction)
        self.snapButton.setMenu(menu)
        self.snapButton.setMaximumWidth(self.sizebuttonMax)
        self.snapButton.setMinimumWidth(self.sizebuttonMax)
        self.snapButton.setMaximumHeight(self.sizebuttonMax)
        self.snapButton.setMinimumHeight(self.sizebuttonMax)
        self.snapButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: green;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"% (self.iconSnap,self.iconSnap) )
        self.snapButton.setToolTip("Snap")
        self.stopButton=QToolButton(self)
        
        self.stopButton.setMaximumWidth(self.sizebuttonMax)
        self.stopButton.setMinimumWidth(self.sizebuttonMax)
        self.stopButton.setMaximumHeight(self.sizebuttonMax)
        self.stopButton.setMinimumHeight(self.sizebuttonMax)
        self.stopButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"% (self.iconStop,self.iconStop) )
        self.stopButton.setEnabled(False)
        self.stopButton.setToolTip("Stop Acquisition")
        self.bgButton=QToolButton(self)
        self.bgButton.setMaximumWidth(self.sizebuttonMax)
        self.bgButton.setMinimumWidth(self.sizebuttonMax)
        self.bgButton.setMaximumHeight(self.sizebuttonMax)
        self.bgButton.setMinimumHeight(self.sizebuttonMax)
        self.bgButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"% (self.iconBg,self.iconBg) )
        self.bgButton.setToolTip("Take a Background")
        
        self.bgLayout=QHBoxLayout()
        self.bgLayout.setContentsMargins(0,0,0,0)
        self.bgLabel=QLabel('Background :')
        self.bgLabel.setStyleSheet('font :bold  8pt')
        self.bgSoustract=QCheckBox()
        self.bgSoustract.setToolTip("Background Soustraction (On/Off)")
        self.bgLayout.addWidget(self.bgLabel)
        self.bgLayout.addWidget(self.bgSoustract)
        
        hbox1.addWidget(self.runButton)
        hbox1.addWidget(self.snapButton)
        hbox1.addWidget(self.stopButton)
        hbox1.addWidget(self.bgButton)
        hbox1.addLayout(self.bgLayout)
        hbox1.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        hbox1.setContentsMargins(5, 24, 0, 10)
        self.widgetControl=QWidget(self)
        
        self.widgetControl.setLayout(hbox1)
        self.dockControl=QDockWidget(self)
        self.dockControl.setWidget(self.widgetControl)
        self.dockControl.resize(80,80)
        
        self.trigg=QComboBox()
        self.trigg.setMaximumWidth(80)
        self.trigg.addItem('OFF')
        self.trigg.addItem('ON')
        self.trigg.setStyleSheet('font :bold  8pt;color: white')
        self.labelTrigger=QLabel('Trig')
        self.labelTrigger.setMaximumWidth(80)
        self.labelTrigger.setStyleSheet('font :bold  12pt')
        self.itrig=self.trigg.currentIndex()
        hbox2=QHBoxLayout()
        hbox2.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        hbox2.setContentsMargins(5, 26, 0, 0)
        hbox2.addWidget(self.labelTrigger)
        hbox2.addWidget(self.trigg)
        self.widgetTrig=QWidget(self)
        
        self.widgetTrig.setLayout(hbox2)
        self.dockTrig=QDockWidget(self)
        self.dockTrig.setWidget(self.widgetTrig)
        
        self.labelExp=QLabel('Exposure (ms)')
        self.labelExp.setStyleSheet('font :bold  10pt')
        self.labelExp.setMaximumWidth(500)
        self.labelExp.setAlignment(Qt.AlignCenter)
        
        self.hSliderShutter=QSlider(Qt.Horizontal)
        self.hSliderShutter.setMaximumWidth(80)
        self.hSliderShutter.setValue(int(self.confFrog.value('VISU'+'/shutter')))
        self.shutterBox=QSpinBox()
        self.shutterBox.setStyleSheet('font :bold  8pt')
        self.shutterBox.setMaximumWidth(200)
        self.hSliderShutter.setMaximum(1100)
        self.shutterBox.setMaximum(1100)
        self.shutterBox.setValue(int(self.confFrog.value('VISU'+'/shutter')))
        hboxShutter=QHBoxLayout()
        hboxShutter.setContentsMargins(5, 0, 0, 0)
        hboxShutter.setSpacing(10)
        vboxShutter=QVBoxLayout()
        vboxShutter.setSpacing(0)
        vboxShutter.addWidget(self.labelExp)#,Qt.AlignLef)
        
        hboxShutter.addWidget(self.hSliderShutter)
        hboxShutter.addWidget(self.shutterBox)
        vboxShutter.addLayout(hboxShutter)
        vboxShutter.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        vboxShutter.setContentsMargins(5, 5, 0, 0)
        
        self.widgetShutter=QWidget(self)
        
        self.widgetShutter.setLayout(vboxShutter)
        self.dockShutter=QDockWidget(self)
        self.dockShutter.setWidget(self.widgetShutter)
        
        
        
        self.labelMoy=QLabel('Average')
        self.labelMoy.setStyleSheet('font :bold  10pt')
        self.labelMoy.setMaximumWidth(120)
        self.labelMoy.setAlignment(Qt.AlignCenter)
        
       
        self.moyBox=QSpinBox()
        self.moyBox.setMaximumWidth(60)
        self.moyBox.setStyleSheet('font :bold  8pt')
        self.moyBox.setMaximum(100)
        self.moyBox.setValue(1)
        
        hboxMoy=QHBoxLayout()

        hboxMoy.addWidget(self.labelMoy)
        hboxMoy.addWidget(self.moyBox)
        
        hboxMoy.setSpacing(1)
        
        hboxMoy.setContentsMargins(5, 17, 200, 0)
        hbox2Moy=QHBoxLayout()
        hbox2Moy.addLayout(hboxMoy)
        hbox2Moy.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.widgetMoy=QWidget(self)
        self.widgetMoy.setLayout(hbox2Moy)
        
        self.dockMoy=QDockWidget(self)
        self.dockMoy.setWidget(self.widgetMoy)
        
        
        
        
        
        self.graph=GRAPHCUT(symbol=None,title='Spectra',pen='w',label='Wavelenght (nm)',labelY='int')
        self.widgetRange=self.graph.widgetRange
        self.widgetRange.labelXmin.setText("Wavelenght(nm) Min ")
        self.widgetRange.labelXmax.setText("Wavelenght(nm) Max ")
        self.dockControl.setTitleBarWidget(QWidget()) # to ovoid title
        self.graph.addDockWidget(Qt.TopDockWidgetArea,self.dockControl)
        self.dockTrig.setTitleBarWidget(QWidget())
        self.graph.addDockWidget(Qt.TopDockWidgetArea,self.dockTrig)
        self.dockShutter.setTitleBarWidget(QWidget())
        self.graph.addDockWidget(Qt.TopDockWidgetArea,self.dockShutter)
        self.dockMoy.setTitleBarWidget(QWidget())
        self.graph.addDockWidget(Qt.TopDockWidgetArea,self.dockMoy)
        
        
        
        self.hbox=QHBoxLayout()
        
        
        self.hbox.addWidget(self.graph)
        
        self.vLatBox=QVBoxLayout()
        # hboxRange=QHBoxLayout()
        # hboxRange.setAlignment(Qt.AlignCenter)
        # labelRange=QLabel('Range')
        # labelRange.setStyleSheet("font: bold 20pt;color:white")
        # hboxRange.addWidget(labelRange)
        # self.vLatBox.addLayout(hboxRange)
        self.vLatBox.addWidget(self.widgetRange)
        
        
        self.vLatBox.addStretch(0)
        self.vLatBox.addWidget(self.motor)
        self.vLatBox.addStretch(0)
        
        self.vLatBox.addWidget(self.scanWidget)
        # self.vLatBox.setContentsMargins(0,0,0,0)
        # self.vLatBox.setStretch(5,0)
        self.hbox.addLayout(self.vLatBox)
        self.hbox.setStretch(0, 3)
        #self.scanWidget.setStyleSheet('border-color:w')
        
        WidgetSpectro=QWidget()
        WidgetSpectro.setLayout(self.hbox)
        
        
        self.tabs=QTabWidget()
        self.tab0=WidgetSpectro
        
        self.tabs.addTab(self.tab0,'   Spectro & Motors    ')
        
        
        self.WidgetResult=SEERESULT(confpath=self.confpath+'confFrog.ini') # graph 2D data vs motor position
        
        # self.hresultLayout=QHBoxLayout()
        # # self.hresultLayout.addWidget(self.visualisation)
        # WidgetResult.setLayout(self.hresultLayout)
        self.tab1=self.WidgetResult
        
        self.tabs.addTab(self.tab1,'    Results    ')
        
        
        self.setCentralWidget(self.tabs)
    
        self.threadOneAcq=ThreadOneAcq(self)
        self.threadOneAcq.newDataRun.connect(self.newImageReceived)#,QtCore.Qt.DirectConnection)
        self.threadOneAcq.newStateCam.connect(self.stateCam)
        self.threadRunAcq=ThreadRunAcq(self)
        self.threadRunAcq.newDataRun.connect(self.newImageReceived)
        
        self.threadBgAcq=THREADBGACQ(self)
        self.threadBgAcq.newDataRun.connect(self.newBgReceived)
        self.threadBgAcq.newStateCam.connect(self.stateCam)
        
    def actionButton(self): 
        '''action when button are pressed
        '''
        self.runButton.clicked.connect(self.acquireMultiImage)
        self.snapButton.clicked.connect(self.acquireOneImage)
        self.stopButton.clicked.connect(self.stopAcq)
        self.bgButton.clicked.connect(self.bgAcq)
        
        
        self.shutterBox.editingFinished.connect(self.shutter)    
        self.hSliderShutter.sliderReleased.connect(self.mSliderShutter)
        self.moyBox.editingFinished.connect(self.MoyenneAct)    
        self.scanWidget.acqMain.connect(self.acquireScan)
        
        self.scanWidget.scanStop.connect(self.endScan)
        
        self.scanWidget.startOn.connect(self.ResetData)
        
        # self.trigg.currentIndexChanged.connect(self.trigger)
    
    def MoyenneAct(self):
        self.moyenne=(self.moyBox.value())
        self.scanWidget.val_time.setValue(0.2+self.moyenne*self.shutterBox.value()/1000)
        #print(self.moyenne)
        
    def ResetData(self):
        ##◙ reset data when scan start
        self.MatData=[]
        self.MatFs=[]
        # print('reset DATMAT')
        
    def shutter (self):
        '''
        set exposure time 
        '''
        
        sh=self.shutterBox.value() # 
        self.hSliderShutter.setValue(sh) # set value of slider
        time.sleep(0.1)
        self.spectrometer.integration_time_micros(sh*1000) # en micro
        # print(sh)
        self.confFrog.setValue('VISU'+'/shutter',sh)
        self.MoyenneAct()
    
    
    def mSliderShutter(self): # for shutter slider 
        sh=self.hSliderShutter.value() 
        self.shutterBox.setValue(sh) # 
        self.spectrometer.integration_time_micros(sh*1000)
        self.confFrog.setValue('VISU'+'/shutter',sh)
    
    def acquireMultiImage(self):
        ''' 
            start the acquisition thread
        '''
        
        self.runButton.setEnabled(False)
        self.runButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconPlay,self.iconPlay))
        self.snapButton.setEnabled(False)
        self.snapButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconSnap,self.iconSnap))
        self.stopButton.setEnabled(True)
        self.stopButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconStop,self.iconStop) )
        self.trigg.setEnabled(False)
        self.bgButton.setEnabled(False)
        self.bgButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconBg,self.iconBg))
        
        self.threadRunAcq.newRun() # to set stopRunAcq=False
        self.threadRunAcq.start()
        self.camIsRunnig=True
    
    def acquireScan(self,pos,nbShoot):
        #acquire on image with scan program
        self.scanWidget.AcqRunning(acqRunning=True)
        self.nbShoot=nbShoot # numero du shoot
        
        self.acquireOneImage()
        self.position=pos # on recupere la valeur de la postion moteur a chaque acquisition
       
    
    def acquireOneImage(self):
        '''Start on acquisition
        '''
        # print('acquire on image spectro')
        self.imageReceived=False
        self.runButton.setEnabled(False)
        self.runButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconPlay,self.iconPlay))
        self.snapButton.setEnabled(False)
        self.snapButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color:gray}"%(self.iconSnap,self.iconSnap))
        self.bgButton.setEnabled(False)
        self.bgButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconBg,self.iconBg))
        
        
        self.stopButton.setEnabled(True)
        self.stopButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconStop,self.iconStop) )
        self.trigg.setEnabled(False)
        self.camIsRunnig=True
        self.threadOneAcq.newRun() # to set stopRunAcq=False
        self.threadOneAcq.start()
    
    
    def bgAcq(self):
        
        self.runButton.setEnabled(False)
        self.runButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconPlay,self.iconPlay))
        self.snapButton.setEnabled(False)
        self.snapButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color:gray}"%(self.iconSnap,self.iconSnap))
        
        self.bgButton.setEnabled(False)
        self.bgButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconBg,self.iconBg))
        
        self.stopButton.setEnabled(True)
        self.stopButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconStop,self.iconStop) )
        self.trigg.setEnabled(False)
        self.camIsRunnig=True
        self.threadBgAcq.newRun()
        self.threadBgAcq.start()
    
    def endScan (self):
        # at the end of the scan we plot MatData( 2d matrix of specta) vs MatFs (vector of the position of the motor) 
        self.MatDataNumpy=np.array(self.MatData)
        self.MatFsNumpy=np.array(self.MatFs)
    
        self.wavelengths=np.array(self.wavelengths)
        self.WidgetResult.newDataReceived(self.MatDataNumpy,axisX=self.MatFsNumpy,axisY=self.wavelengths)
        print('  ')
        print('  ')
        print(' ___RESULTS___')
        print('  dim matrice result :',self.MatDataNumpy.shape)
        print('  dim matrice fs :',len(self.MatFsNumpy))
        print('  dim matrice wavelengths : ',len(self.wavelengths))
        print('  ')
        print('  ')
        
        #self.MatFs=[]
        self.tabs.setCurrentIndex(1)
        self.stopAcq()
        
    
    def stateCam(self,state):
        self.camIsRunnig=state
        
    def newBgReceived(self,data):
        
        self.bg=data
        self.bgSoustract.setChecked(True)
        if self.camIsRunnig is False:
            self.stopAcq()
            
    def newImageReceived(self,data):
        
        if self.bgSoustract.isChecked():
            self.data=data-self.bg
            
        else :
            self.data=data
       
        self.graph.PLOT(self.data,axis=self.wavelengths)
       
        # self.MatData=np.append(self.MatData,self.data)
        self.MatData.append(self.data)
        # print(self.position)
        self.MatFs.append(self.position)
        
        self.scanWidget.AcqRunning(acqRunning=False)
        
        if self.camIsRunnig is False:
            self.stopAcq()
    
    def nbShotAction(self):
        '''
        number of snapShot
        '''
        nbShot, ok=QInputDialog.getInt(self,'Number of SnapShot ','Enter the number of snapShot ')
        if ok:
            self.nbShot=int(nbShot)
            if self.nbShot<=0:
                self.nbShot=1
               
               
    def stopAcq(self):
        '''Stop  acquisition
        '''
        
        self.runButton.setEnabled(True)
        self.runButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconPlay,self.iconPlay))
        self.snapButton.setEnabled(True)
        self.snapButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconSnap,self.iconSnap))
        
        self.bgButton.setEnabled(True)
        self.bgButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconBg,self.iconBg))
        
        
        
        self.stopButton.setEnabled(False)
        self.stopButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconStop,self.iconStop) )
        self.trigg.setEnabled(True)  
        
        self.threadRunAcq.stopThreadRunAcq()
    
    def closeEvent(self,event):
        # when the window is closed
        # to do close motor and spectro
        print('close')
        
class ThreadOneAcq(QtCore.QThread):
    
    '''Second thread for controling one or more  acquisition independtly
    '''
    newDataRun=QtCore.Signal(object)
    newStateCam=QtCore.Signal(bool)
    
    def __init__(self, parent):
        
        super(ThreadOneAcq,self).__init__(parent)
        self.parent=parent
        self.spectrometer = parent.spectrometer
        self.stopRunAcq=False
        self.itrig= parent.itrig
        
        
    def wait(self,seconds):
        time_end=time.time()+seconds
        while time.time()<time_end:
            QtGui.QApplication.processEvents()    
    
    def newRun(self):
        self.stopRunAcq=False
        
    def run(self):
        
        self.newStateCam.emit(True)
        
        for i in range (self.parent.nbShot):
            
            if self.stopRunAcq is not True :
                
                if i<self.parent.nbShot-1:
                    self.newStateCam.emit(True)
                    time.sleep(0.01)
                else:
                    self.newStateCam.emit(False)
                    time.sleep(0.01)
                data=0
                
                for m in range (self.parent.moyenne):
                    
                    dataSp=self.spectrometer.intensities()
                    data=data+dataSp
                    print('Acqusition Spectro',m+1,'/',self.parent.moyenne)
                data=data /self.parent.moyenne
                
                if np.max(data)>0:
                    
                    
                    if self.stopRunAcq==True:
                        pass
                    else :
                        
                        self.newDataRun.emit(data)
                time.sleep(0.1)  
                
                
            else:
                break
            
        self.newStateCam.emit(False)
        
        
        
    def stopThreadOneAcq(self):
        
        #self.cam0.send_trigger()
        self.stopRunAcq=True

        
class ThreadRunAcq(QtCore.QThread):
    
    '''Second thread for controling continus acquisition independtly
    '''
    newDataRun=QtCore.Signal(object)
    
    def __init__(self, parent):
        
        super(ThreadRunAcq,self).__init__(parent)
        self.parent=parent
        self.spectrometer = parent.spectrometer
        self.stopRunAcq=False
        self.itrig= parent.itrig
       
        
    def newRun(self):
        self.stopRunAcq=False
        
    def run(self):
        # print('moyenne',self.parent.moyenne)
        while self.stopRunAcq is not True :
            data=0
            for m in range (self.parent.moyenne):
                dataSp=self.spectrometer.intensities()
                data=data+dataSp
                # print(m)
                    
            data=data /self.parent.moyenne
                
            if np.max(data)>0:
                
                if self.stopRunAcq==True:
                    pass
                else :
                    self.newDataRun.emit(data)
            
            
    def stopThreadRunAcq(self):
        #self.cam0.send_trigger()
        self.stopRunAcq=True


class THREADBGACQ(QtCore.QThread):
    
    '''Second thread for controling one or more  acquisition independtly
    '''
    newDataRun=QtCore.Signal(object)
    newStateCam=QtCore.Signal(bool)
    
    def __init__(self, parent):
        
        super(THREADBGACQ,self).__init__(parent)
        self.parent=parent
        self.spectrometer = parent.spectrometer
        self.stopRunAcq=False
        self.itrig= parent.itrig
        
        
    def wait(self,seconds):
        time_end=time.time()+seconds
        while time.time()<time_end:
            QtGui.QApplication.processEvents()    
    
    def newRun(self):
        self.stopRunAcq=False
        
    def run(self):
        
        self.newStateCam.emit(True)
        
        for i in range (self.parent.nbShot):
            
            if self.stopRunAcq is not True :
               
                if i<self.parent.nbShot-1:
                    self.newStateCam.emit(True)
                    time.sleep(0.01)
                else:
                    self.newStateCam.emit(False)
                    time.sleep(0.01)
                data=0
                
                for m in range (self.parent.moyenne):
                    #print('moy',m)
                    dataSp=self.spectrometer.intensities()
                    data=data+dataSp
                    
                data=data /self.parent.moyenne
                
                if np.max(data)>0:
                    
                    
                    if self.stopRunAcq==True:
                        pass
                    else :
                        
                        self.newDataRun.emit(data)
                time.sleep(0.1)  
                
                
            else:
                break
            
        self.newStateCam.emit(False)
        
        
        
    def stopThreadOneAcq(self):
        
        #self.cam0.send_trigger()
        self.stopRunAcq=True


if __name__ == "__main__":
    
    appli = QApplication(sys.argv) 
    appli.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    e = FROG()
    e.show()
    appli.exec_() 