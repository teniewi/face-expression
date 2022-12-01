
import sys
import cv2
from cv2 import CAP_DSHOW
import imutils
import numpy as np

import PyQt5
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import QTimer, pyqtSlot, QDate
from PyQt5.uic import loadUi
from PyQt5.QtGui import QImage, QPixmap, QCloseEvent
import datetime
from sklearn.metrics import accuracy_score
import tensorflow as tf
import time
import pyshine as ps

import pymysql as con

feedback = {0: "Puas", 1: "Tidak Puas", 2: "Netral"}

model = tf.keras.models.load_model('best_model.h5')

face_detector = cv2.CascadeClassifier(r'C:\Program Files\anaconda3\envs\Skripsi\Project_Skripsi\haarcascade_frontalface_default.xml')
     
class webCam (QDialog):

    

    def __init__(self):
        super(webCam, self).__init__()
        loadUi("main.ui", self)

        #self.koneksi()
        # Update Time
        now = QDate.currentDate()
        curent_date = now.toString('ddd dd MMMM yyyy')
        curent_time = datetime.datetime.now().strftime('%I:%M %p')
        self.Date_Label.setText(curent_date)
        self.Time_Label.setText(curent_time)

        self.imput.clicked.connect(self.input_)
        self.tampil.clicked.connect(self.tampil_)
        self.updated.clicked.connect(self.updated_)
        self.hapus.clicked.connect(self.clear_)

        self.on = None

        self.status = None 

        self.startWebcam.clicked.connect(self.Start_webcam)
        self.stopWebcam.clicked.connect(self.Stop_webcam)

    """
    def koneksi(self):
        db = con.connect(host = "localhost",user = "root",password = "",db = "riefhy_store", autocommit=True)
        cur = db.cursor()
        if(cur):
            self.messagebox("Koneksi","Koneksi Berhasil")
        else:
            self.messagebox("Koneksi","Koneksi Gagal")
    """

    def messagebox(self, title, message):
        mess = QtWidgets.QMessageBox()
        mess.setWindowTitle(title)
        mess.setText(message)
        mess.setStandardButtons(QtWidgets.QMessageBox.Ok)
        mess.exec_()


    def input_(self):
        nama_pelanggan = self.tb1.toPlainText()
        nama_barang = self.tb2.toPlainText()
        nohp = self.tb4.toPlainText()
        insert = (nohp, nama_pelanggan, nama_barang)
        db = con.connect(host = "localhost",user = "root",password = "",db = "riefhy_store", autocommit=True)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM orderan WHERE no_hp = '" + nohp + "'" )
        data = cursor.fetchone()
        if (data):
            self.messagebox("GAGAL", "No Hp Sudah Ada")
        else:
            cursor.execute("INSERT INTO orderan (no_hp, nama_pelanggan, barang_orderan) VALUES " + str(insert))
            self.tb1.setPlainText("")
            self.tb2.setPlainText("")
            self.tb4.setPlainText("")
            self.messagebox("SUKSES", "Data tersimpan")
        

    def updated_(self):
        nama_pelanggan = self.tb1.toPlainText()
        nama_barang = self.tb2.toPlainText()
        status_ = self.tb3.toPlainText()
        nohp = self.tb4.toPlainText()
        db = con.connect(host = "localhost",user = "root",password = "",db = "riefhy_store", autocommit=True)
        cursor = db.cursor()
        sql = "UPDATE orderan SET nama_pelanggan=%s, barang_orderan=%s, feedback=%s WHERE no_hp=%s"
        data = cursor.execute(sql, (nama_pelanggan, nama_barang, status_, nohp))
        if (data):
            self.messagebox("SUKSES", "Data terupdate")
        else:
            self.messagebox("GAGAL", "Data gagal terupdate")

    def tampil_(self):
        nama_pelanggan = self.tb1.toPlainText()
        db = con.connect(host = "localhost",user = "root",password = "",db = "riefhy_store", autocommit=True)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM orderan WHERE nama_pelanggan = '" + str(nama_pelanggan) + "'")
        data = cursor.fetchall()
        if (data):
            for tp in data:
                self.tb1.setPlainText(""+tp[0])
                self.tb2.setPlainText(""+tp[2])
                self.tb4.setPlainText(""+tp[1])
        else:
            self.messagebox("INVALID", "Data tidak ada, Silahkan Input Data")

    def clear_(self):
        self.tb1.setPlainText("")
        self.tb2.setPlainText("")
        self.tb3.setPlainText("")
        self.tb4.setPlainText("")

    @pyqtSlot()
    def Start_webcam(self):
        cam = True # True for webcam
        if cam:
            vid = cv2.VideoCapture(0)
            self.on = vid
            
        else:
            vid = cv2.VideoCapture('video.mp4')
        
        
        pTime = 0
        
        while(self.on.isOpened()):
            QtWidgets.QApplication.processEvents()	
            img, self.image = vid.read()
            self.image = cv2.flip(self.image, 1)
            self.image = imutils.resize(self.image ,height = 480 )
            
            gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY) 

            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime
            cv2.putText(self.image, f'FPS: {int(fps)}', (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            try:
                faces = face_detector.detectMultiScale(
                gray,
                scaleFactor=1.15,  
                minNeighbors=3, 
                minSize=(80, 80), 
                flags=cv2.CASCADE_SCALE_IMAGE)

                for (x, y, w, h) in faces:
                    cv2.rectangle(self.image, (x, y), (x + w, y + h), (10, 228,220), 5) 
                    roi_gray_frame = gray[y:y + h, x:x + w]
                    cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray_frame, (48, 48)), -1), 0)
       
                    # predict the emotions
                    emotion_prediction = model.predict(cropped_img)
                    maxindex = int(np.argmax(emotion_prediction))
                    self.status = feedback[maxindex]
                    cv2.putText(self.image, self.status, (x+5, y-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
                    
                    self.tb3.setPlainText(self.status)
                    
                    
                

            except Exception as e:
                pass
            
            
            self.update()
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def update(self):
        #img = self.Start_webcam()
        # Here we add display text to the image
        #text  =  'FPS: '+str(self.fps)
        #img = ps.putBText(img,text,text_offset_x=20,text_offset_y=30,vspace=20,hspace=10, font_scale=1.0,background_RGB=(10,20,222),text_RGB=(255,255,255))
        self.displayImage(self.image, 1)

    def displayImage(self, img, window = 1):
        format = QImage.Format_Indexed8
        if len(img.shape) == 3: # [0] = rows, [1]= cols, [2]= channels
            if img.shape[2]== 4:
                format = QImage.Format.Format_RGBA8888
            else:
                format = QImage.Format.Format_RGB888

        outImage = QImage(img, img.shape[1], img.shape[0], img.strides[0], format)
        # BGR to RGB
        outImage = outImage.rgbSwapped()

        if window == 1:
            self.imgLabel.setPixmap(QPixmap.fromImage(outImage))
            self.imgLabel.setScaledContents(True)

    def Stop_webcam(self):
        self.on.release()
        self.imgLabel.clear()
        self.tb3.setPlainText("")
        self.image = None

    def closeEvent(self, event):
        if self.on:
            self.on.release()
            self.image = None
        else:
            event.accept()
        self.image = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    web = webCam()
    web.show()
    sys.exit(app.exec_())
