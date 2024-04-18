from PyQt5 import QtWidgets, uic
import sys
import time

startScreen = './screens/start.ui'
mainScreen = './screens/main.ui'

class resultObj:
    feltShock: bool
    timing: float
    def __init__(self, feltShock: bool = False, timing: float = 0.0):
        self.feltShock = feltShock
        self.timing = timing
    def setShockToTrue(self):
        self.feltShock = True
    def setTiming(self, time):
        self.timing = time

class Ui(QtWidgets.QDialog):
    seconds = time.time()
    print("Time in seconds since the epoch:", seconds)  
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi(startScreen, self)
        self.start_btn.clicked.connect(self.openMainDialog)
        self.show()
    def openMainDialog(self):
        self.close();
        mainDialog = Ui_main()
        mainDialog.exec_();

class Ui_main(QtWidgets.QDialog):
    results = [resultObj() for i in range(10)]
    def __init__(self):
        super(Ui_main, self).__init__()
        uic.loadUi(mainScreen, self)
        shockCount = 0
        self.shock_count.setDigitCount(2)
        self.feel_it_btn.clicked.connect(self.onBtnClick)
        self.back_btn.clicked.connect(self.onClickBackBtn)
    def onClickBackBtn(self):
        self.close()
        startDialog = Ui()
        startDialog.exec_();
    def onBtnClick(self):
        # TODO: save the result {feltShock: true, timing: <time>}
        pass
    def incrementShockCount(self):
        shockCount = shockCount + 1
        self.shock_count.display(shockCount)
        if shockCount >= 10:
            #TODO: if shockcount more than 10, then show a result screen ??
            pass


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()