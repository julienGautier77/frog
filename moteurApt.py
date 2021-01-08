
from PyQt5.QtCore import QSettings

confApt=QSettings('./fichiersConfig/configMoteurApt.ini', QSettings.IniFormat)
from DLL.apt import core



class MOTORAPT():
    def __init__(self, mot1='',parent=None):
        #super(MOTORNEWPORT, self).__init__()
        self.moteurname=mot1
        self.numMoteur=int(confApt.value(self.moteurname+'/numMoteur'))
        print(self.numMoteur)
        self.aptMotor=core.Motor(self.numMoteur)
        
    def stopMotor(self): # stop le moteur motor
        """ stopMotor(motor): stop le moteur motor """
        self.numMoteur.stop_profiled
    
    def rmove(self,pas,vitesse=1000):
        actualPosition=int(confApt.value(self.moteurname+'/Pos'))
        
        position=actualPosition+pas
        
        self.aptMotor.move_by(pas)
       
        confApt.setValue(self.moteurname+"/Pos",position)
        confApt.sync()
        #return recu

    def move(self,position,vitesse=1000):
        
        actualPosition=float(confApt.value(self.moteurname+'/Pos'))
        pas=(position)-(actualPosition)
        
        self.aptMotor.move_by(pas)
        
        #self.aptMotor.move_to(position)
        confApt.setValue(self.moteurname+"/Pos",position)
        confApt.sync()
        #return recu
    
    def position(self):
        #position = self.aptMotor.position()
        position=float(confApt.value(self.moteurname+'/Pos'))
        return position
    
    def setzero(self):
        confApt.setValue(self.moteurname+"/Pos",0)
        

    
