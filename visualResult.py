#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 15:07:27 2019

https://github.com/julienGautier77/visu.git

@author: juliengautier(LOA)
for dark style :
pip install qdarkstyle (https://github.com/ColinDuquesnoy/QDarkStyleSheet.git)

pip install pyqtgraph (https://github.com/pyqtgraph/pyqtgraph.git)
conda install pyopengl 3D plot

created 2021/11/02 : new design
"""




from PyQt5.QtWidgets import QApplication,QVBoxLayout,QHBoxLayout,QWidget,QPushButton,QGridLayout,QDoubleSpinBox
from PyQt5.QtWidgets import QInputDialog,QSlider,QLabel,QSizePolicy,QMenu,QMessageBox
from PyQt5.QtWidgets import QShortcut,QMainWindow,QAction,QStatusBar
from pyqtgraph.Qt import QtCore,QtGui 
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import pylab
import sys,time,os
import pyqtgraph as pg # pip install pyqtgraph (https://github.com/pyqtgraph/pyqtgraph.git)
import numpy as np
import qdarkstyle # pip install qdarkstyle https://github.com/ColinDuquesnoy/QDarkStyleSheet  sur conda
from scipy.interpolate import splrep, sproot #
from scipy.ndimage.filters import gaussian_filter,median_filter
from PIL import Image
from visu.winspec import SpeFile
from visu.winSuppE import WINENCERCLED
from visu.WinCut import GRAPHCUT
from visu.winMeas import MEAS
from visu.WinOption import OPTION
from visu.andor import SifFile
from visu.winFFT import WINFFT
from visu.winMath import WINMATH
from visu.WinPreference import PREFERENCES
try :
    from visu.Win3D import GRAPH3D #conda install pyopengl
except :
    print ('')
    
import pathlib
import visu
from scipy.optimize import curve_fit
__version__=visu.__version__
__author__=visu.__author__


__all__=['SEERESULT']


class WINDOWRANGE(QWidget):
    """Samll widget to set axis range
    """
    def __init__(self):
        super().__init__()
        self.isWinOpen=False
        self.setup()
        self.setWindowTitle("Range")
    def setup(self):
        #hRangeBox=QHBoxLayout()
        hRangeGrid=QGridLayout()
        
        self.labelXmin=QLabel('Xmin:')
        self.xMinBox=QDoubleSpinBox(self)
        self.xMinBox.setMinimum(-100000)
        self.xMinBox.setMaximum(100000)
        hRangeGrid.addWidget(self.labelXmin,0,0)
        hRangeGrid.addWidget(self.xMinBox,0,1)
        self.labelXmax=QLabel('Xmax:')
        self.xMaxBox=QDoubleSpinBox(self)
        self.xMaxBox.setMaximum(100000)
        self.xMaxBox.setMinimum(-100000)
        hRangeGrid.addWidget(self.labelXmax,1,0)
        hRangeGrid.addWidget(self.xMaxBox,1,1)
        
        self.labelYmin=QLabel('Ymin:')
        self.yMinBox=QDoubleSpinBox(self)
        self.yMinBox.setMinimum(-100000)
        self.yMinBox.setMaximum(100000)
        hRangeGrid.addWidget(self.labelYmin,2,0)
        hRangeGrid.addWidget(self.yMinBox,2,1)
        self.labelYmax=QLabel('Ymax:')
        self.yMaxBox=QDoubleSpinBox(self)
        self.yMaxBox.setMaximum(100000)
        self.yMaxBox.setMinimum(-100000)
        hRangeGrid.addWidget(self.labelYmax,3,0)
        hRangeGrid.addWidget(self.yMaxBox,3,1)
        self.applyButton=QPushButton('Apply')
        self.ResetButton=QPushButton('Reset')
        hRangeGrid.addWidget(self.applyButton,4,0)
        hRangeGrid.addWidget(self.ResetButton,4,1)
        hRangeGrid.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.setLayout(hRangeGrid)
        

        
    def closeEvent(self, event):
        """ when closing the window
        """
        self.isWinOpen=False
        
        time.sleep(0.1)
        event.accept()




class SEERESULT(QMainWindow) :
    
    '''
    open and plot file : 
        SEE(file='nameFile,path=pathFileName,confpath,confMot,name,aff)
        Make plot profile ands differents measurements(max,min mean...)
        Can open .spe .SPE .sif .TIFF files
        
        
        file = name of the file to open
        path=path of the file to open
        confpath=path  and  file name of the ini file if =None ini file will be the one in visu folder
        confMot usefull if RSAI motors is read
        name= name of the item  in the ini file could be usfull if there is more than two visu widget open in the  same   time
            default is  VISU
        
        kwds :
            aff = "right" or "left" display button on the  right or on the left
            fft="on" or "off" display 1d and 2D fft 
            plot3D 
    '''
   
    def __init__(self,file=None,path=None,parent=None,**kwds):
        
        super().__init__(parent)
        
        version=__version__
        print("data visualisation :  ",version)
        p = pathlib.Path(__file__)
        self.fullscreen=False
        self.setAcceptDrops(True)
        sepa=os.sep
        self.icon=str(p.parent) + sepa+'icons' +sepa
        self.colorBar='flame'
        self.parent=parent
        self.nomFichier=''
        
        
        ### kwds definition  : 
        
        if "confpath"in kwds :
            self.confpath=kwds["confpath"]
            self.conf=QtCore.QSettings(self.confpath, QtCore.QSettings.IniFormat)
            
        else:
            self.conf=QtCore.QSettings(str(p.parent / 'confVisu.ini'), QtCore.QSettings.IniFormat)
        
        
        if "name" in kwds:
            self.name=kwds["name"]
        else:
            self.name="VISU"
            
        
        
        if "aff" in kwds:
            self.aff=kwds["aff"]
        else :
            self.aff="right"
        
        if "fft" in kwds:
            self.fft=kwds["fft"]
        else:
            self.fft="off"
        
        if "meas" in kwds:
            self.meas=kwds["meas"]
        else:
           self.meas="on" 
           
        if "encercled" in kwds:
            self.encercled=kwds["encercled"]
        else:
            self.encercled="on"
        
        
        if self.fft=='on'  :  
            self.winFFT=WINFFT(conf=self.conf,name=self.name)
            self.winFFT1D=GRAPHCUT(symbol=None,title='FFT 1D',conf=self.conf,name=self.name)
          
        if "filter" in kwds:
            self.winFilter=kwds['filter']
        else :
            self.winFilter='on'
            
        if "confMot" in kwds:
            print('motor accepted')
            if self.meas=="on":
                self.confMot=kwds["confoMot"]
                self.winM=MEAS(confMot=self.confMot,conf=self.conf,name=self.name)
        else :
            if self.meas=="on":
                self.winM=MEAS(conf=self.conf,name=self.name)
            
        self.winOpt=OPTION(conf=self.conf,name=self.name)
        self.winPref=PREFERENCES(conf=self.conf,name=self.name)
        if self.encercled=="on":
            self.winEncercled=WINENCERCLED(conf=self.conf,name=self.name)
        
        if "plot3d" in kwds :
            self.plot3D=kwds["plot3d"]
        else:
            self.plot3D="off"
            
        if self.plot3D=="on":
            
            self.Widget3D=GRAPH3D(self.conf,name=self.name)
        
        
        if "math" in kwds:
            self.math=kwds["math"]
        else :
            self.math="on"
        
        if self.math=="on":
            self.winMath=WINMATH()
        
        self.winCoupe=GRAPHCUT(symbol=None,conf=self.conf,name=self.name)
        self.path=path
        self.setWindowTitle('Visualization'+'       v.'+ version)
        self.bloqKeyboard=bool((self.conf.value(self.name+"/bloqKeyboard"))  )  # block cross by keyboard
        self.bloqq=1 # block the cross by click on mouse
        
        # initialize variable : 
        self.filter='origin' # filter initial value
        self.ite=None
        self.setWindowIcon(QIcon(self.icon+'LOA.png'))
        self.zo=1 # zoom initial value
        self.scaleAxis="off"
        self.plotRectZoomEtat='Zoom'
        self.angleImage=0
        
        
        
        def twoD_Gaussian(x,y, amplitude, xo, yo, sigma_x, sigma_y, theta, offset):
           xo = float(xo)
           yo = float(yo)    
           a = (np.cos(theta)**2)/(2*sigma_x**2) + (np.sin(theta)**2)/(2*sigma_y**2)
           b = -(np.sin(2*theta))/(4*sigma_x**2) + (np.sin(2*theta))/(4*sigma_y**2)
           c = (np.sin(theta)**2)/(2*sigma_x**2) + (np.cos(theta)**2)/(2*sigma_y**2)
           return offset + amplitude*np.exp( - (a*((x-xo)**2) + 2*b*(x-xo)*(y-yo) + c*((y-yo)**2)))

        
        if file==None:
            # to have a gaussian picture when we start
            self.dimy=800
            self.dimx=800
            # Create x and y index
            self.x = np.arange(0,self.dimx)
            self.y = np.arange(0,self.dimy)
            self.y,self.x = np.meshgrid(self.y, self.x)
            
            self.data=twoD_Gaussian(self.x, self.y,200, 200, 600, 40, 40, 0, 10)+(50*np.random.rand(self.dimx,self.dimy)).round() 
        
            #self.data=(50*np.random.rand(self.dimx,self.dimy)).round() + 150
        else:
            if path==None:
                self.path=self.conf.value(self.name+"/path")
            
            self.data=self.OpenF(fileOpen=self.path+'/'+file)
        
        
        self.dataOrg=self.data
        self.dataOrgScale=self.data
        
        self.xminR=0
        self.xmaxR=self.dimx
        self.yminR=0
        self.ymaxR=self.dimy
        
        self.setup()
        self.shortcut()
        self.actionButton()
        self.activateWindow()
        self.raise_()
        self.showNormal()
        
        
        
    def setup(self):
        # definition of all button 
        self.hboxBar=QHBoxLayout() 
        
        #self.setStyleSheet("QCheckBox::indicator{width: 30px;height: 30px;}""QCheckBox::indicator:unchecked { image : url(%s);}""QCheckBox::indicator:checked { image:  url(%s);}""QCheckBox{font :10pt;QCheckBox{background-color :red}" % (TogOff,TogOn) )
        
        
        self.toolBar =self.addToolBar('tools')
        #self.setStyleSheet("{background-color: black}")
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        self.fileMenu = menubar.addMenu('&File')
        self.ImageMenu = menubar.addMenu('&Image')
        self.ProcessMenu = menubar.addMenu('&Process')
        self.AnalyseMenu = menubar.addMenu('&Analyse')
        self.Aboutenu = menubar.addMenu('&About')
        self.statusBar = QStatusBar()
        self.setContentsMargins(0, 0, 0, 0)
        
        self.setStatusBar(self.statusBar)
       
        
        self.vbox1=QVBoxLayout() 
        self.vbox1.setContentsMargins(0, 0, 0, 0)
        
        self.hbox0=QHBoxLayout()
        self.hbox0.setContentsMargins(0, 0, 0, 0)
        self.vbox1.addLayout(self.hbox0)
        
         
        self.openAct = QAction(QtGui.QIcon(self.icon+"Open.png"), 'Open File', self)
        self.openAct.setShortcut('Ctrl+o')
        self.openAct.triggered.connect(self.OpenF)
        self.toolBar.addAction(self.openAct)
        self.fileMenu.addAction(self.openAct)
        
        self.saveAct=QAction(QtGui.QIcon(self.icon+"disketteSave.png"), 'Save file', self)
        self.saveAct.setShortcut('Ctrl+s')
        self.saveAct.triggered.connect(self.SaveF)
        self.toolBar.addAction(self.saveAct)
        self.fileMenu.addAction(self.saveAct)

        
        self.checkBoxAutoSave=QAction(QtGui.QIcon(self.icon+"diskette.png"),'AutoSave on',self)
        self.checkBoxAutoSave.setCheckable(True)
        self.checkBoxAutoSave.setChecked(False)
        self.toolBar.addAction(self.checkBoxAutoSave)
        self.fileMenu.addAction(self.checkBoxAutoSave)
        
        
        self.optionAutoSaveAct=QAction(QtGui.QIcon(self.icon+"Settings.png"),'Option',self) #
        self.optionAutoSaveAct.triggered.connect(lambda:self.open_widget(self.winOpt))
        self.toolBar.addAction(self.optionAutoSaveAct)
        self.fileMenu.addAction(self.optionAutoSaveAct)
        
        
        self.checkBoxPlot=QAction(QtGui.QIcon(self.icon+"target.png"),'Cross On (ctrl+b to block ctrl+d to deblock)',self)
        self.checkBoxPlot.setCheckable(True)
        self.checkBoxPlot.setChecked(True)
        self.checkBoxPlot.triggered.connect(self.PlotXY)
        self.toolBar.addAction(self.checkBoxPlot)
        self.AnalyseMenu.addAction(self.checkBoxPlot)
        
        self.checkBoxPlotRect=QAction(QtGui.QIcon(self.icon+"Focus.png"),'Rectangular cut',self)
        self.checkBoxPlotRect.setCheckable(True)
        self.checkBoxPlotRect.setChecked(False)
        self.checkBoxPlotRect.triggered.connect(self.PlotXYRect)
        self.toolBar.addAction(self.checkBoxPlotRect)
        self.AnalyseMenu.addAction(self.checkBoxPlotRect)
        
        
        
        
        
        self.maxGraphBox=QAction('Set Cross on the max',self)
        self.maxGraphBox.setCheckable(True)
        self.maxGraphBox.setChecked(False)
        self.maxGraphBox.triggered.connect(self.Coupe)
        self.AnalyseMenu.addAction(self.maxGraphBox)
        
        
        
        self.label_CrossValue=QLabel()
        self.label_CrossValue.setStyleSheet("font:13pt")
        
        self.label_Cross=QLabel()
        #self.label_Cross.setMaximumHeight(20)
        self.label_Cross.setMaximumWidth(300)
        self.label_Cross.setStyleSheet("font:10pt")
        self.statusBar.addPermanentWidget(self.label_Cross)
        self.statusBar.addPermanentWidget(self.label_CrossValue)
        
        self.labelFileName=QLabel("File :")
        self.labelFileName.setStyleSheet("font:12pt;")
        self.labelFileName.setMinimumHeight(30)
        self.labelFileName.setMaximumWidth(40)
        
        self.fileName=QLabel()
        self.fileName.setStyleSheet("font:12pt")
        self.fileName.setMaximumHeight(30)
        self.fileName.setMaximumWidth(200000)
        #self.fileName.setAlignment(Qt.AlignRight)
        self.statusBar.addWidget(self.labelFileName)
        self.statusBar.addWidget(self.fileName)
         
        self.checkBoxScale=QAction(QtGui.QIcon(self.icon+"resize.png"),'Auto Scale on',self)
        self.checkBoxScale.setCheckable(True)
        self.checkBoxScale.triggered.connect(self.autoScale)
        self.checkBoxScale.setChecked(True)
        self.toolBar.addAction(self.checkBoxScale)
        self.ImageMenu.addAction(self.checkBoxScale)
        
        self.checkBoxColor=QAction(QtGui.QIcon(self.icon+"colors-icon.png"),'Color on',self)
        self.checkBoxColor.triggered.connect(self.Color)
        self.checkBoxColor.setCheckable(True) 
        self.checkBoxColor.setChecked(True)
        self.toolBar.addAction(self.checkBoxColor)
        self.ImageMenu.addAction(self.checkBoxColor)
        
    
        self.checkBoxHist=QAction(QtGui.QIcon(self.icon+"colourBar.png"),'Show colour Bar',self)
        self.checkBoxHist.setCheckable(True)
        self.checkBoxHist.setChecked(False)
        self.checkBoxHist.triggered.connect(self.HIST)
        self.ImageMenu.addAction(self.checkBoxHist)
        
        self.ColorBox=QAction('&LookUp Table',self)
        menuColor=QMenu()
        menuColor.addAction('thermal',self.Setcolor)
        menuColor.addAction('flame',self.Setcolor)
        menuColor.addAction('yellowy',self.Setcolor)
        menuColor.addAction('bipolar',self.Setcolor)
        menuColor.addAction('spectrum',self.Setcolor)
        menuColor.addAction('cyclic',self.Setcolor)
        menuColor.addAction('viridis',self.Setcolor) 
        menuColor.addAction('inferno',self.Setcolor)
        menuColor.addAction('plasma',self.Setcolor)      
        menuColor.addAction('magna',self.Setcolor)            
        
        self.ColorBox.setMenu(menuColor)
        self.ImageMenu.addAction(self.ColorBox)
        
        
        self.checkBoxBg=QAction('Background Substraction On',self)
        self.checkBoxBg.setCheckable(True)
        self.checkBoxBg.setChecked(False)
        self.ImageMenu.addAction(self.checkBoxBg)
        
        
        
        if self.encercled=="on":
            self.energyBox=QAction(QtGui.QIcon(self.icon+"coin.png"),'Energy Encercled',self)
            self.energyBox.setShortcut('Ctrl+e')
            self.AnalyseMenu.addAction(self.energyBox)
            self.energyBox.triggered.connect(self.Energ)
        
            
        if self.math=="on":
            self.mathButton=QAction(QtGui.QIcon(self.icon+"math.png"),'Math',self)
            self.mathButton.triggered.connect(lambda:self.open_widget(self.winMath))
            self.ProcessMenu.addAction(self.mathButton)
            self.winMath.emitApply.connect(self.newDataReceived)
        
        if self.winFilter=='on':
            self.filtreBox=QAction('&Filters',self)
            menu=QMenu()
            menu.addAction('&Gaussian',self.Gauss)
            menu.addAction('&Median',self.Median)
            menu.addAction('&Origin',self.Orig)
            self.filtreBox.setMenu(menu)
            self.ProcessMenu.addAction(self.filtreBox)
        
        if self.plot3D=="on":
            self.box3d=QPushButton('3D', self)
            self.toolBar.addWidget(self.box3d)
        
        if self.meas=='on':
            self.MeasButton=QAction(QtGui.QIcon(self.icon+"laptop.png"),'Measure',self)
            self.MeasButton.setShortcut('ctrl+m')
            self.MeasButton.triggered.connect(self.Measurement)
            self.AnalyseMenu.addAction(self.MeasButton)
            
        if self.fft=='on':
            self.fftButton=QAction('FFT')
            self.AnalyseMenu.addAction(self.fftButton)
            self.fftButton.triggered.connect(self.fftTransform)
            
            
        self.ZoomRectButton=QAction(QtGui.QIcon(self.icon+"loupe.png"),'Zoom',self)
        self.ZoomRectButton.triggered.connect(self.zoomRectAct)
        self.toolBar.addAction(self.ZoomRectButton)
        
        
        self.ligneButton=QAction(QtGui.QIcon(self.icon+"line.png"),'add  Line',self)
        self.toolBar.addAction(self.ligneButton)
        
        self.rectangleButton=QAction(QtGui.QIcon(self.icon+"rectangle.png"),'Add Rectangle',self)
        self.toolBar.addAction(self.rectangleButton)
        
        self.circleButton=QAction(QtGui.QIcon(self.icon+"Red_circle.png"),'add  Cercle',self)
        self.toolBar.addAction(self.circleButton)
        
        self.PlotButton=QAction(QtGui.QIcon(self.icon+"analytics.png"),'Plot Profile',self)
        self.PlotButton.triggered.connect(self.CUT)
        self.PlotButton.setShortcut("ctrl+k")
        self.AnalyseMenu.addAction(self.PlotButton)
        
        self.flipButton=QAction(QtGui.QIcon(self.icon+"fliphorizontal.png"),'Flip Horizontally',self)
        self.flipButton.setCheckable(True)
        self.flipButton.setChecked(False)
        self.flipButton.triggered.connect(self.flipAct)
        self.ImageMenu.addAction(self.flipButton)
        
        
        self.flipButtonVert=QAction(QtGui.QIcon(self.icon+"flipvertical.png"),'Flip Horizontally',self)
        self.flipButtonVert.setCheckable(True)
        self.flipButtonVert.setChecked(False)
        self.ImageMenu.addAction(self.flipButtonVert)
        self.flipButtonVert.triggered.connect(self.flipVertAct)
        
        
        self.vbox2=QVBoxLayout()
        
        self.winImage = pg.GraphicsLayoutWidget()
        self.winImage.setContentsMargins(0,0,0,0)
       # self.winImage.setAspectLocked(True)
        self.winImage.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.winImage.ci.setContentsMargins(10,0,15,15)
        self.vbox2.addWidget(self.winImage)
        self.vbox2.setContentsMargins(0,0,0,0)
        
        self.p1=self.winImage.addPlot()#col=0,row=0)#,rowspan=2, colspan=2)
        self.imh=pg.ImageItem()
        self.axeX=self.p1.getAxis('bottom')
        self.axeY=self.p1.getAxis('left')
        self.p1.addItem(self.imh)
        self.p1.setMouseEnabled(x=False,y=False)
        #self.p1.setContentsMargins(0,0,0,0)
   
        #self.p1.setAspectLocked(True,ratio=1)
        self.p1.showAxis('right',show=False)
        self.p1.showAxis('top',show=False)
        self.p1.showAxis('left',show=False)
        self.p1.showAxis('bottom',show=False)
        
        if self.bloqKeyboard==True:
            self.vLine = pg.InfiniteLine(angle=90, movable=False,pen='r')
            self.hLine = pg.InfiniteLine(angle=0, movable=False,pen='r')
        else:
            self.vLine = pg.InfiniteLine(angle=90, movable=False,pen='y')
            self.hLine = pg.InfiniteLine(angle=0, movable=False,pen='y')

        self.xc=int(self.conf.value(self.name+"/xc"))
        self.yc=int(self.conf.value(self.name+"/yc"))
        self.rx=int(self.conf.value(self.name+"/rx"))
        self.ry=int(self.conf.value(self.name+"/ry"))
        self.vLine.setPos(self.xc)
        self.hLine.setPos(self.yc)
       
        
        self.ro1=pg.EllipseROI([self.xc,self.yc],[self.rx,self.ry],pen='y',movable=False,maxBounds=QtCore.QRectF(0,0,self.rx,self.ry))
        self.ro1.setPos([self.xc-(self.rx/2),self.yc-(self.ry/2)])
      
       
        # text for fwhm on p1
        self.textX = pg.TextItem(angle=-90) 
        self.textY = pg.TextItem()
        
        #histogram
        self.hist = pg.HistogramLUTItem() 
        self.hist.setImageItem(self.imh)
        self.hist.autoHistogramRange()
        self.hist.gradient.loadPreset('flame')
        
        ##  XY  graph
        self.curve2=pg.PlotCurveItem()
        self.curve3=pg.PlotCurveItem()
        
        ## slider to open multi file
        self.sliderImage=QSlider(Qt.Horizontal)
        self.sliderImage.setEnabled(False)
        
        
        
        # self.axisRange=QAction('Set Axis Range',self)
        # self.axisMenu.addAction(self.axisRange)
        # self.axisRange.triggered.connect(self.showRange)
        
        self.logActionX=QAction('Image Log ',self)
        self.ImageMenu.addAction(self.logActionX)
        self.logActionX.setCheckable(True)
        self.logActionX.triggered.connect(self.logMode)
        
        
        ## main layout
        
        # vMainLayout=QVBoxLayout()
        
        hMainLayout=QHBoxLayout()
        # vMainLayout.addLayout(self.hboxBar)
        #vMainLayout.addLayout(hMainLayout)
       
        self.p1.setYRange(0,self.dimy)
        self.p1.setXRange(0,self.dimx)
        self.winPLOTY = self.winImage.addPlot(col=1,row=0)#, colspan=1)
        self.winPLOTY.setMaximumWidth(120)
        self.winPLOTY.showAxis('right',show=True)
        self.winPLOTY.showAxis('left',show=False)
        self.winPLOTY.getViewBox().invertY(False)
        self.winPLOTY.setLabel('right','Wavlenght (nm) ')
        #self.winPLOTY.setContentsMargins(0,15,0,0)
        
        self.winPLOTX = self.winImage.addPlot(col=0,row=1)
        self.winPLOTX.setMaximumHeight(120)
        self.winPLOTX.showAxis('bottom',show=False)
        self.winPLOTX.showAxis('left',show=False)
        self.winPLOTX.showAxis('right',show=True)
        self.winPLOTX.setLabel('top','Time (fs) ')
        #self.winPLOTX.setContentsMargins(0,0,20,0) #left top right bottom
        penFit=pg.mkPen(color='r',width=2)
        self.pFit=self.winPLOTX.plot(pen=penFit)
        
        #self.vbox2.addWidget(self.sliderImage)
        
        hMainLayout.addLayout(self.vbox1)
        hMainLayout.addLayout(self.vbox2)
        
        self.hboxLabelfwhm=QVBoxLayout()
        self.hboxLabelfwhm.setAlignment(Qt.AlignCenter)
        self.fwhmLabelFit=QLabel('FWHM (fit):')
        self.fwhmLabelFit.setStyleSheet("font: bold 12pt;color:red")
        self.fwhmLabelFitValue=QLabel('...')
        self.fwhmLabelFitValue.setStyleSheet("font: bold 12pt;color:red")
        self.hboxLabelfwhm.addWidget(self.fwhmLabelFit)
        self.hboxLabelfwhm.addWidget(self.fwhmLabelFitValue)
        
        self.fwhmLabel=QLabel('FWHM :')
        self.fwhmLabel.setStyleSheet("font: bold 12pt;color:yellow")
        self.fwhmLabelValue=QLabel('...')
        self.fwhmLabelValue.setStyleSheet("font: bold 12pt;color:yellow")
        
        self.hboxLabelfwhm.addWidget(self.fwhmLabel)
        self.hboxLabelfwhm.addWidget(self.fwhmLabelValue)
        
        
        
        
        self.widgetRange=WINDOWRANGE()
        self.widgetRange.labelXmin.setText("Time (fs) Min ")
        self.widgetRange.labelXmax.setText("Time (fs) Min ")
        self.widgetRange.labelYmin.setText("Wavelenght(nm) Min ")
        self.widgetRange.labelYmax.setText("Wavelenght(nm) Maxn ")
        
        self.vbox3=QVBoxLayout()
        hboxRange=QHBoxLayout()
        hboxRange.setAlignment(Qt.AlignCenter)
        labelRange=QLabel('Range')
        labelRange.setStyleSheet("font: bold 12pt;color:yellow")
        hboxRange.addWidget(labelRange)
        self.vbox3.addLayout(hboxRange)
        self.vbox3.addStretch(0)
        self.vbox3.addWidget(self.widgetRange)
        self.vbox3.setContentsMargins(0,0,0,0)
        
        self.vbox3.addStretch(1)
        self.vbox3.addLayout(self.hboxLabelfwhm)
        hMainLayout.addLayout(self.vbox3)
        hMainLayout.setContentsMargins(1,1,1,1)
        #hMainLayout.setSpacing(1)
        hMainLayout.setStretch(0,5)
        MainWidget=QWidget()
        
        MainWidget.setLayout(hMainLayout)
        
        self.setCentralWidget(MainWidget)
        #self.setContentsMargins(1,1,1,1)
        #self.plotLine=pg.LineSegmentROI(positions=((self.dimx/2-100,self.dimy/2),(self.dimx/2+100,self.dimy/2)), movable=True,angle=0,pen='b')
        self.plotLine=pg.LineSegmentROI(positions=((0,200),(200,200)), movable=True,angle=0,pen='w')
        #self.plotLine=pg.PolyLineROI(positions=((0,200),(200,200),(300,200)), movable=True,angle=0,pen='w')
        self.plotRect=pg.RectROI([self.xc,self.yc],[1*self.rx,self.ry],pen='g')
        self.plotCercle=pg.CircleROI([self.xc,self.yc],[10,10],pen='g')
        self.plotRectZoom=pg.RectROI([self.xc,self.yc],[1*self.rx,self.ry],pen='w')
        
        self.ROICross=pg.RectROI([0,2],[10,10],pen='r')
        #self.plotRect.addScaleRotateHandle([0.5, 1], [0.5, 0.5])
        #self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5()) # dark style
        
        
        # self.newDataReceived(self.data)
        
    def actionButton(self):
        # action of button
        
        self.widgetRange.applyButton.clicked.connect(self.setRangeOn)
        self.widgetRange.ResetButton.clicked.connect(self.setRangeReset)
        
        
        self.ro1.sigRegionChangeFinished.connect(self.roiChanged)
        
        self.plotRectZoom.sigRegionChanged.connect(self.roiChangedZoom)
        
        self.ROICross.sigRegionChangeFinished.connect(self.PlotXYRect)
        
        self.ligneButton.triggered.connect(self.LIGNE)
        self.rectangleButton.triggered.connect(self.Rectangle)
        self.circleButton.triggered.connect(self.CERCLE)
        
        self.plotLine.sigRegionChangeFinished.connect(self.LigneChanged)
        self.plotRect.sigRegionChangeFinished.connect(self.RectChanged)
        self.plotCercle.sigRegionChangeFinished.connect(self.CercChanged)
        
        if self.plot3D=="on":
            self.box3d.clicked.connect(self.Graph3D)
            
        self.winPref.closeEventVar.connect(self.ScaleImg)
        
        
        self.sliderImage.valueChanged.connect(self.SliderImgFct)
        # self.dockImage.topLevelChanged.connect(self.fullScreen)
       
        
        
    def fullScreen(self):
        if  self.fullscreen==False:
            self.fullscreen=True
            self.dockImage.showMaximized()
        else :
            self.fullscreen=False
            self.dockImage.showNormal()
        
    def shortcut(self):
        # keyboard shortcut
        
        self.shortcutPu=QShortcut(QtGui.QKeySequence("+"),self)
        self.shortcutPu.activated.connect(self.paletteup)
        self.shortcutPu.setContext(Qt.ShortcutContext(3))
        #3: The shortcut is active when its parent widget, or any of its children has focus. default O The shortcut is active when its parent widget has focus.
        self.shortcutPd=QtGui.QShortcut(QtGui.QKeySequence("-"),self)
        self.shortcutPd.activated.connect(self.palettedown)
        self.shortcutPd.setContext(Qt.ShortcutContext(3))
        
        # self.shortcutOpen=QtGui.QShortcut(QtGui.QKeySequence("Ctrl+o"),self)
        # self.shortcutOpen.activated.connect(self.OpenF)
        # self.shortcutOpen.setContext(Qt.ShortcutContext(3))
        
        # self.shortcutSave=QtGui.QShortcut(QtGui.QKeySequence("Ctrl+s"),self)
        # self.shortcutSave.activated.connect(self.SaveF)
        # self.shortcutSave.setContext(Qt.ShortcutContext(3))
        
        # self.shortcutMeas=QtGui.QShortcut(QtGui.QKeySequence('Ctrl+m'),self)
        # self.shortcutMeas.activated.connect(self.Measurement)
        # self.shortcutMeas.setContext(Qt.ShortcutContext(3))
        
        # self.shortcutCut=QtGui.QShortcut(QtGui.QKeySequence('Ctrl+k'),self)
        # self.shortcutCut.activated.connect(self.CUT)
        # self.shortcutCut.setContext(Qt.ShortcutContext(3))
        
        self.shortcutBloq=QtGui.QShortcut(QtGui.QKeySequence("Ctrl+b"),self)
        self.shortcutBloq.activated.connect(self.bloquer)
        self.shortcutBloq.setContext(Qt.ShortcutContext(3))
        
        self.shortcutDebloq=QtGui.QShortcut(QtGui.QKeySequence("Ctrl+d"),self)
        self.shortcutDebloq.activated.connect(self.debloquer)
        self.shortcutDebloq.setContext(Qt.ShortcutContext(3))
        
        
        
        # mousse action:
        self.proxy=pg.SignalProxy(self.p1.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.p1.scene().sigMouseClicked.connect(self.mouseClick)
        self.vb=self.p1.vb
        
        
    def Energ(self):
        # open windget for calculated encercled energy and plot it vs shoot number
        self.open_widget(self.winEncercled)
        self.winEncercled.Display(self.data)
        
    def LIGNE(self) : 
        #plot a line
        try :
            self.p1.removeItem(self.plotRect)
            self.p1.removeItem(self.plotCercle)
        except:pass
    
        if self.ite=='line':
            self.p1.removeItem(self.plotLine)
            self.ite=None
        else: 
            self.ite='line'
            self.p1.addItem(self.plotLine)
            self.LigneChanged()
        
      
    def LigneChanged(self):
        # take ROI 
        self.cut=self.plotLine.getArrayRegion(self.data,self.imh)
        
        if self.winPref.checkBoxAxeScale.isChecked()==1:
            self.linePoints=self.plotLine.listPoints()
            self.lineXo=self.linePoints[0][0]
            self.lineYo=self.linePoints[0][1]
            self.lineXf=self.linePoints[1][0]
            self.lineYf=self.linePoints[1][1]
            #self.plotLineAngle=np.arctan((self.lineYf-self.lineYo)/(self.lineXf-self.lineXo))
            # print('angle',self.plotLineAngle*360/(2*3.14),self.cut.size)
            
            step=(self.winPref.stepX**2*(self.lineXo-self.lineXf)**2+self.winPref.stepY**2*(self.lineYo-self.lineYf)**2)
            step=step**0.5/self.cut.size
            self.absiLine=np.arange(0,(self.cut.size)*step,step)
            
            #print(self.absiLine)
        
    def Rectangle(self)  :
        
        try :
            self.p1.removeItem(self.plotLine)
            self.p1.removeItem(self.plotCercle)
        except:pass
        
        if self.ite=='rect':
            self.p1.removeItem(self.plotRect)
            self.ite=None
        else :
            self.p1.addItem(self.plotRect)
            self.plotRect.setPos([self.dimx/2,self.dimy/2])
            self.ite='rect'
            self.RectChanged()
        
    def RectChanged(self):
        # take ROI
        self.cut=(self.plotRect.getArrayRegion(self.data,self.imh))
        self.cut1=self.cut.mean(axis=1)
        
        
    def CERCLE(self) : 
        try :
            self.p1.removeItem(self.plotRect)
            self.p1.removeItem(self.plotLine)
        except:pass
        #self.p1.clear()
        if self.ite=='cercle':
            self.p1.removeItem(self.plotCercle)
            self.ite=None
        else:
            self.p1.addItem(self.plotCercle) 
            self.plotCercle.setPos([self.dimx/2,self.dimy/2])
            self.ite='cercle'
        
    def CercChanged(self):
        # take ROI
        self.cut=(self.plotCercle.getArrayRegion(self.data,self.imh))
        self.cut1=self.cut.mean(axis=1)
    
    def CUT(self): 
        # plot on a separated widget the ROI plot profile
        if self.ite=='line':
            self.open_widget(self.winCoupe)
            if self.winPref.checkBoxAxeScale.isChecked()==1:
                self.winCoupe.PLOT(self.cut,axis=self.absiLine)
            else:
                self.winCoupe.PLOT(self.cut)
            
        if self.ite=='rect':
            self.open_widget(self.winCoupe)
            self.winCoupe.PLOT(self.cut1)
   
    def Graph3D (self):
        
        self.open_widget(self.Widget3D)
        self.Widget3D.Plot3D(self.data)
        
        
    def Measurement(self) :
        # show widget for measurement on all image or ROI  (max, min mean ...)
        if self.ite=='rect':
            self.RectChanged()
            if self.meas=="on":
                self.winM.setFile(self.nomFichier)
                self.open_widget(self.winM)
                self.winM.Display(self.cut)
            
        if self.ite=='cercle':
            self.CercChanged()
            if self.meas=="on":
                self.winM.setFile(self.nomFichier)
                self.open_widget(self.winM)
                self.winM.Display(self.cut)
        
        # if self.ite=='line':
        #     self.LigneChanged()
        #     self.winM.setFile(self.nomFichier)
        #     self.open_widget(self.winM)
        #     self.winM.Display(self.cut)
        
        if self.ite==None:
            if self.meas=="on":
                self.winM.setFile(self.nomFichier)
                self.open_widget(self.winM)
                self.winM.Display(self.data)
    

    def fftTransform(self):
        # show on a new widget fft 
        if self.ite=='rect':
            self.RectChanged()
            self.open_widget(self.winFFT)
            self.winFFT.Display(self.cut)   
        if self.ite=='cercle':
            self.CercChanged()
            self.open_widget(self.winFFT)
            self.winFFT.Display(self.cut)
        if self.ite=='line':
            self.LigneChanged()
            self.open_widget(self.winFFT1D)
            if self.cut.ndim==1:
                datafft=np.fft.fft(np.array(self.cut))
                self.norm=abs(np.fft.fftshift(datafft))
                self.norm=np.log10(1+self.norm)
                self.winFFT1D.PLOT(self.norm)
            
        if self.ite==None:
            self.open_widget(self.winFFT)
            self.winFFT.Display(self.data) 
        

        
        
    def Display(self,data):
        #  display the data and refresh all the calculated things and plots
        self.data=data
        self.zoomRectupdate() # update rect
        
        if self.checkBoxBg.isChecked()==True and self.winOpt.dataBgExist==True:
            try :
                self.data=self.data-self.winOpt.dataBg
            except :
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Background not soustracred !")
                msg.setInformativeText("Background file error  ")
                msg.setWindowTitle("Warning ...")
                msg.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
                msg.exec_()
                
        if self.checkBoxBg.isChecked()==True and self.winOpt.dataBgExist==False:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Background not soustracred !")
                msg.setInformativeText("Background file not selected in options menu ")
                msg.setWindowTitle("Warning ...")
                msg.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
                msg.exec_()
            
        
        #### filtre
        if self.filter=='gauss':
            self.data=gaussian_filter(self.data,self.sigma)
            print('gauss filter')
            
        if self.filter=='median':
            self.data=median_filter(self.data,size=self.sigma)
            print('median filter')
        
        
        
        
        # self.p1.setAspectLocked(True,ratio=1)
        
        ### color  and sacle 
        if self.checkBoxScale.isChecked()==1: # color autoscale on
            
            if self.winPref.checkBoxAxeScale.isChecked()==1:
                self.axeX.setScale(self.winPref.stepX)
                self.axeY.setScale(self.winPref.stepY)
                self.axeX.setLabel('um')
                self.axeY.setLabel('um')
                self.axeX.showLabel(True)
            if self.winPref.checkBoxAxeScale.isChecked()==0:
                self.scaleAxis="off"
                self.axeX.setScale(1)
                self.axeY.setScale(1)  
                self.axeX.showLabel(False)
            self.imh.setImage(self.data,autoLevels=True,autoDownsample=True) #.astype(float)
        else :
            self.imh.setImage(self.data,autoLevels=False,autoDownsample=True)
        
        self.PlotXY() # graph update
        
        ##update        
        if self.encercled=="on":
            if self.winEncercled.isWinOpen==True:
                self.winEncercled.Display(self.data) ## energy update
        
        if self.winCoupe.isWinOpen==True:
            if self.ite=='line':
                self.LigneChanged()
                self.CUT()
            if self.ite=='rect':
                self.RectChanged()
                self.CUT()
            if self.ite=='cercle':
                self.CercChanged()
        if self.meas=="on":       
            if self.winM.isWinOpen==True: #  measurement update
                if self.ite=='rect':
                    self.RectChanged()
                    self.Measurement()
                elif self.ite=='cercle':
                    self.CercChanged()
                    self.Measurement()
                else :
                    self.Measurement()
        if self.fft=='on':        
            if self.winFFT.isWinOpen==True: # fft update
                self.winFFT.Display(self.data)
        if self.plot3D=="on":
            if self.Widget3D.isWinOpen==True:
                self.Graph3D()
        ### autosave
        if self.checkBoxAutoSave.isChecked()==True: ## autosave data
            self.pathAutoSave=str(self.conf.value(self.name+'/pathAutoSave'))
            self.fileNameSave=str(self.conf.value(self.name+'/nameFile'))
            date=time.strftime("%Y_%m_%d_%H_%M_%S")
            self.numTir=int(self.conf.value(self.name+'/tirNumber'))
            if self.numTir<10:
                num="00"+str(self.numTir)
            elif 9<self.numTir<100:
                num="0"+str(self.numTir)
            else:
                num=str(self.numTir)
            if self.winOpt.checkBoxDate.isChecked()==True: # add the date
                nomFichier=str(str(self.pathAutoSave)+'/'+self.fileNameSave+'_'+num+'_'+date)
            else :
                nomFichier=str(str(self.pathAutoSave)+'/'+self.fileNameSave+'_'+num)

            print( nomFichier, 'saved')
            if self.winOpt.checkBoxTiff.isChecked()==True: #save as tiff 
                self.dataS=self.dataS=np.rot90(self.data,1)
                img_PIL = Image.fromarray(self.dataS)
                img_PIL.save(str(nomFichier)+'.TIFF',format='TIFF') 
            else :
                
                np.savetxt(str(nomFichier)+'.txt',self.data)

            self.numTir+=1
            self.winOpt.setTirNumber(self.numTir)
            self.conf.setValue(self.name+"/tirNumber",self.numTir)
            self.fileName.setText(nomFichier)
    
        
       
        
    def mouseClick(self): # block the cross if mousse button clicked
        
        if self.bloqq==1:
            self.bloqq=0
            
        else :
            self.bloqq=1
            self.conf.setValue(self.name+"/xc",int(self.xc)) # save cross postion in ini file
            self.conf.setValue(self.name+"/yc",int(self.yc))
            
            
    def mouseMoved(self,evt):

        ## the cross mouve with the mousse mvt
        if self.bloqKeyboard==False :  #mouse not  blocked by  keyboard
            if self.bloqq==0: # mouse not  blocked by mouse  click
                
                pos = evt[0]  ## using signal proxy turns original arguments into a tuple
                if self.p1.sceneBoundingRect().contains(pos):
                    
                    mousePoint = self.vb.mapSceneToView(pos)
                    self.xMouse = (mousePoint.x())
                    self.yMouse= (mousePoint.y())
                    if ((self.xMouse>0 and self.xMouse<self.dimx) and (self.yMouse>0 and self.yMouse<self.dimy) ):
                            self.xc = self.xMouse
                            self.yc= self.yMouse  
                            self.vLine.setPos(self.xc)
                            self.hLine.setPos(self.yc) # the cross move only in the graph    
                            #self.ro1.setPos([self.xc-(self.rx/2),self.yc-(self.ry/2)])
                            self.PlotXY()
                
    def fwhm(self,x, y, order=3):
        """
            Determine full-with-half-maximum of a peaked set of points, x and y.
    
        """
        
        y=gaussian_filter(y,5) # filtre for reducing noise
        
        half_max = np.amax(y)/2.0
        
        s = splrep(x, y - half_max,k=order) # F
        
        roots = sproot(s) # Given the knots .
        
        if len(roots) > 2:
            pass
           
        elif len(roots) < 2:
            pass
        else:
            #print(np.around(abs(roots[1] - roots[0]),decimals=2))
            return np.around(abs(roots[1] - roots[0]),decimals=2),half_max
    
        
    
    
    def CoupeRect(self):
        
        if self.checkBoxPlotRect.isChecked()==1:

            self.dataRect=(self.ROICross.getArrayRegion(self.data,self.imh))
            self.dataRect=self.dataRect.mean(axis=1)
            
            if self.axisXPixel==True:
                
                self.xRect=np.arange(self.ROICross.pos()[0],self.ROICross.pos()[0]+self.ROICross.size()[0],1)#
            else:
                # print('position croix',self.ROICross.pos(),self.ROICross.size())
                
                
                self.xRect=self.axisX[int(round(self.ROICross.pos()[0])):int(round(self.ROICross.pos()[0])+self.ROICross.size()[0])+1]
                # print('lens',np.shape(self.xRect),np.shape(self.dataRect))
                
                if np.shape(self.xRect)>np.shape(self.dataRect):
                    self.xRect=self.xRect[0,np.shape(self.dataRect)]
                    print('sup')
                if np.shape(self.xRect)<np.shape(self.dataRect):
                    self.dataRect=self.dataRect[0,np.shape(self.xRect)]
                    print('inf')
            
            self.curve3.setData(self.xRect,self.dataRect,clear=True)
            
            self.setFit(data=self.dataRect,xMat=self.xRect)
            
            try:
                self.fwhmY=self.fwhm(self.xRect, self.dataRect, order=3)[0]
                self.fwhmLabelValue.setText(str(self.fwhmY))
            except:
                self.fwhmLabelValue.setText('.....')
            
            
    def Coupe(self):
        
        # make  plot profile on cross
        
        if self.checkBoxPlot.isChecked()==True:
            
            if self.maxGraphBox.isChecked()==True  and self.bloqKeyboard==False  : # find and fix the cross on the maximum of the image
                
                dataF=gaussian_filter(self.data,5)
                (self.xc,self.yc)=pylab.unravel_index(dataF.argmax(),self.data.shape) #take the max ndimage.measurements.center_of_mass(dataF)#
                self.vLine.setPos(self.xc)
                self.hLine.setPos(self.yc)
            
            try:    
                dataCross=self.data[int(self.xc),int(self.yc)] 
            except:
                dataCross=0
            
            try:
                coupeX=self.data[int(self.xc),:]
            except :
                coupeX=np.arange(0,int(self.xc+1),1) # to avoid error if cross out of picture
            self.coupeX=coupeX
            try: 
                coupeY=self.data[:,int(self.yc)]
            except:
                coupeY=np.arange(0,int(self.yc+1),1)
            self.coupeY=coupeY
            xxx=np.arange(0,int(self.dimx),1)#
            if self.axisX is None:
                self.axisX=xxx
            yyy=np.arange(0,int(self.dimy),1)#
            if self.axisY is None:
                self.axisY=yyy
            coupeXMax=np.max(coupeX)
            coupeYMax=np.max(coupeY)
            
            
            if coupeXMax==0: # avoid zero
                coupeXMax=1
            
            if coupeYMax==0:
                coupeYMax=1
                
            if self.winPref.checkBoxAxeScale.isChecked()==1: # scale axe on 
                self.label_Cross.setText('x='+ str(round(int(self.xc)*self.winPref.stepX,2)) + '  um'+' y=' + str(round(int(self.yc)*self.winPref.stepY,2)) +' um')
            else : 
                try:
                    self.label_Cross.setText('x='+ str(round(self.axisX[int(self.xc)],2)) + ' fs  '+ ' y=' + str(self.axisY[int(self.yc)]) +' nm' )
                except:
                    self.label_Cross.setText('x=')
            dataCross=round(dataCross,3) # take data  value  on the cross
            self.label_CrossValue.setText(' v.=' + str(dataCross))
            
            
            # coupeXnorm=(self.data.shape[0]/10)*(coupeX/coupeXMax) # normalize the curves
            
            
            self.curve2.setData(x=coupeX,y=self.axisY,clear=True)#(20+self.xminR+coupeXnorm,yyy,clear=True)
            self.winPLOTY.setYRange(min(self.axisY),max(self.axisY))
            self.winPLOTY.setXRange(min(coupeX),max(coupeX))
            # coupeYnorm=(self.data.shape[1]/10)*(coupeY/coupeYMax)
            
            
            
            self.curve3.setData(x=self.axisX,y=coupeY,clear=True)#20+self.yminR+coupeYnorm,clear=True)
            # self.winPLOTX.setXRange(min(self.axisX),max(self.axisX))
            self.winPLOTX.setXRange(self.xMin,self.xMax)
        
            self.winPLOTX.setYRange(min(coupeY),max(coupeY))
                                    
            ###  fwhm on the  X et Y curves if max  >20 counts if checked in winOpt
            
            
            # if self.winOpt.checkBoxFwhm.isChecked()==1: # show fwhm values on graph
            #     xCXmax=np.amax(coupeXnorm) # max
            #     if xCXmax>20:
            #         try :
            #             fwhmX=self.fwhm(yyy, coupeXnorm, order=3)[0]
                        
            #         except : fwhmX=None
            #         if fwhmX==None:
            #             self.textX.setText('')
            #         else:
            #             if self.winOpt.checkBoxAxeScale.isChecked()==1:
            #                 self.textX.setText('fwhm='+str(round(fwhmX*self.winOpt.stepX,2))+' um',color='w')
            #             else :
                            
            #                self.textX.setText('fwhm='+str(round(fwhmX,2)),color='w')
            #         yCXmax=yyy[coupeXnorm.argmax()]
                    
            #         self.textX.setPos(xCXmax+70,yCXmax+60)
                
            #     yCYmax=np.amax(coupeYnorm) # max
                
            #     if yCYmax>20:
            #         try:
            #             fwhmY=self.fwhm(xxx, coupeYnorm, order=3)[0]
            #         except :fwhmY=None
            #         xCYmax=xxx[coupeYnorm.argmax()]
            #         if fwhmY==None:
            #             self.textY.setText('',color='w')
            #         else:
            #             if self.winOpt.checkBoxAxeScale.isChecked()==1:
            #                 self.textY.setText('fwhm='+str(round(fwhmY*self.winOpt.stepY,2))+' um',color='w')
            #             else:
            #                 self.textY.setText('fwhm='+str(round(fwhmY,2)),color='w')
                            
            #         self.textY.setPos(xCYmax-60,yCYmax+70)   
                    
            try:
                self.fwhmY=self.fwhm(self.axisX, coupeY, order=3)[0]
                self.fwhmLabelValue.setText(str(self.fwhmY))
            except:
                self.fwhmLabelValue.setText('.....')
        
        try :self.setFit(data=self.coupeY,xMat=self.axisX)
        except: pass
    
    
    def PlotXYRect(self):
        self.checkBoxPlot.setChecked(False)
        self.PlotXY()
        
        if self.checkBoxPlotRect.isChecked()==1:
            self.p1.addItem(self.ROICross)
            self.winPLOTX.addItem(self.curve3)
            self.winPLOTX.addItem(self.pFit)
            self.CoupeRect()
            
            
        else :
            self.p1.removeItem(self.ROICross)
            self.winPLOTX.removeItem(self.pFit)
            
            
            
    def PlotXY(self): # plot curves on the  graph
        
        if self.checkBoxPlot.isChecked()==1:
            
            self.p1.addItem(self.vLine, ignoreBounds=False)
            self.p1.addItem(self.hLine, ignoreBounds=False)
            self.winPLOTY.addItem(self.curve2)
            self.winPLOTX.addItem(self.curve3)
            self.winPLOTX.addItem(self.pFit)
            self.winPLOTX.addItem(self.textX)
            self.winPLOTY.addItem(self.textY)
            self.p1.removeItem(self.ROICross)
            self.checkBoxPlotRect.setChecked(False)
            
            self.winPLOTX.setXRange(self.xMin,self.xMax)
            self.winPLOTY.setYRange(self.yMin,self.yMax)
            
            self.Coupe()
        else:
            self.p1.removeItem(self.vLine)
            self.p1.removeItem(self.hLine)
            self.winPLOTY.removeItem(self.curve2)
            self.winPLOTX.removeItem(self.curve3)
            self.winPLOTX.removeItem(self.pFit)
            self.winPLOTX.removeItem(self.textX)
            self.winPLOTX.removeItem(self.textY)
            
            
            
    def paletteup(self):
        # change the color scale
        levels=self.imh.getLevels()
        if levels[0]==None:
            xmax =self.data.max()
            xmin=self.data.min()
        else :
            xmax=levels[1]
            xmin=levels[0]
            
        self.imh.setLevels([xmin, xmax-(xmax- xmin) / 10])
        #hist.setImageItem(imh,clear=True)
        self.hist.setHistogramRange(xmin,xmax)

    def palettedown(self):
        
        levels=self.imh.getLevels()
        if levels[0]==None:
            xmax=self.data.max()
            xmin=self.data.min()
        else :
            xmax=levels[1]
            xmin=levels[0]
            
        self.imh.setLevels([xmin, xmax+ (xmax- xmin) / 10])
        #hist.setImageItem(imh,clear=True)
        self.hist.setHistogramRange(xmin,xmax)
    
    def Setcolor(self):
        action = self.sender()
        self.colorBar=str(action.text())
        
        self.hist.gradient.loadPreset(self.colorBar)
    
    def Color(self):
        """ image in colour/n&b
        """
        
        
        if self.checkBoxColor.isChecked()==1:
            self.hist.gradient.loadPreset(self.colorBar)
        else:
            self.hist.gradient.loadPreset('grey')
            
            
    def roiChanged(self):
        
        self.rx=self.ro1.size()[0]
        self.ry=self.ro1.size()[1]
        self.conf.setValue(self.name+"/rx",int(self.rx))
        self.conf.setValue(self.name+"/ry",int(self.ry))
        
    def roiChangedZoom (self):
        
        
        self.xZoomMin=(self.plotRectZoom.pos()[0])
        self.yZoomMin=(self.plotRectZoom.pos()[1])
        self.xZoomMax=(self.plotRectZoom.pos()[0])+self.plotRectZoom.size()[0]
        self.yZoomMax=(self.plotRectZoom.pos()[1])+self.plotRectZoom.size()[1]
       
        self.xMin=self.axisX[int(self.xZoomMin)]
        self.xMax=self.axisX[int(self.xZoomMax)]
        self.yMin=self.axisY[int(self.yZoomMin)]
        self.yMax=self.axisY[int(self.yZoomMax)]
        
        self.widgetRange.xMinBox.setValue(self.xMin)
        self.widgetRange.yMinBox.setValue(self.yMin)
        self.widgetRange.xMaxBox.setValue(self.xMax)
        self.widgetRange.yMaxBox.setValue(self.yMax)
        
    def bloquer(self): # block the cross
        
        self.bloqKeyboard=bool(True)
        self.conf.setValue(self.name+"/xc",int(self.xc))# save cross postion in ini file
        self.conf.setValue(self.name+"/yc",int(self.yc))
        self.conf.setValue(self.name+"/bloqKeyboard",bool(self.bloqKeyboard))
        self.vLine.setPen('r')
        self.hLine.setPen('r')
        
    def debloquer(self): # unblock the cross
        self.bloqKeyboard=bool(False)
        self.vLine.setPen('y')
        self.hLine.setPen('y')
        self.conf.setValue(self.name+"/bloqKeyboard",bool(self.bloqKeyboard))
        
        
        
    def HIST(self):
        #show histogramm
        if self.checkBoxHist.isChecked()==1:
            self.winImage.addItem(self.hist)
        else:
            self.winImage.removeItem(self.hist)
    
    
    def Gauss(self):
        # gauss filter
        self.filter='gauss'
        sigma, ok=QInputDialog.getInt(self,'Gaussian Filter ','Enter sigma value (radius)')
        if ok:
            self.sigma=sigma
            self.filtreBox.setText('F: Gaussian')
            self.Display(self.data)
        
        
    def Median(self):
        #median  filter
        self.filter='median'
        sigma, ok=QInputDialog.getInt(self,'Median Filter ','Enter sigma value (radius)')
        if ok:
            self.sigma=sigma
            self.filtreBox.setText('F: Median')
            self.Display(self.data)
        
        
    def Orig(self):
        """
        return data without filter
        """
        self.data=self.dataOrg
        self.filter='origin'
        self.Display(self.data)
        self.filtreBox.setText('Filters')
        print('original')
        
    def OpenF(self,fileOpen=False):
        #open file in txt spe TIFF sif jpeg png  format
        fileOpen=fileOpen
        
        if fileOpen==False:
            
            chemin=self.conf.value(self.name+"/path")
            fname=QtGui.QFileDialog.getOpenFileNames(self,"Open File",chemin,"Images (*.txt *.spe *.TIFF *.sif *.tif);;Text File(*.txt);;Ropper File (*.SPE);;Andor File(*.sif);; TIFF file(*.TIFF)")
            
            fichier=fname[0]
            self.openedFiles=fichier

            self.nbOpenedImage=len(fichier)
            if self.nbOpenedImage==1:
                fichier=fichier[0]
                self.sliderImage.setEnabled(False)
            if self.nbOpenedImage>1:
                fichier=fichier[0]
                self.sliderImage.setMinimum(0)
                self.sliderImage.setMaximum(self.nbOpenedImage - 1)
                self.sliderImage.setValue(0)
                self.sliderImage.setEnabled(True)
                
                
        else:
            fichier=str(fileOpen)
            
        ext=os.path.splitext(fichier)[1]
        
        if ext=='.txt': # text file
            data=np.loadtxt(str(fichier))
        elif ext=='.spe' or ext=='.SPE': # SPE file
            dataSPE=SpeFile(fichier)
            data1=dataSPE.data[0]#.transpose() # first frame
            data=data1#np.flipud(data1)
        elif ext=='.TIFF' or ext=='.tif' or ext=='.Tiff' or ext=='.jpg' or ext=='.JPEG' or ext=='.png': # tiff File
            dat=Image.open(fichier)
            data=np.array(dat)
            data=np.rot90(data,3)
        elif ext=='.sif': 
            sifop=SifFile()
            im=sifop.openA(fichier)
            data=np.rot90(im,3)
#            self.data=self.data[250:495,:]
        else :
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Wrong file format !")
            msg.setInformativeText("The format of the file must be : .SPE  .TIFF .sif  png jpeg or .txt ")
            msg.setWindowTitle("Warning ...")
            msg.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            msg.exec_()
            
        chemin=os.path.dirname(fichier)
        self.conf.setValue(self.name+"/path",chemin)
        self.conf.setValue(self.name+"/lastFichier",os.path.split(fichier)[1])
        print('open',fichier)
        
        self.fileName.setText(str(fichier))
        self.nomFichier=os.path.split(fichier)[1]
    
        self.newDataReceived(data)
        
    
    
    def SliderImgFct(self):
        nbImgToOpen=int(self.sliderImage.value())
        
        self.OpenF(fileOpen=self.openedFiles[nbImgToOpen])
        
    def SaveF (self):
        # save data  in TIFF or Text  files
        
        if self.winOpt.checkBoxTiff.isChecked()==True: 
            fname=QtGui.QFileDialog.getSaveFileName(self,"Save data as TIFF",self.path)
            self.path=os.path.dirname(str(fname[0]))
            fichier=fname[0]
        
            ext=os.path.splitext(fichier)[1]
            #print(ext)
            print(fichier,' is saved')
            self.conf.setValue(self.name+"/path",self.path)
            time.sleep(0.1)
            self.dataS=np.rot90(self.data,1)
            img_PIL = Image.fromarray(self.dataS)

            img_PIL.save(str(fname[0])+'.TIFF',format='TIFF')
            np.savetxt(str(fichier)+'_Time'+'.txt',self.axisX )
            np.savetxt(str(fichier)+'_Wavelength'+'.txt',self.axisY )
            self.fileName.setText(fname[0]+'.TIFF') 
            
        else :
            fname=QtGui.QFileDialog.getSaveFileName(self,"Save data as txt",self.path)
            self.path=os.path.dirname(str(fname[0]))
            fichier=fname[0]
            self.dataS=np.rot90(self.data,1)
            ext=os.path.splitext(fichier)[1]
            #print(ext)
            print(fichier,' is saved')
            self.conf.setValue(self.name+"/path",self.path)
            time.sleep(0.1)
            np.savetxt(str(fichier)+'.txt',self.dataS)
            np.savetxt(str(fichier)+'_Time'+'.txt',self.axisX )
            np.savetxt(str(fichier)+'_Wavelength'+'.txt',self.axisY )
            self.fileName.setText(fname[0]+str(ext))

  
    def newDataReceived(self,data,axisX=None,axisY=None):
        # Do display and save origin data when new data is  sent to  visu
        self.data=data
        if self.flipButton.isChecked()==1 and self.flipButtonVert.isChecked()==1 :
            self.data=np.flipud(self.data)
            self.data=np.fliplr(self.data)
        elif self.flipButton.isChecked()==1:
            self.data=np.flipud(self.data)
        elif self.flipButtonVert.isChecked()==1 :
            self.data=np.fliplr(self.data)
        else:
            self.data=data
        self.dimy=np.shape(self.data)[1]
        self.dimx=np.shape(self.data)[0]
        self.dataOrgScale=self.data
        self.dataOrg=self.data
        
        self.axisX=axisX
        self.axisY=axisY
        # print('X',self.axisX,np.shape(self.axisX))
        # print('Y',self.axisY,np.shape(self.axisY))
        if self.axisX is None:
            self.axisXPixel=True
        else:
            self.axisXPixel=False
        
        
        self.Display(self.data)
        
    

    
    def ScaleImg(self):
        #scale Axis px to um
        if self.winPref.checkBoxAxeScale.isChecked()==1:
            self.scaleAxis="on"
            self.LigneChanged()
        else :
            self.scaleAxis="off"
        self.data=self.dataOrg
        self.Display(self.data)
    
    
    def zoomRectAct(self):
        
        if self.plotRectZoomEtat=="Zoom": 
            
            self.p1.addItem(self.plotRectZoom)
            self.plotRectZoom.setPos([self.dimx/2,self.dimy/2])
            self.ZoomRectButton.setIcon(QtGui.QIcon(self.icon+"zoom-in.png"))
            self.plotRectZoomEtat="ZoomIn"
            
        elif self.plotRectZoomEtat=="ZoomIn":
            self.ZoomRectButton.setIcon(QtGui.QIcon(self.icon+"zoom-out.png"))
            self.xZoomMin=(self.plotRectZoom.pos()[0])
            self.yZoomMin=(self.plotRectZoom.pos()[1])
            self.xZoomMax=(self.plotRectZoom.pos()[0])+self.plotRectZoom.size()[0]
            self.yZoomMax=(self.plotRectZoom.pos()[1])+self.plotRectZoom.size()[1]
            self.p1.setXRange(self.xZoomMin,self.xZoomMax)
            self.p1.setYRange(self.yZoomMin,self.yZoomMax)
            #self.p1.setAspectLocked(True)
            self.p1.removeItem(self.plotRectZoom)
            
            self.xMin=self.axisX[int(self.xZoomMin)]
            self.xMax=self.axisX[int(self.xZoomMax)]
            self.yMin=self.axisY[int(self.yZoomMin)]
            self.yMax=self.axisY[int(self.yZoomMax)]
            
            self.widgetRange.xMinBox.setValue(self.xMin)
            self.widgetRange.yMinBox.setValue(self.yMin)
            self.widgetRange.xMaxBox.setValue(self.xMax)
            self.widgetRange.yMaxBox.setValue(self.yMax)
            
            
            self.winPLOTX.setXRange(self.xMin,self.xMax)
            self.winPLOTY.setYRange(self.yMin,self.yMax)
            
            self.plotRectZoomEtat="ZoomOut"
        
        elif self.plotRectZoomEtat=="ZoomOut": 
            self.p1.setYRange(0,self.dimy)
            self.p1.setXRange(0,self.dimx)
            self.xMax=self.axisX.max()
            self.yMax=self.axisY.max()
            self.xMin=self.axisX.min()
            self.yMin=self.axisY.min()
            self.winPLOTX.setXRange(self.xMin,self.xMax)
            self.winPLOTY.setYRange(self.yMin,self.yMax)
            self.ZoomRectButton.setIcon(QtGui.QIcon(self.icon+"loupe.png"))
            self.plotRectZoomEtat="Zoom"
            #self.p1.setAspectLocked(True,ratio=1)
            
    def zoomRectupdate(self):
        if self.plotRectZoomEtat=="ZoomOut":
            self.p1.setXRange(self.xZoomMin,self.xZoomMax)
            self.p1.setYRange(self.yZoomMin,self.yZoomMax)
            
            self.xMax=self.axisX.max()
            self.yMax=self.axisY.max()
            self.xMin=self.axisX.min()
            self.yMin=self.axisY.min()
            self.winPLOTX.setXRange(self.xMin,self.xMax)
            self.winPLOTY.setYRange(self.yMin,self.yMax)
            #self.p1.setAspectLocked(True)
        else:
            self.p1.setYRange(0,self.dimy)
            self.p1.setXRange(0,self.dimx)
            self.xMax=self.axisX.max()
            self.yMax=self.axisY.max()
            self.xMin=self.axisX.min()
            self.yMin=self.axisY.min()
            self.winPLOTX.setXRange(self.xMin,self.xMax)
            self.winPLOTY.setYRange(self.yMin,self.yMax)
            
    def flipAct (self):
        
        self.data=np.flipud(self.data)
        self.Display(self.data)
    
    def flipVertAct (self):
        
        self.data=np.fliplr(self.data)
        self.Display(self.data)
    
  
    
    
    def open_widget(self,fene):
        """ open new widget 
        """

        if fene.isWinOpen==False:
            fene.setup
            fene.isWinOpen=True
            
            #fene.Display(self.data)
            fene.show()
        else:
            #fene.activateWindow()
            fene.raise_()
            fene.showNormal()
    
    
    def dragEnterEvent(self, e):
        e.accept()

        
    def dropEvent(self, e):
        l = []
        for url in e.mimeData().urls():
            l.append(str(url.toLocalFile()))
        e.accept()
        self.OpenF(fileOpen=l[0])
    
    
    
    def gauss(self,x, A, mu, sigma ,B):
        if sigma==0:
            sigma=0.1
        try :
            gau=A*np.exp(-(x-mu)**2/(2*sigma**2))+B
        except : gau=0
        return gau
    
    
    
    def setFit(self,data,xMat):
        
        xxx=xMat
        # print('matx',xxx)    
        try :
            Datafwhm,xDataMax=self.fwhm(xxx,data)
        except :
            Datafwhm,xDataMax=0,0
            
        ymaxx=data[int(xDataMax)]
        init_vals = [ymaxx, xDataMax, Datafwhm,0]  # for [A, mu, sigma]
        try : 
            best_vals, covar = curve_fit(self.gauss, xxx, data, p0=init_vals)
        
            y_fit = self.gauss(xxx, best_vals[0], best_vals[1], best_vals[2],best_vals[3])
        
            self.pFit.setData(x=xxx,y=y_fit)
        
        
        
            self.fitA=best_vals[0]
            self.fitMu=best_vals[1]
            self.fitSigma=best_vals[2]
        
            self.fwhmLabelFitValue.setText(str(self.fitSigma*2.355))#2.355
        except :
            self.fwhmLabelFitValue.setText('...')
    
    
    def autoScale(self):
        
        if self.checkBoxScale.isChecked()==1: # color autoscale on
            if self.winPref.checkBoxAxeScale.isChecked()==1:
                self.axeX.setScale(self.winOpt.stepX)
                self.axeY.setScale(self.winOpt.stepY)
                self.axeX.setLabel('um')
                self.axeY.setLabel('um')
                self.axeX.showLabel(True)
            if self.winPref.checkBoxAxeScale.isChecked()==0:
                self.scaleAxis="off"
                self.axeX.setScale(1)
                self.axeY.setScale(1)  
                self.axeX.showLabel(False)
            self.imh.setImage(self.data,autoLevels=True,autoDownsample=True)
    
    def logMode(self):
       
        if self.logActionX.isChecked():
            self.data=np.log(self.data)
            self.Display(self.data)
        else:
            self.data=self.dataOrg
            self.Display(self.data)
        
        #     self.hist.setLogMode(False,True)
        
        #     self.hist.autoHistogramRange() 
        
        #     self.hist.plot.setLogMode(False,False)
        
        #     self.hist.autoHistogramRange()
    
    def setRangeOn(self) :       
        self.xZoomMin=(self.widgetRange.xMinBox.value())
        self.yZoomMin=(self.widgetRange.yMinBox.value())
        self.xZoomMax=(self.widgetRange.xMaxBox.value())
        self.yZoomMax=(self.widgetRange.yMaxBox.value())
        
        
        # transform value to index
        self.xZoomMin=list((abs(self.axisX-self.xZoomMin))).index(min(list(abs(self.axisX-self.xZoomMin))))
        
        self.xZoomMax=list((abs(self.axisX-self.xZoomMax))).index(min(list(abs(self.axisX-self.xZoomMax))))
       
        self.yZoomMin=list((abs(self.axisY-self.yZoomMin))).index(min(list(abs(self.axisY-self.yZoomMin))))
        
        self.yZoomMax=list((abs(self.axisY-self.yZoomMax))).index(min(list(abs(self.axisY-self.yZoomMax))))
       
        print(self.xZoomMin,self.xZoomMax)
       
        
        self.p1.setXRange(self.xZoomMin,self.xZoomMax)
        self.p1.setYRange(self.yZoomMin,self.yZoomMax)
        
        self.xMax=self.widgetRange.xMaxBox.value()
        self.yMax=self.widgetRange.yMaxBox.value()
        self.xMin=self.widgetRange.xMinBox.value()
        self.yMin=self.widgetRange.yMinBox.value()
        
        self.winPLOTX.setXRange(self.xMin,self.xMax)
        self.winPLOTY.setYRange(self.yMin,self.yMax)
        
        self.plotRectZoomEtat="ZoomIn"
        
    def setRangeReset(self) :  
        
        self.p1.setYRange(0,self.dimy)
        self.p1.setXRange(0,self.dimx)
        
        self.xMax=self.axisX.max()
        self.yMax=self.axisY.max()
        self.xMin=self.axisX.min()
        self.yMin=self.axisY.min()
        
        self.winPLOTX.setXRange(self.xMin,self.xMax)
        self.winPLOTY.setYRange(self.yMin,self.yMax)
        
        
        self.ZoomRectButton.setIcon(QtGui.QIcon(self.icon+"loupe.png"))
        self.plotRectZoomEtat="Zoom"    
    
    
    def closeEvent(self,event):
        # when the window is closed
        if self.encercled=="on":
            if self.winEncercled.isWinOpen==True:
                self.winEncercled.close()
        if self.winCoupe.isWinOpen==True:
            self.winCoupe.close()
        if self.meas=="on":
            if self.winM.isWinOpen==True:
                self.winM.close()
        if self.winOpt.isWinOpen==True:
            self.winOpt.close() 
        if self.fft=='on':
            if self.winFFT.isWinOpen==True:
                self.winFFT.close()
            if self.winFFT1D.isWinOpen==True:
                self.winFFT1D.close()
        
   
if __name__ == "__main__":
    
    appli = QApplication(sys.argv) 
    appli.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    
    e = SEERESULT()
    e.show()
    appli.exec_() 
