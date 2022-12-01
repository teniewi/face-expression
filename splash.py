
from ast import main
from cgitb import strong
from fileinput import close
import sys
from PyQt5.QtWidgets import  QApplication, QMainWindow
from PyQt5 import QtCore



# Import user interface file
from ui_splash import Ui_SplasScreen
from main import webCam

# Global 
counter = 0

# Splash Screen Class
class SplashScreen(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_SplasScreen()
        self.ui.setupUi(self)

        # Remove Window Title Bar
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)

        # Set Background To transparent
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Initial Text
        self.ui.label_Description.setText("Welcome To My Application")

        # Change Text
        QtCore.QTimer.singleShot(1500, lambda: self.ui.label_Description.setText("Loading ."))
        QtCore.QTimer.singleShot(2000, lambda: self.ui.label_Description.setText("Loading . ."))
        QtCore.QTimer.singleShot(2500, lambda: self.ui.label_Description.setText("Loading . . . "))
        QtCore.QTimer.singleShot(3500, lambda: self.ui.label_Description.setText("<strong>LOADING</strong> DATABASE"))
        QtCore.QTimer.singleShot(4500, lambda: self.ui.label_Description.setText("<strong>LOADING</strong> User Interface"))


        # QTimer Start
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)

        #Timer in Millisecond
        self.timer.start(45)

        # Show Window
        self.show()

    def progress(self):

        global counter

        # Set value progress bar
        self.ui.progressBar.setValue(counter)

        # Close Splash Screen and open app
        if counter >= 100:
            # Stop Timer
            self.timer.stop()

            # Start App
            self.outputWindow_()
            self.close()

        counter +=1

    def outputWindow_(self):
        self._new_window = webCam()
        self._new_window.show()


# Execute App
if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = SplashScreen()

    sys.exit(app.exec_())
