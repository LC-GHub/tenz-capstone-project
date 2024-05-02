from PyQt5 import QtWidgets, uic, QtCore, QtGui
from tenz import *
import sys
import time
import threading

startScreen = './screens/start.ui'
mainScreen = './screens/main.ui'
summaryScreen = './screens/summary.ui'

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
        self.timer=QtCore.QElapsedTimer()

    def run(self):
        for _ in range(10):
            self.incrementProgressBar()
            self.timer.restart()
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
    shocksFinished = QtCore.pyqtSignal()
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
        self.shocksFinished.connect(self.showSummary)

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
        Ui_main.results[self.shockCount-1].setTiming(float(elapsed_time))
        Ui_main.results[self.shockCount-1].setShockToTrue()
 
    def onClickStopBtn(self):
        set_GPIO_low();
        self.workerThread.quit()
        self.close()
    def incrementShockCount(self):
        self.shockCount += 1
        self.shock_count.display(self.shockCount)
        if self.shockCount >= 10:
            self.shocksFinished.emit()
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
            table_data.append((i+1, "Felt" if result.feltShock else "Not Felt", result.timing))
        print("table data", table_data)
        print(type(len(table_data)))
        model = QtGui.QStandardItemModel(len(table_data), 3)
        model.setHorizontalHeaderLabels(['Shock #', "Felt", "Timing"])

        for row, (shock_num, felt, timing) in enumerate(table_data):
            model.setItem(row, 0, QtGui.QStandardItem(str(shock_num)))
            model.setItem(row, 1, QtGui.QStandardItem(felt))
            model.setItem(row, 2, QtGui.QStandardItem(str(timing)))
        
        model.setItem(row+1,0, QtGui.QStandardItem(str("Avg")))
        avg_time = self.averageTime(Ui_main.results)
        model.setItem(row+1,2, QtGui.QStandardItem(str(avg_time)))
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