from PyQt5 import QtWidgets, uic, QtCore, QtGui
# tenz.py is where the tenz service (GPIO pin is set there too!)
from tenz import *
import sys
import time
import threading
import random

startScreen = './screens/start.ui'
mainScreen = './screens/main.ui'
summaryScreen = './screens/summary.ui'

class resultObj:
    isShock:bool
    feltShock: bool
    timing: float
    def __init__(self, feltShock: bool = False, timing: float = 0.0, isShock: bool = False):
        self.feltShock = feltShock
        self.timing = timing
        self.isShock = isShock
    def setIsShock(self):
        self.isShock = True
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
    shocksFinished = QtCore.pyqtSignal()

    def __init__(self, results):
        super(Worker, self).__init__()
        self.shockCount = 0
        self.timer=QtCore.QElapsedTimer()

    def run(self):
        self.incrementProgressBar()
        self.timer.restart()
        for i in range(10):
            if i is 9:
                self.incrementProgressBar()
                self.shocksFinished.emit()
            else:
                random_int = random.randint(1,10)
                if random_int > 3:
                    Ui_main.results[i].setIsShock()
                shock_w_placebo(random_int)
                self.shockAdministered.emit()
                self.progressChanged.emit(0)
                self.incrementProgressBar()
                self.timer.restart()
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
        self.worker = Worker(self.results)
        self.workerThread = QtCore.QThread()
        self.worker.moveToThread(self.workerThread)
        self.worker.finished.connect(self.workerThread.quit)
        self.worker.shockAdministered.connect(self.incrementShockCount)
        self.worker.progressChanged.connect(self.updateProgressBar)
        self.workerThread.started.connect(self.worker.run)
        self.worker.shocksFinished.connect(self.showSummary)

    def onClickBackBtn(self):
        self.close()
        startDialog = Ui()
        startDialog.exec_()
    def onClickStartBtn(self):
        self.shockCount = 0
        self.workerThread.start()    
    def onBtnClick(self):
        elapsed_time = self.worker.timer.elapsed()
        print(elapsed_time)
        print("onBtnClick's SC")
        Ui_main.results[self.shockCount-1].setTiming(float(elapsed_time))
        Ui_main.results[self.shockCount-1].setShockToTrue()
 
    def onClickStopBtn(self):
        set_GPIO_low();
        self.workerThread.quit()
        self.close()
    def incrementShockCount(self):
        self.shockCount += 1
        print("incrementSC")
        print(self.shockCount)
        self.shock_count.display(self.shockCount)
        if self.shockCount is 10:
            print("seq ended")
            
    def updateProgressBar(self, value):
        # Update progress bar value based on the shock count
        self.progressBar.setValue(value)
    def showSummary(self):
        summaryDialog = UiSummary()
        summaryDialog.exec_()

class UiSummary(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(UiSummary, self).__init__(parent)
        uic.loadUi(summaryScreen, self)
        self.btn_close.clicked.connect(self.onBtnCloseClick)
        self.populateTable()
    def onBtnCloseClick(self):
        set_GPIO_low();
        self.workerThread.quit()
        self.close()
    def populateTable(self):
        table_data = []
        for i, result in enumerate(Ui_main.results):
            table_data.append((i+1, 1 if result.feltShock else 0,1 if result.isShock else 0 ,result.timing))
        print("table data", table_data)
        print(type(len(table_data)))
        model = QtGui.QStandardItemModel(len(table_data), 4)
        model.setHorizontalHeaderLabels(['Shock #', "Felt", "Is Shock","Timing"])

        for row, (shock_num, felt,isShock ,timing) in enumerate(table_data):
            model.setItem(row, 0, QtGui.QStandardItem(str(shock_num)))
            model.setItem(row, 1, QtGui.QStandardItem(str(felt)))
            model.setItem(row, 2, QtGui.QStandardItem(str(isShock)))
            model.setItem(row, 3, QtGui.QStandardItem(str(timing)))
        
        model.setItem(row+1,0, QtGui.QStandardItem(str("Avg")))
        avg_time = self.averageTime(Ui_main.results)
        model.setItem(row+1,3, QtGui.QStandardItem(str(avg_time)))
        self.tableView.setModel(model)
    def averageTime(self,results):
        total_timing = sum(result.timing for result in results)
        num_results = len(results)
        if num_results == 0:
            return 0.0
        return total_timing / num_results

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()