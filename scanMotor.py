#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 20:23:31 2019

@author: juliengautier
"""

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget,QToolButton,QFrame
from PyQt5.QtWidgets import QVBoxLayout,QHBoxLayout,QGridLayout,QDoubleSpinBox,QProgressBar
from PyQt5.QtWidgets import QComboBox,QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sys,time
import qdarkstyle
import numpy as np


class SCAN(QWidget):
    acqMain=QtCore.pyqtSignal(float,int)
    startOn=QtCore.pyqtSignal(bool)
    scanStop=QtCore.pyqtSignal(bool)
    
    
    def __init__(self, MOT='',motor='',configMotName='',parent=None):
        
        super(SCAN, self).__init__(parent)
        
        self.isWinOpen=False
        self.parent=parent
        
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        #self.setStyleSheet("border-color:red")
        self.MOT=MOT 
        self.motor=motor
        self.configMotName=configMotName
       
        self.conf=QtCore.QSettings(self.configMotName, QtCore.QSettings.IniFormat)
        self.stepmotor=float(self.conf.value(self.motor+"/stepmotor"))
        self.indexUnit=3 #fs
        self.name=str(self.conf.value(self.motor+"/Name"))
        self.threadScan=ThreadScan(self)
        
        self.setup()
        self.actionButton()
        self.unit()
        self.isrunnig=False
        self.threadScan.nbRemain.connect(self.Remain)
        self.setWindowIcon(QIcon('./icons/LOA.png'))
        self.setWindowTitle('Scan'+' : '+ self.name)
        
        
    def setup(self):
        
        self.vbox=QVBoxLayout()
        
        hboxScan=QHBoxLayout()
        hboxScan.setAlignment(Qt.AlignCenter)
        labelScan=QLabel('SCAN')
        labelScan.setStyleSheet("font: bold 20pt;color:white")
        hboxScan.addWidget(labelScan)
        self.vbox.addLayout(hboxScan)
        
        
        hboxTitre=QHBoxLayout()
        hboxRemain=QHBoxLayout()
        # self.nom=QLabel(self.name)
        # self.nom.setStyleSheet("font: bold 30pt")
        # hboxTitre.addWidget(self.nom)
        self.vbox.addLayout(hboxTitre)
        self.vbox.addLayout(hboxRemain)
        self.unitBouton=QComboBox()
        self.unitBouton.addItem('Step')
        self.unitBouton.addItem('um')
        self.unitBouton.addItem('mm')
        self.unitBouton.addItem('fs')
        self.unitBouton.addItem('°')
        self.unitBouton.setMaximumWidth(100)
        self.unitBouton.setMinimumWidth(100)
        self.unitBouton.setCurrentIndex(self.indexUnit)
        
        #hboxTitre.addWidget(self.unitBouton)
        sizeWidth=80
        sizeHeight=40
        font="font:14pt"
        
        
        lab_nbStepRemain=QLabel('Remaining step :')
        lab_nbStepRemain.setStyleSheet(font)
        self.val_nbStepRemain=QLabel(self)
        
        hboxRemain.addWidget(lab_nbStepRemain)
        hboxRemain.addWidget(self.val_nbStepRemain)
        self.progressBar=QProgressBar()
        self.progressBar.setMinimumHeight(sizeHeight)
        hboxRemain.addWidget(self.progressBar)
        
        
        
        self.lab_nbr_step = QLabel('nb of step :')
        self.lab_nbr_step.setStyleSheet(font)
        self.val_nbr_step = QDoubleSpinBox(self)
        self.val_nbr_step.setDecimals(0)
        self.val_nbr_step.setMaximum(10000)
        self.val_nbr_step.setMinimum(1)
        self.val_nbr_step.setValue(20)
        self.val_nbr_step.setMaximumWidth(sizeWidth)
        self.val_nbr_step.setMaximumHeight(sizeHeight)
        self.val_nbr_step.setMinimumHeight(sizeHeight)
        self.val_nbr_step.setStyleSheet(font)
        self.lab_step = QLabel("Step value:")
        self.lab_step.setStyleSheet(font)
        self.val_step = QDoubleSpinBox()
        self.val_step.setDecimals(0)
        self.val_step.setMaximum(10000)
        self.val_step.setMinimum(-10000)
        self.val_step.setValue(50)
        self.val_step.setMaximumWidth(sizeWidth)
        self.val_step.setMaximumHeight(sizeHeight)
        self.val_step.setMinimumHeight(sizeHeight)
        self.val_step.setStyleSheet(font)
        self.lab_ini = QLabel('Init value:')
        self.lab_ini.setStyleSheet(font)
        self.val_ini =QDoubleSpinBox()
        self.val_ini.setDecimals(0)
        self.val_ini.setMaximum(100000)
        self.val_ini.setMinimum(-100000)
        self.val_ini.setMaximumWidth(sizeWidth)
        self.val_ini.setMaximumHeight(sizeHeight)
        self.val_ini.setMinimumHeight(sizeHeight)
        self.val_ini.setStyleSheet(font)
        self.lab_fin = QLabel('Final value:')
        self.lab_fin.setStyleSheet(font)
        self.val_fin =QDoubleSpinBox()
        self.val_fin.setDecimals(0)
        self.val_fin.setMaximum(100000)
        self.val_fin.setMinimum(-10000)
        self.val_fin.setValue(1000)
        self.val_fin.setMaximumWidth(sizeWidth)
        self.val_fin.setMaximumHeight(sizeHeight)
        self.val_fin.setMinimumHeight(sizeHeight)
        self.val_fin.setStyleSheet(font)
        self.lab_nbTir=QLabel('Nb Average')
        self.lab_nbTir.setStyleSheet(font)
        self.val_nbTir=QDoubleSpinBox()
        self.val_nbTir.setDecimals(0)
        self.val_nbTir.setMaximum(100)
        self.val_nbTir.setValue(1)
        self.val_nbTir.setMaximumWidth(sizeWidth)
        self.val_nbTir.setEnabled(False)
        
        self.lab_time=QLabel('TimeOut:')
        self.lab_time.setStyleSheet(font)
        self.val_time=QDoubleSpinBox()
        self.val_time.setSuffix(" %s" % 's')
        self.val_time.setMaximum(20)
        self.val_time.setValue(0.2)
        self.val_time.setMaximumWidth(sizeWidth)
        self.val_time.setMaximumHeight(sizeHeight)
        self.val_time.setMinimumHeight(sizeHeight)
        self.val_time.setStyleSheet(font)
        self.but_start = QToolButton()
        self.but_start.setText(' START ')
        self.but_start.setStyleSheet("border-radius:20px;background-color: green;font:24pt")
        self.but_start.setMaximumHeight((sizeHeight))
        self.but_start.setMinimumHeight((sizeHeight))
        self.but_start.setMinimumWidth((sizeWidth))
        
        self.but_stop  = QToolButton()
        self.but_stop.setText(' STOP ')
        self.but_stop.setStyleSheet("border-radius:20px;background-color: red;font:24pt")
        self.but_stop.setMinimumHeight((sizeHeight))
        self.but_stop.setMinimumWidth((sizeWidth))
        self.but_stop.setEnabled(False)
        
        
        
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(1)
        grid_layout.addWidget(self.lab_nbr_step  , 0, 0)
        grid_layout.addWidget(self.val_nbr_step  , 0, 1)
        grid_layout.addWidget(self.lab_step  , 0, 2)
        grid_layout.addWidget(self.val_step  , 0, 3)
        #grid_layout.addWidget(self.but_start,0,4)
        grid_layout.addWidget(self.lab_ini,1,0)
        grid_layout.addWidget(self.val_ini,1,1)
        grid_layout.addWidget(self.lab_fin,1,2)
        grid_layout.addWidget(self.val_fin,1,3)
        #grid_layout.addWidget(self.but_stop,1,4)
        # grid_layout.addWidget(self.lab_nbTir,2,0)
        # grid_layout.addWidget(self.val_nbTir,2,1)
        grid_layout.addWidget(self.lab_time,2,0)
        grid_layout.addWidget(self.val_time,2,1)
       
        hboxTitre.addWidget(self.but_start)
        hboxTitre.addWidget(self.but_stop)
        self.vbox.addLayout(grid_layout)
        
        
        Frame=QFrame()
        Frame.setStyleSheet('background-color: rgb(20, 20, 20);border-radius:40px;')
        Frame.setLayout(self.vbox)
        self.vMain=QVBoxLayout()
        self.vMain.addWidget(Frame)
        self.setLayout(self.vMain)
 
    
    def actionButton(self):
    
        '''
           buttons action setup 
        '''
        self.unitBouton.currentIndexChanged.connect(self.unit)
        #self.val_nbr_step.editingFinished.connect(self.stepChange)
        
        self.val_ini.editingFinished.connect(self.stepChange)
        self.val_fin.editingFinished.connect(self.stepChange)
        self.val_step.editingFinished.connect(self.stepChange)
        
        
        self.but_start.clicked.connect(self.startScan)
        self.but_stop.clicked.connect(self.stopScan)
        
        
        self.threadScan.nbRemain.connect(self.Remain)
        self.threadScan.acqScan.connect(self.Acq)
        
        
        
    def Acq(self,pos,nbShoot):
        
        # print('position acquise',pos/self.unitChange,self.unitChange,self.unitName)
        self.acqMain.emit(pos/self.unitChange,nbShoot) # emit signal to acquire and emit the shot number 
    
    def AcqRunning(self,acqRunning=False):
        self.isrunnig=acqRunning
        
    def stopScan(self):
        
        self.threadScan.stopThread()
        self.MOT.stopMotor()
        self.lab_nbr_step.setEnabled(True)
        self.val_nbr_step.setEnabled(True)
        self.lab_step.setEnabled(True)
        self.lab_ini.setEnabled(True)
        self.val_step.setEnabled(True)
        self.val_ini.setEnabled(True)
        self.lab_fin.setEnabled(True)
        self.val_fin.setEnabled(True)
        self.lab_nbTir.setEnabled(True)
        self.val_nbTir.setEnabled(False)
        self.lab_time.setEnabled(True)
        self.val_time.setEnabled(True)
        self.but_start.setEnabled(True)
        
        self.but_stop.setEnabled(False)
        self.but_stop.setStyleSheet("border-radius:20px;background-color: red")
        self.scanStop.emit(True) # emit signal at the end of the scan
        print('stop scan')
        
        
    def Remain(self,nbstepdone,shotmax)   :
        
        # print('remain',nbstepdone,self.nbStep)
        self.progressBar.setMaximum(int(shotmax))
        self.val_nbStepRemain.setText(str(nbstepdone) )  #Ì(str((self.nbStep*self.val_nbShoot)-nbstepdone))
        self.progressBar.setValue(int(shotmax-nbstepdone))
        # if self.nbStep*self.val_nbShoot==nbstepdone:
        #     # print ('fin scan')
        #     self.stopScan()
            
    
            
    def stepChange(self):
        
        self.vInit=self.val_ini.value()
        self.vFin=self.val_fin.value()
        self.vStep=self.val_step.value()
        
        self.val_step.setValue(self.vStep)
        
        self.nbStep=(self.vFin-self.vInit)/self.vStep
        self.nbStep=int(abs(self.nbStep))
        self.val_nbr_step.setValue(self.nbStep)
        
        self.val_nbShoot=1#self.val_nbTir.value()#
        
    def changeFinal(self):
       self.nbStep=self.val_nbr_step.value()
       self.vInit=self.val_ini.value()
       self.vStep=self.val_step.value()
       self.vFin=self.vInit+(self.nbStep)*self.vStep
       self.val_fin.setValue(self.vFin)
       self.val_nbShoot=1#self.val_nbTir.value()
    
    def startScan(self):
        self.stepChange()
        self.threadScan.start()
        self.lab_nbr_step.setEnabled(False)
        self.val_nbr_step.setEnabled(False)
        self.lab_step.setEnabled(False)
        self.lab_ini.setEnabled(False)
        self.val_step.setEnabled(False)
        self.val_ini.setEnabled(False)
        self.lab_fin.setEnabled(False)
        self.val_fin.setEnabled(False)
        self.lab_nbTir.setEnabled(False)
        self.val_nbTir.setEnabled(False)
        self.lab_time.setEnabled(False)
        self.val_time.setEnabled(False)
        self.but_start.setEnabled(False)
        
        self.but_stop.setEnabled(True)
        self.but_stop.setStyleSheet("border-radius:20px;background-color: red")
        self.startOn.emit(True) #emit signal at the end of the scan
        
        
    def unit(self):
        '''
        unit change mot foc
        '''
        ii=self.unitBouton.currentIndex()
        # print(ii,'index')
        if ii==0: #  step
            self.unitChange=1
            self.unitName='step'
            
        if ii==1: # micron
            self.unitChange=float((1*self.stepmotor)) 
            self.unitName='um'
        if ii==2: #  mm 
            # print('ici step montor ', self.stepmotor)
            self.unitChange=float((1000*self.stepmotor))
            self.unitName='mm'
        if ii==3: #  fs  double passage : 1 microns=6fs
            self.unitChange=float(self.stepmotor/6.6666666) 
            self.unitName='fs'
        if ii==4: #  en degres
            self.unitChange=1 *self.stepmotor
            self.unitName='°'    
        # print(self.unitChange)
        if self.unitChange==0:
            self.unitChange=1 #avoid 0 
        
        self.val_step.setSuffix(" %s" % self.unitName)
        self.val_ini.setSuffix(" %s" % self.unitName)
        self.val_fin.setSuffix(" %s" % self.unitName)
        # print('unitChange main',self.unitChange)
    def closeEvent(self, event):
        """ when closing the window
        """
        self.isWinOpen=False
       
        time.sleep(0.1)
        event.accept() 
    

        
class ThreadScan(QtCore.QThread):
   
    nbRemain=QtCore.pyqtSignal(float,float)
    acqScan=QtCore.pyqtSignal(float,int)
    
    def __init__(self, parent=None):
        super(ThreadScan,self).__init__(parent)
        self.parent = parent
        self.stop=False

    def run(self):
        print('     Start Scan :     ' )
        self.stop=False
        
        # print('number of steps:', self.parent.nbStep,self.parent.unitName)
        # print('Initial position:',self.parent.vInit,self.parent.unitName)
        # print('final position:',self.parent.vFin,self.parent.unitName)
        # print('step value',self.parent.vStep,self.parent.unitName)
        # print('nb of shoot for one postion',self.parent.val_nbTir.value())
        self.vini=self.parent.vInit*self.parent.unitChange
        self.vfin=self.parent.vFin*self.parent.unitChange
        self.step=self.parent.vStep*self.parent.unitChange
        
        
        
        # print('unitChange scan',self.parent.unitChange)
        
        # print('step en mm',self.step)
        self.val_time=self.parent.val_time.value()
        # print('timeouts',self.val_time)
        self.parent.MOT.move(self.vini)
        
        b=self.parent.MOT.position()
        # print(b)
        while True:
            if self.vini-1< float(b) and b<=self.vini+1:
                break
            if self.stop==True:
                break
            else:	
                time.sleep(0.2)
                b=self.parent.MOT.position()
                # print(b,self.vini)
        time.sleep(0.5)
        #print(self.vini,self.vfin,self.step)
        movement=np.arange(float(self.vini),float(self.vfin)+float(self.step),float(self.step))
        #print (movement,"start scan",self.parent.unitChange)
        nb=0 # numero du tir
        mv=0
        nbTotShot=np.size(movement)*self.parent.val_nbTir.value()
       
        for mv in movement:
            # print (mv)
            if self.stop==True:
                break
            else:
                
                self.parent.MOT.move(mv)
                b=self.parent.MOT.position()
                
                while True:
                    if self.stop==True:
                        break
                    else :
                        b=self.parent.MOT.position()
                        time.sleep(0.1)
                        print (' Moving..., Actual position :',b,'Position to reach', mv)
                        if mv-1<b and b<=mv+1:
                            print( "position reached")
                            break 
                
                self.acqScan.emit(self.parent.MOT.position(),nb)
                print('Acquisition spectro en cours')
                while self.parent.isrunnig==True: # if cam is ruunig we wait
                    print('...',end='')#,self.parent.isrunnig)
                    if self.stop==True:
                        print('') 
                        break
                    else :

                        time.sleep(0.1)
                print('')       
                print('wait ... ',self.val_time)#,self.stop)
                print('  Acquisition done  ')#,self.parent.isrunnig)
                print('   ')
                nb=nb+1
                self.nbRemain.emit(nbTotShot-nb,nbTotShot)
                
                
                time.sleep(self.val_time)
        
        
        print ("    End Scan    ")
        print('Go back to 0')
        self.parent.MOT.move(0)
        b=self.parent.MOT.position()
        
        # go to zero @the end of the scan 
        while b!=0:
            if self.stop==True:
                break
            else:	
                time.sleep(1)
                b=self.parent.MOT.position()
         
        self.parent.stopScan()
        
    def stopThread(self):
        self.stop=True
        # print( "stop thread" )  

       
if __name__=='__main__':
    appli=QApplication(sys.argv)
    
    motorType='motorTest'
    motor="moteurTest"
    import moteurtest as mTest
    motorType=mTest
    MOT=motorType.MOTORTEST(motor) 
    
    s=SCAN(MOT=MOT,motor=motor,configMotName='./fichiersConfig/configMoteurTest.ini') # for the scan)
        
    s.show()
    appli.exec_()