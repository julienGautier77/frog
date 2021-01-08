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
class FROG(QMainWindow) :
    
    def __init__(self):
        super().__init__()
        
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
        self.motorName="testMot1"
        self.motorType="test"
        self.configPath="./fichiersConfig/"
        self.configMotName='configMoteurTest.ini'
        self.motor=ONEMOTOR(mot0=self.motorName,motorTypeName0=self.motorType,unit=3,jogValue=1)
        self.scanWidget=SCAN(MOT=self.motor,motor=self.motorName,configMotName=self.configPath+self.configMotName) # for the scan)
        self.setup()
    
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
        self.labelExp.setMaximumWidth(120)
        self.labelExp.setAlignment(Qt.AlignCenter)
        
        self.hSliderShutter=QSlider(Qt.Horizontal)
        self.hSliderShutter.setMaximumWidth(80)
        self.shutterBox=QSpinBox()
        self.shutterBox.setStyleSheet('font :bold  8pt')
        self.shutterBox.setMaximumWidth(120)
        
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
        
        
        
        self.labelGain=QLabel('Gain')
        self.labelGain.setStyleSheet('font :bold  10pt')
        self.labelGain.setMaximumWidth(120)
        self.labelGain.setAlignment(Qt.AlignCenter)
        
        self.hSliderGain=QSlider(Qt.Horizontal)
        self.hSliderGain.setMaximumWidth(80)
        self.gainBox=QSpinBox()
        self.gainBox.setMaximumWidth(60)
        self.gainBox.setStyleSheet('font :bold  8pt')
        self.gainBox.setMaximumWidth(120)
        
        hboxGain=QHBoxLayout()
        hboxGain.setContentsMargins(5, 0, 0, 0)
        hboxGain.setSpacing(10)
        vboxGain=QVBoxLayout()
        vboxGain.setSpacing(0)
        vboxGain.addWidget(self.labelGain)

        hboxGain.addWidget(self.hSliderGain)
        hboxGain.addWidget(self.gainBox)
        vboxGain.addLayout(hboxGain)
        vboxGain.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        vboxGain.setContentsMargins(5, 5, 0, 0)
        
        self.widgetGain=QWidget(self)
        self.widgetGain.setLayout(vboxGain)
        self.dockGain=QDockWidget(self)
        self.dockGain.setWidget(self.widgetGain)
        
        
        
        
        
        self.graph=GRAPHCUT(symbol=None,title='Spectra',pen='w',label='Lambda (nm)',labelY='int')
        
        self.dockControl.setTitleBarWidget(QWidget()) # to ovoid title
        self.graph.addDockWidget(Qt.TopDockWidgetArea,self.dockControl)
        self.dockTrig.setTitleBarWidget(QWidget())
        self.graph.addDockWidget(Qt.TopDockWidgetArea,self.dockTrig)
        self.dockShutter.setTitleBarWidget(QWidget())
        self.graph.addDockWidget(Qt.TopDockWidgetArea,self.dockShutter)
        self.dockGain.setTitleBarWidget(QWidget())
        self.graph.addDockWidget(Qt.TopDockWidgetArea,self.dockGain)
        
        
        
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
    
    def nbShotAction(self):
        '''
        number of snapShot
        '''
        nbShot, ok=QInputDialog.getInt(self,'Number of SnapShot ','Enter the number of snapShot ')
        if ok:
            self.nbShot=int(nbShot)
            if self.nbShot<=0:
               self.nbShot=1



        
if __name__ == "__main__":
    
    appli = QApplication(sys.argv) 
    appli.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    e = FROG()
    e.show()
    appli.exec_() 