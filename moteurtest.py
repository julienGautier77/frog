
from PyQt5.QtCore import QSettings

confTest=QSettings('./fichiersConfig/configMoteurTest.ini', QSettings.IniFormat)

class MOTORTEST():
    
    def __init__(self, mot1='',parent=None):
        
        super(MOTORTEST, self).__init__()
        self.moteurname=mot1
        #print(self.moteurname)
        self.numMoteur=int(confTest.value(self.moteurname+'/numMoteur'))
        #print('init motor test')
 
    def rmove(self,pas,vitesse=1000):
        
        print('motor',self.moteurname,'rmove',pas)
        #return recu

    def move(self,position,vitesse=1000):
        print('motor',self.moteurname,'move',position)
        
    
    def position(self):
        return 12345
    
    def setzero(self):
        confTest.setValue(self.moteurname+"/Pos",0)
    
    def name(self):
        return self.moteurname
    def stopMotor(self):
        print('stop motor')
