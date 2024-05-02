from PyQt5 import QtWidgets, uic, QtCore
from tenz import *
import sys
import time
import threading

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
    def __rep__(self):
        return self.feltShock

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

class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progressChanged = QtCore.pyqtSignal(int)
    shockAdministered = QtCore.pyqtSignal()

    def __init__(self):
        super(Worker, self).__init__()
        self.shockCount = 0

    def run(self):
        for _ in range(10):
            self.incrementProgressBar()
            shock()
            self.shockAdministered.emit()
            self.progressChanged.emit(0)
        self.finished.emit()

    def incrementProgressBar(self):
        for _ in range(5):
            progress_value = (_ + 1) * 20
            self.progressChanged.emit(progress_value)
            time.sleep(1)

class Ui_main(QtWidgets.QDialog):
    results = [resultObj() for i in range(10)]
    def __init__(self):
        super(Ui_main, self).__init__()
        uic.loadUi(mainScreen, self)
        self.shockCount = 0
        self.shock_count.setDigitCount(2)
        self.feel_it_btn.clicked.connect(self.onBtnClick)
        self.back_btn.clicked.connect(self.onClickBackBtn)
        self.start_btn.clicked.connect(self.onClickStartBtn)
        self.stop_btn.clicked.connect(self.onClickStopBtn)
        self.worker = Worker()
        self.workerThread = QtCore.QThread()
        self.worker.moveToThread(self.workerThread)
        self.worker.finished.connect(self.workerThread.quit)
        self.worker.shockAdministered.connect(self.incrementShockCount)
        self.worker.progressChanged.connect(self.updateProgressBar)
        self.workerThread.started.connect(self.worker.run)
    def onClickBackBtn(self):
        self.close()
        startDialog = Ui()
        startDialog.exec_()
    def onClickStartBtn(self):
        self.shockCount = 0
        self.workerThread.start()    
    def onBtnClick(self):
        # TODO: save the result {feltShock: true, timing: <time>}
        Ui_main.results[self.shockCount-1].setShockToTrue()
        print(Ui_main.results[self.shockCount-1].feltShock)
        pass
    def onClickStopBtn(self):
        set_GPIO_low();
        self.workerThread.quit()
        self.close()
    def incrementShockCount(self):
        self.shockCount += 1
        self.shock_count.display(self.shockCount)
        if self.shockCount >= 3:
            #TODO: if shockcount more than 10, then show a result screen ??
            # print(list(Ui_main.results.feltShock))
            pass
    def updateProgressBar(self, value):
        # Update progress bar value based on the shock count
        self.progressBar.setValue(value)


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()