from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QAction, QMessageBox, QMenu, QListWidgetItem, QFileDialog,QLabel
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
from scipy import misc,optimize
from PIL import Image, ImageQt


ui_main_window, q_main_window = loadUiType("ui/loadImages.ui")


class Main(q_main_window, ui_main_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # self.menubar.setNativeMenuBar(False)  # for osx to present the menu inside the app
        self.data = None
        self.init_slot()
        self.setMouseTracking(True)
        self.point_list=[]

    def init_slot(self):
        # self.glayout = pg.GraphicsLayout()
        # self.vb = self.glayout.addViewBox()
        self.Button_load.pressed.connect(self.loadImages)
        # self.Button_up.pressed.connect(self.z_up)
        # self.Button_down.pressed.connect(self.z_down)
        self.Button_erase.pressed.connect(self.deletePoints)
        self.Btn_showz.pressed.connect(self.show_z)
        self.Button_confirm.pressed.connect(self.leastsq_circle)
        # self.Button_confirm.pressed.connect()


    def loadImages(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fileNames, _ = QFileDialog.getOpenFileNames(None,"QFileDialog.getOpenFileName()",
        "","All Files (*);;Python Files (*.py)", options=options)
        im = np.array([np.array(Image.open(fname)) for fname in self.fileNames])
        self.particle_im.setImage(
            im, autoRange=False,
            xvals=np.arange(im.shape[0]),scale=(512,512),pos=(-50,-50)
        )
        # self.particle_im.autoRange()
        print(dir(self.particle_im.ui))
        self.particle_im.ui.histogram.hide()
        self.particle_im.ui.roiBtn.hide()
        self.particle_im.ui.menuBtn.hide()
        self.z_current = self.particle_im.currentIndex
        # self.label.setPixmap(QPixmap(self.fileNames[self.z_current]))
        # self.particle_im.setMouseTracking(True)
        self.pTextEdit.appendPlainText('z =' + str(self.z_current))

    def show_z(self):
        self.z_current = self.particle_im.currentIndex
        self.pTextEdit.clear()
        self.pTextEdit.appendPlainText('z =' + str(self.z_current))

    def z_up(self):
        z_current = self.z_current
        if z_current < self.z_max-1:
            z_current += 1
        else:
            z_current == self.z_max
        self.z_current = z_current
        self.label.setPixmap(QPixmap(self.fileNames[self.z_current]))
        self.pTextEdit.clear()
        self.pTextEdit.appendPlainText('z =' + str(self.z_current))

    def z_down(self):
        z_current = self.z_current
        if z_current > 0:
            z_current -= 1
        else:
            z_current == 0
        self.z_current = z_current
        self.label.setPixmap(QPixmap(self.fileNames[self.z_current]))
        self.pTextEdit.clear()
        self.pTextEdit.appendPlainText('z =' + str(self.z_current))

    def mouseMoveEvent(self,event):
        # self.label_mouse = QLabel(self)
        self.label_mouse.setText('x = %d y = %d '% (event.x(), event.y()))
        # self.label_mouse.setText('x = %d y = %d z = %d)'% (event.x(), event.y(), self.z_current))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.z_current = self.particle_im.currentIndex
            self.pTEdit_points.appendPlainText('circle drawn x = %d y = %d z = %d '% (event.x(), event.y(),self.z_current))
            self.point_list.append((event.x(),event.y()))


    def deletePoints(self):
        pointsRemove = self.point_list[-1]
        self.point_list = np.delete(self.point_list,-1,axis=0)
        self.pTEdit_points.clear()
        if len(self.point_list)>0:
            for i in range(len(self.point_list)):
                xx = self.point_list[:,0]
                yy = self.point_list[:,1]
                self.pTEdit_points.appendPlainText('x = %d y = %d '% (xx[i],yy[i]))
        self.point_list = list(self.point_list)
        ### How to avoid quit if press too many times 'erase'?

    def showCircleCoor(self):
        self.pTEdit_circleCenter.setText()

    def leastsq_circle(self):
        points = np.array(self.point_list)
        x = points[:,0]
        y = points[:,1]
        x_m = np.mean(x)
        y_m = np.mean(y)
        center_estimate = x_m, y_m
        center, ier = optimize.leastsq(self.f, center_estimate, args=(x,y))
        xc, yc = center
        Ri = self.calc_R(x, y, *center)
        R = Ri.mean()
        residu = np.sum((Ri - R)**2)
        self.pTEdit_points.clear()
        self.pTEdit_circleCenter.clear()
        self.pTEdit_circleCenter.appendPlainText('x = %0.1f y = %0.1f z = %0.1f r = %0.1f '% (xc,yc,self.z_current, R))
        ### save both points and the circle

    def calc_R(self,x,y, xc, yc):
        """ calculate the distance of each 2D points from the center (xc, yc) """
        return np.sqrt((x-xc)**2 + (y-yc)**2)

    def f(self,c, x, y):
        """ calculate the algebraic distance between the data points and the mean circle centered at c=(xc, yc) """
        Ri = self.calc_R(x, y, *c)
        return Ri - Ri.mean()


    # def draw(self):
    #     scatters = pg.ScatterPlotItem()
    #     scatters.setData(np.random.random(100), np.random.random(100))
    #     self.canvas.addItem(scatters)
    #     self.notify("plotting")
    #
    # def clear(self):
    #     self.canvas.clear()
    #     self.warning("clearing")

    @staticmethod
    def notify(msg):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(msg)
        msg_box.exec_()

    @staticmethod
    def warning(msg):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText(msg)
        msg_box.exec_()
