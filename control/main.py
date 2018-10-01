from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QAction, QMessageBox, QMenu, QListWidgetItem, QFileDialog, QLabel
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
from scipy import misc, optimize
from PIL import Image, ImageQt

ui_main_window, q_main_window = loadUiType("ui/load_images.ui")


class Main(q_main_window, ui_main_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.data = None
        self._setup_canvas()
        self._init_slot()
        self.point_list = []
        self.images = None
        self.z_current = 0
        self.z_max = None
        self.xy_current = None

    def _setup_canvas(self):
        self.plot = self.view.addPlot()
        self.plot.hideAxis('left')
        self.plot.hideAxis('bottom')

    def _refresh_image(self):
        self.plot.clear()
        image = pg.ImageItem()
        image.setImage(self.images[self.z_current])
        self.plot.addItem(image)

    def _get_mouse_on_canvas(self, event):
        """store the x, y positions to self.xy_current"""
        scene_pos = event.scenePos()
        plot_pos = self.plot.vb.mapSceneToView(scene_pos)
        x, y = plot_pos.x(), plot_pos.y()
        self.xy_current = (x, y)

    def _show_current_location(self, event):
        """present x, y, z positions on the Text Edit"""
        plot_pos = self.plot.vb.mapSceneToView(event.toPoint())
        x, y, z = plot_pos.x(), plot_pos.y(), self.z_current
        self.text_coordinate.clear()
        self.text_coordinate.setPlainText('{:.2f}, {:.2f}, {}'.format(x, y, z))

    def _init_slot(self):
        self.btn_load.pressed.connect(self.load_images)
        self.btn_up.pressed.connect(self.z_up)
        self.btn_down.pressed.connect(self.z_down)
        self.btn_erase.pressed.connect(self.deletePoints)
        self.btn_confirm.pressed.connect(self.leastsq_circle)
        self.view.scene().sigMouseClicked.connect(self._get_mouse_on_canvas)
        self.view.scene().sigMouseMoved.connect(self._show_current_location)

    def load_images(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.file_names, _ = QFileDialog.getOpenFileNames(None, "QFileDialog.getOpenFileName()",
                                                          "", "All Files (*);;Python Files (*.py)", options=options)
        im = np.array([np.array(Image.open(fname)) for fname in self.file_names])
        self.z_max = len(im)
        self.images = im
        self._refresh_image()

    def z_up(self):
        z_current = self.z_current
        if z_current < self.z_max - 1:
            z_current += 1
        self.z_current = z_current
        self._refresh_image()

    def z_down(self):
        z_current = self.z_current
        if z_current > 0:
            z_current -= 1
        self.z_current = z_current
        self._refresh_image()

    def deletePoints(self):
        pointsRemove = self.point_list[-1]
        self.point_list = np.delete(self.point_list, -1, axis=0)
        self.pTEdit_points.clear()
        if len(self.point_list) > 0:
            for i in range(len(self.point_list)):
                xx = self.point_list[:, 0]
                yy = self.point_list[:, 1]
                self.pTEdit_points.appendPlainText('x = %d y = %d ' % (xx[i], yy[i]))
        self.point_list = list(self.point_list)
        ### How to avoid quit if press too many times 'erase'?

    def showCircleCoor(self):
        return
        self.pTEdit_circleCenter.setText()

    def leastsq_circle(self):
        points = np.array(self.point_list)
        x = points[:, 0]
        y = points[:, 1]
        x_m = np.mean(x)
        y_m = np.mean(y)
        center_estimate = x_m, y_m
        center, ier = optimize.leastsq(self.f, center_estimate, args=(x, y))
        xc, yc = center
        Ri = self.calc_R(x, y, *center)
        R = Ri.mean()
        residu = np.sum((Ri - R) ** 2)
        self.pTEdit_points.clear()
        self.pTEdit_circleCenter.clear()
        self.pTEdit_circleCenter.appendPlainText(
            'x = %0.1f y = %0.1f z = %0.1f r = %0.1f ' % (xc, yc, self.z_current, R))
        # save both points and the circle

    def calc_R(self, x, y, xc, yc):
        """ calculate the distance of each 2D points from the center (xc, yc) """
        return np.sqrt((x - xc) ** 2 + (y - yc) ** 2)

    def f(self, c, x, y):
        """ calculate the algebraic distance between the data points and the mean circle centered at c=(xc, yc) """
        Ri = self.calc_R(x, y, *c)
        return Ri - Ri.mean()

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
