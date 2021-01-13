#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 17:39:44 2020

@author: juliengautier
"""
import qdarkstyle 
from pyqtgraph.Qt import QtCore,QtGui 
from PyQt5.QtWidgets import QApplication,QVBoxLayout,QHBoxLayout,QPushButton,QMainWindow,QLabel,QDockWidget,QSlider,QInputDialog
from PyQt5.QtWidgets import QMenu,QWidget,QTableWidget,QTableWidgetItem,QAbstractItemView,QTabWidget,QComboBox,QToolButton,QSpinBox
import sys,time,os
from pyqtgraph.Qt import QtCore
from PyQt5.QtCore import Qt

from PyQt5.QtGui import QIcon

from visu.WinCut import GRAPHCUT

import pathlib
import numpy as np

from oneMotorSimpleFrog import ONEMOTOR
from scanMotor import SCAN
from visu import SEE2
from visualResult import SEERESULT

from seabreeze.spectrometers import Spectrometer, list_devices

class FROG(QMainWindow) :
    
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
        self.iconPlay=pathlib.Path(self.iconPlay)
        self.iconPlay=pathlib.PurePosixPath(self.iconPlay)
        self.iconStop=pathlib.Path(self.iconStop)
        self.iconStop=pathlib.PurePosixPath(self.iconStop)
        self.iconSnap=pathlib.Path(self.iconSnap)
        self.iconSnap=pathlib.PurePosixPath(self.iconSnap)
        self.setWindowIcon(QIcon(self.icon+'LOA.png'))
        self.setWindowTitle('FROG ')
        self.motorName="Moteur0A"
        self.motorType="Apt"
        self.configPath="./fichiersConfig/"
        self.configMotName='configMoteurApt.ini'
        self.motor=ONEMOTOR(mot0=self.motorName,motorTypeName0=self.motorType,unit=3,jogValue=1)
        self.motor.startThread2()
        
        MOT=self.motor.MOT
        self.scanWidget=SCAN(MOT=MOT,motor=self.motorName,configMotName=self.configPath+self.configMotName) # for the scan)
        listdevice=list_devices()
        self.spectrometer=Spectrometer(listdevice[0])
        print("spectrometer connected @",self.spectrometer)
        self.wavelengths=self.spectrometer.wavelengths() # array Wavelengths of the spectrometer 
        
        
        self.moyenne=1
        self.nbShot=1
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
        
        self.snapButton=QToolButton(self)
        self.snapButton.setPopupMode(0)
        menu=QMenu()
        #menu.addAction('acq',self.oneImage)
        menu.addAction('set nb of shot',self.nbShotAction)
        self.snapButton.setMenu(menu)
        self.snapButton.setMaximumWidth(self.sizebuttonMax)
        self.snapButton.setMinimumWidth(self.sizebuttonMax)
        self.snapButton.setMaximumHeight(self.sizebuttonMax)
        self.snapButton.setMinimumHeight(self.sizebuttonMax)
        self.snapButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: green;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"% (self.iconSnap,self.iconSnap) )
        
        self.stopButton=QToolButton(self)
        
        self.stopButton.setMaximumWidth(self.sizebuttonMax)
        self.stopButton.setMinimumWidth(self.sizebuttonMax)
        self.stopButton.setMaximumHeight(self.sizebuttonMax)
        self.stopButton.setMinimumHeight(self.sizebuttonMax)
        self.stopButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"% (self.iconStop,self.iconStop) )
        self.stopButton.setEnabled(False)
      
        hbox1.addWidget(self.runButton)
        hbox1.addWidget(self.snapButton)
        hbox1.addWidget(self.stopButton)
        hbox1.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        hbox1.setContentsMargins(0, 10, 0, 10)
        self.widgetControl=QWidget(self)
        
        self.widgetControl.setLayout(hbox1)
        self.dockControl=QDockWidget(self)
        self.dockControl.setWidget(self.widgetControl)
        self.dockControl.resize(80,80)
        
        self.trigg=QComboBox()
        self.trigg.setMaximumWidth(80)
        self.trigg.addItem('OFF')
        self.trigg.addItem('ON')
        self.trigg.setStyleSheet('font :bold  12pt;color: white')
        self.labelTrigger=QLabel('Trigger')
        self.labelTrigger.setMaximumWidth(70)
        self.labelTrigger.setStyleSheet('font :bold  12pt')
        self.itrig=self.trigg.currentIndex()
        hbox2=QHBoxLayout()
        hbox2.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        hbox2.setContentsMargins(5, 15, 0, 0)
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
        self.hSliderShutter.setValue(100)
        self.shutterBox=QSpinBox()
        self.shutterBox.setStyleSheet('font :bold  8pt')
        self.shutterBox.setMaximumWidth(200)
        self.hSliderShutter.setMaximum(5000)
        self.shutterBox.setMaximum(5000)
        self.shutterBox.setValue(100)
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
        hboxMoy.setContentsMargins(5, 15, 200, 0)
        hboxMoy.setSpacing(10)

        hboxMoy.addWidget(self.labelMoy)
        hboxMoy.addWidget(self.moyBox)
        
        self.widgetMoy=QWidget(self)
        self.widgetMoy.setLayout(hboxMoy)
        self.dockMoy=QDockWidget(self)
        self.dockMoy.setWidget(self.widgetMoy)
        
        
        
        
        
        self.graph=GRAPHCUT(symbol=None,title='Spectra',pen='w',label='Lambda (nm)',labelY='int')
        
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
        self.vLatBox.addWidget(self.motor)
        self.vLatBox.addStretch(1)
        
        self.vLatBox.addWidget(self.scanWidget)
        self.hbox.addLayout(self.vLatBox)
        
     
        
        WidgetSpectro=QWidget()
        WidgetSpectro.setLayout(self.hbox)
        
        
        self.tabs=QTabWidget()
        self.tab0=WidgetSpectro
        
        self.tabs.addTab(self.tab0,'   Spectro & Motors    ')
        
        WidgetResult=SEERESULT()
        
        # self.hresultLayout=QHBoxLayout()
        # # self.hresultLayout.addWidget(self.visualisation)
        # WidgetResult.setLayout(self.hresultLayout)
        self.tab1=WidgetResult
        
        self.tabs.addTab(self.tab1,'    Results    ')
        
        
        self.setCentralWidget(self.tabs)
    
        self.threadOneAcq=ThreadOneAcq(self)
        self.threadOneAcq.newDataRun.connect(self.newImageReceived)#,QtCore.Qt.DirectConnection)
        self.threadOneAcq.newStateCam.connect(self.stateCam)
        self.threadRunAcq=ThreadRunAcq(self)
        self.threadRunAcq.newDataRun.connect(self.newImageReceived)
        
    def actionButton(self): 
        '''action when button are pressed
        '''
        self.runButton.clicked.connect(self.acquireMultiImage)
        self.snapButton.clicked.connect(self.acquireOneImage)
        self.stopButton.clicked.connect(self.stopAcq)      
        self.shutterBox.editingFinished.connect(self.shutter)    
        self.hSliderShutter.sliderReleased.connect(self.mSliderShutter)
        self.moyBox.editingFinished.connect(self.MoyenneAct)    
        
        # self.trigg.currentIndexChanged.connect(self.trigger)
    def MoyenneAct(self):
        self.moyenne=(self.moyBox.value())
        
    
    def shutter (self):
        '''
        set exposure time 
        '''
        
        sh=self.shutterBox.value() # 
        self.hSliderShutter.setValue(sh) # set value of slider
        time.sleep(0.1)
        self.spectrometer.integration_time_micros(sh*1000) # en micro
    
    
    
    def mSliderShutter(self): # for shutter slider 
        sh=self.hSliderShutter.value() 
        self.shutterBox.setValue(sh) # 
        self.spectrometer.integration_time_micros(sh*1000)
        
    
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
        
        self.threadRunAcq.newRun() # to set stopRunAcq=False
        self.threadRunAcq.start()
        self.camIsRunnig=True
        
    def acquireOneImage(self):
        '''Start on acquisition
        '''
        print('acquire on image spectro')
        self.imageReceived=False
        self.runButton.setEnabled(False)
        self.runButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconPlay,self.iconPlay))
        self.snapButton.setEnabled(False)
        self.snapButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color:gray}"%(self.iconSnap,self.iconSnap))
        self.stopButton.setEnabled(True)
        self.stopButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconStop,self.iconStop) )
        self.trigg.setEnabled(False)
        self.camIsRunnig=True
        self.threadOneAcq.newRun() # to set stopRunAcq=False
        self.threadOneAcq.start()
        
    def stateCam(self,state):
        self.camIsRunnig=state
        print(state)
    
    def newImageReceived(self,data):
        self.data=data
        self.graph.PLOT(self.data,axis=self.wavelengths)
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

        self.stopButton.setEnabled(False)
        self.stopButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconStop,self.iconStop) )
        self.trigg.setEnabled(True)  
        
        self.threadRunAcq.stopThreadRunAcq()

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
        
        while self.stopRunAcq is not True :
            data=0
            for m in range (self.parent.moyenne):
                dataSp=self.spectrometer.intensities()
                data=data+dataSp
                    
            data=data /self.parent.moyenne
                
            if np.max(data)>0:
                
                if self.stopRunAcq==True:
                    pass
                else :
                    self.newDataRun.emit(data)
            
            
    def stopThreadRunAcq(self):
        #self.cam0.send_trigger()
        self.stopRunAcq=True




if __name__ == "__main__":
    
    appli = QApplication(sys.argv) 
    appli.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    e = FROG()
    e.show()
    appli.exec_() 