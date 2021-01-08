#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 20:23:31 2019

@author: juliengautier
"""

#%%Import
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication,QSizePolicy
from PyQt5.QtWidgets import QWidget,QMessageBox,QLineEdit,QFrame
from PyQt5.QtWidgets import QVBoxLayout,QHBoxLayout,QPushButton,QGridLayout,QDoubleSpinBox
from PyQt5.QtWidgets import QComboBox,QCheckBox,QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sys,time,os
import qdarkstyle
import numpy as np


class SCAN(QWidget):
    
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
        
        self.indexUnit=3 #fs
        self.name=str(self.conf.value(self.motor+"/Name"))
        
        self.stepmotor=float(self.conf.value(self.motor+"/stepmotor"))
        self.setup()
        self.actionButton()
        self.unit()
        self.threadScan=ThreadScan(self)
        self.threadScan.nbRemain.connect(self.Remain)
        self.setWindowIcon(QIcon('./icons/LOA.png'))
        self.setWindowTitle('Scan'+' : '+ self.name)
        
        
    def setup(self):
        
        self.vbox=QVBoxLayout()
        
        hboxScan=QHBoxLayout()
        hboxScan.setAlignment(Qt.AlignCenter)
        labelScan=QLabel('Scan')
        labelScan.setStyleSheet("font: bold 20pt;color:yellow")
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
        self.unitBouton.addItem('ps')
        self.unitBouton.addItem('°')
        self.unitBouton.setMaximumWidth(100)
        self.unitBouton.setMinimumWidth(100)
        self.unitBouton.setCurrentIndex(self.indexUnit)
        
        #hboxTitre.addWidget(self.unitBouton)
        
        lab_nbStepRemain=QLabel('Remaining step :')
        self.val_nbStepRemain=QLabel(self)
        
        hboxRemain.addWidget(lab_nbStepRemain)
        hboxRemain.addWidget(self.val_nbStepRemain)
        
        
        
        sizeWidth=70
        self.lab_nbr_step = QLabel('nb of step :')
        self.val_nbr_step = QDoubleSpinBox(self)
        self.val_nbr_step.setDecimals(0)
        self.val_nbr_step.setMaximum(10000)
        self.val_nbr_step.setMinimum(1)
        self.val_nbr_step.setValue=10
        self.val_nbr_step.setMaximumWidth(sizeWidth)
        
        self.lab_step = QLabel("step value")
        self.val_step = QDoubleSpinBox()
        self.val_step.setDecimals(0)
        self.val_step.setMaximum(10000)
        self.val_step.setMinimum(-10000)
        self.val_step.setMaximumWidth(sizeWidth)
        
        self.lab_ini = QLabel('ini value')
        self.val_ini =QDoubleSpinBox()
        self.val_ini.setDecimals(0)
        self.val_ini.setMaximum(10000)
        self.val_ini.setMinimum(-10000)
        self.val_ini.setMaximumWidth(sizeWidth)
        
        self.lab_fin = QLabel('Final value')
        self.val_fin =QDoubleSpinBox()
        self.val_fin.setDecimals(0)
        self.val_fin.setMaximum(10000)
        self.val_fin.setMinimum(-10000)
        self.val_fin.setValue(100)
        self.val_fin.setMaximumWidth(sizeWidth)
        
        self.lab_nbTir=QLabel('Nb Average')
        self.val_nbTir=QDoubleSpinBox()
        self.val_nbTir.setDecimals(0)
        self.val_nbTir.setMaximum(100)
        self.val_nbTir.setValue(1)
        self.val_nbTir.setMaximumWidth(sizeWidth)
        
        self.lab_time=QLabel('Timeout')
        self.val_time=QDoubleSpinBox()
        self.val_time.setSuffix(" %s" % 's')
        self.val_time.setMaximum(10)
        self.val_time.setValue(2)
        self.val_time.setMaximumWidth(sizeWidth)
        
        self.but_start = QPushButton('Start')
        self.but_start.setStyleSheet("border-radius:20px;background-color: green")
        self.but_stop  = QPushButton('STOP')
        self.but_stop.setStyleSheet("border-radius:20px;background-color: red")
        self.but_stop.setEnabled(False)
        
        
        
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(10)
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
        grid_layout.addWidget(self.lab_nbTir,2,0)
        grid_layout.addWidget(self.val_nbTir,2,1)
        grid_layout.addWidget(self.lab_time,2,2)
        grid_layout.addWidget(self.val_time,2,3)
       
        hboxTitre.addWidget(self.but_start)
        hboxTitre.addWidget(self.but_stop)
        self.vbox.addLayout(grid_layout)
        self.setLayout(self.vbox)
 
    
    def actionButton(self):
    
        '''
           buttons action setup 
        '''
        self.unitBouton.currentIndexChanged.connect(self.unit)
        self.val_nbr_step.editingFinished.connect(self.stepChange)
        self.val_ini.editingFinished.connect(self.stepChange)
        self.val_fin.editingFinished.connect(self.stepChange)
        self.val_step.editingFinished.connect(self.changeFinal)
        self.but_start.clicked.connect(self.startScan)
        self.but_stop.clicked.connect(self.stopScan)
        
        
        
        
        
        
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
        self.val_nbTir.setEnabled(True)
        self.lab_time.setEnabled(True)
        self.val_time.setEnabled(True)
        self.but_start.setEnabled(True)
        
        self.but_stop.setEnabled(False)
        self.but_stop.setStyleSheet("border-radius:20px;background-color: red")
        
        
        
    def Remain(self,nbstepdone)   :
        print('remain',nbstepdone,self.nbStep)
        
        self.val_nbStepRemain.setText(str((self.nbStep*self.val_nbShoot)-nbstepdone))
        
        if self.nbStep*self.val_nbShoot==nbstepdone:
            print ('fin scan')
            self.stopScan()
            
    def RemainShoot(self,nbstepdone)   :
        print('remain shoot',nbstepdone,self.nbStep)
        
        self.val_nbStepRemain.setText(str((self.val_nbShoot)-nbstepdone))
        
        if self.val_nbShoot==nbstepdone:
            print ('fin scan multi Average')
            self.stopScan()
            
    def stepChange(self):
        self.nbStep=self.val_nbr_step.value()
        self.vInit=self.val_ini.value()
        self.vFin=self.val_fin.value()
        self.vStep=(self.vFin-self.vInit)/self.nbStep
        self.val_step.setValue(self.vStep)
        self.val_nbShoot=self.val_nbTir.value()
        
    def changeFinal(self):
       self.nbStep=self.val_nbr_step.value()
       self.vInit=self.val_ini.value()
       self.vStep=self.val_step.value()
       self.vFin=self.vInit+(self.nbStep)*self.vStep
       self.val_fin.setValue(self.vFin)
       self.val_nbShoot=self.val_nbTir.value()
    
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
    
    def unit(self):
        '''
        unit change mot foc
        '''
        ii=self.unitBouton.currentIndex()
        if ii==0: #  step
            self.unitChange=1
            self.unitName='step'
            
        if ii==1: # micron
            self.unitChange=float((1*self.stepmotor)) 
            self.unitName='um'
        if ii==2: #  mm 
            self.unitChange=float((1000*self.stepmotor))
            self.unitName='mm'
        if ii==3: #  fs  double passage : 1 microns=6fs
            self.unitChange=float(1000*self.stepmotor/0.0066666666) 
            self.unitName='fs'
        if ii==4: #  en degres
            self.unitChange=1 *self.stepmotor
            self.unitName='°'    
            
        if self.unitChange==0:
            self.unitChange=1 #avoid 0 
        
        self.val_step.setSuffix(" %s" % self.unitName)
        self.val_ini.setSuffix(" %s" % self.unitName)
        self.val_fin.setSuffix(" %s" % self.unitName)
 
    def closeEvent(self, event):
        """ when closing the window
        """
        self.isWinOpen=False
       
        time.sleep(0.1)
        event.accept() 
    

        
class ThreadScan(QtCore.QThread):
   
    nbRemain=QtCore.pyqtSignal(float)
    
    def __init__(self, parent=None):
        super(ThreadScan,self).__init__(parent)
        self.parent = parent
        self.stop=False

    def run(self):
        
        self.stop=False
#        print('number of steps:', self.parent.nbStep,self.parent.unitName)
#        print('Initial position:',self.parent.vInit,self.parent.unitName)
#        print('final position:',self.parent.vFin,self.parent.unitName)
#        print('step value',self.parent.vStep,self.parent.unitName)
#        print('nb of shoot for one postion',self.parent.val_nbTir.value())
        self.vini=self.parent.vInit*self.parent.unitChange
        self.vfin=self.parent.vFin*self.parent.unitChange
        self.step=self.parent.vStep*self.parent.unitChange
        
        self.val_time=self.parent.val_time.value()
        print('timeouts',self.val_time)
        self.parent.MOT.move(self.vini)
        
        b=self.parent.MOT.position()
        while b!=self.vini:
            if self.stop==True:
                break
            else:	
                time.sleep(1)
                b=self.parent.MOT.position()
        time.sleep(0.5)
        print(self.vini,self.vfin,self.step)
        movement=np.arange(self.vini+self.step,self.vfin+self.step,self.step)
        print (movement,"start scan",self.parent.unitChange)
        nb=0
        for mv in movement:
            
            if self.stop==True:
                break
            else:
                mv=int(mv)
                self.parent.MOT.move(mv)
                b=self.parent.MOT.position()
                b=int(b)
                while True:
                    if self.stop==True:
                        break
                    else :
                        b=self.parent.MOT.position()
                        print (b,mv)
                        if b==mv:
                            print( "position reached")
                            break
                
                for nu in range (0,int(self.parent.val_nbTir.value())):
                    nb+=1
                    print('acq spectro')
                        
                    print('wait',self.val_time)
                    time.sleep(self.val_time)
        print ("fin du scan")

    def stopThread(self):
        self.stop=True
        print( "stop thread" )  

       
if __name__=='__main__':
    appli=QApplication(sys.argv)
    import moteurtest as test
    motorType=test
    motor="testMot1"
    MOT=test.MOTORTEST(motor)
    print('name',MOT.name())
    s=SCAN(MOT=MOT,motor=motor,configMotName='./fichiersConfig/configMoteurTest.ini') # for the scan)
        
    s.show()
    appli.exec_()