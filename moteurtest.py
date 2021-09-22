
from PyQt5.QtCore import QSettings


class MOTORTEST():
    
    def __init__(self, mot1='',parent=None):
        
        super(MOTORTEST, self).__init__()
        self.moteurname=mot1
        self.confTest=QSettings('./fichiersConfig/configMoteurTest.ini', QSettings.IniFormat)

        #print(self.moteurname)
        self.numMoteur=int(self.confTest.value(self.moteurname+'/numMoteur'))
        #print('init motor test')
        
    def rmove(self,pas,vitesse=1000):
        
        print('motor : ',self.moteurname,'rmove of ',pas)
        posi= float(self.confTest.value(self.moteurname+'/Pos'))+pas
        self.confTest.setValue(self.moteurname+'/Pos',posi)

    def move(self,position,vitesse=1000):
        print('motor : ',self.moteurname,'move to ',position)
        self.confTest.setValue(self.moteurname+'/Pos',position)
    
    def position(self):
        return float( self.confTest.value(self.moteurname+'/Pos'))
    
    def setzero(self):
        self.confTest.setValue(self.moteurname+"/Pos",0)
    
    def name(self):
        return self.moteurname
    def stopMotor(self):
        print('Stop motor')
