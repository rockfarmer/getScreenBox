#!/usr/bin/python
#-*- coding:UTF-8 -*-
__author__ = 'zhaoxu'

from PySide.QtCore import *
from PySide.QtGui import *

QTextCodec.setCodecForTr(QTextCodec.codecForName("utf8"))


class GetScreenBox(QWidget):
    def __init__(self, parent=None):
        super(GetScreenBox, self).__init__(parent)
        self.is_save = False
        self.screen = QPixmap(QPixmap.grabWindow(QApplication.desktop().winId()))
        self.tmp_screen = QPixmap(self.screen)
        self.start_pos = None
        self.end_pos = None
        self.initUI()
        self.setCursor(Qt.CrossCursor)

    def initUI(self):
        close_action = QAction('close_win', self)
        close_action. setShortcut(QKeySequence(Qt.Key_Escape))
        self.connect(close_action, SIGNAL('triggered()'), self.close)

        self.addAction(close_action)

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Window)
        self.setGeometry(0, 0,
                         QApplication.desktop().width(),
                         QApplication.desktop().height())

    def showEvent(self, event):
        self.showFullScreen()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.tmp_screen)

    def mousePressEvent(self, event):
        self.start_pos = event.pos()

    def mouseMoveEvent(self, event):
        self.end_pos = event.pos()

        self.tmp_screen = QPixmap(self.screen)
        self.paint(self.tmp_screen)

    def mouseReleaseEvent(self, event):
        self.end_pos = event.pos()
        points_list = self.getKeyPoints()

        if points_list:
            self.win = FloatBox(points_list=points_list)
            self.win.show()

        self.close()

    def paint(self, pixmap):
        painter = QPainter(pixmap)
        painter.drawRect(QRect(self.start_pos, self.end_pos))
        self.update()

    def getKeyPoints(self):
        # [left_top_point, right_down_point]

        if self.start_pos.x() == self.end_pos.x() or self.start_pos.y() == self.end_pos.y():
            self.close()
            return

        max_x = self.start_pos.x() if self.start_pos.x() > self.end_pos.x() else self.end_pos.x()
        min_x = self.start_pos.x() if self.start_pos.x() < self.end_pos.x() else self.end_pos.x()

        max_y = self.start_pos.y() if self.start_pos.y() > self.end_pos.y() else self.end_pos.y()
        min_y = self.start_pos.y() if self.start_pos.y() < self.end_pos.y() else self.end_pos.y()

        return [QPoint(min_x, min_y), QPoint(max_x, max_y)]


class FloatBox(QLabel):
    def __init__(self, parent=None, points_list=[]):
        super(FloatBox, self).__init__(parent)
        self.diff_x = 0
        self.diff_y = 0
        self.is_double = False
        self.min_scale = 50
        self.ratio = 0.2
        self.box_width = points_list[1].x() - points_list[0].x()
        self.box_height = points_list[1].y() - points_list[0].y()
        self.points_list = points_list

        self.start_pos = None
        self.end_pos = None

        self.screen = QPixmap.grabWindow(QApplication.desktop().winId(),
                                         points_list[0].x()+1, points_list[0].y()+1,
                                         self.box_width, self.box_height)
        self.initUI()

    def initUI(self):
        close_action = QAction('close_win', self)
        close_action.setShortcut(QKeySequence(Qt.Key_Escape))
        self.connect(close_action, SIGNAL('triggered()'), self.close)
        close_action.setText('Close')

        bigger_action = QAction('bigger', self)
        bigger_action.setShortcut(QKeySequence(Qt.Key_Plus))
        self.connect(bigger_action, SIGNAL('triggered()'), self.bigger)
        bigger_action.setText('Zoom in')

        bigger2_action = QAction('bigger2', self)
        bigger2_action.setShortcut(QKeySequence(Qt.Key_Equal))
        self.connect(bigger2_action, SIGNAL('triggered()'), self.bigger)
        bigger2_action.setText('Zoom in')

        smaller_action = QAction('smaller', self)
        smaller_action.setShortcut(QKeySequence(Qt.Key_Minus))
        self.connect(smaller_action, SIGNAL('triggered()'), self.smaller)
        smaller_action.setText('Zoom out')

        save_action = QAction('save', self)
        save_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_S))
        self.connect(save_action, SIGNAL('triggered()'), self.saveScreenBox)
        save_action.setText('Save as')

        copy_action = QAction('copy', self)
        copy_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_C))
        self.connect(copy_action, SIGNAL('triggered()'), self.copyScreenBox)
        copy_action.setText('Copy')

        self.setContextMenuPolicy(Qt.ActionsContextMenu)

        self.addAction(copy_action)
        self.addAction(save_action)
        self.addAction(bigger_action)
        self.addAction(bigger2_action)
        self.addAction(smaller_action)
        self.addAction(close_action)

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        self.setPixmap(self.screen)
        self.setScaledContents(True)

        self.setFrameShape(QFrame.Box)
        self.setStyleSheet("border: 1px solid #000000")
        self.setGeometry(self.points_list[0].x()+1, self.points_list[0].y()+1,
                         self.box_width, self.box_height)

    def bigger(self):
        w = self.width() + self.width() * self.ratio
        h = self.height() + self.height() * self.ratio

        if w > QApplication.desktop().width() or h > QApplication.desktop().height():
            return

        self.setFixedSize(w, h)

    def smaller(self):
        w = self.width() - self.width() * self.ratio
        h = self.height() - self.height() * self.ratio

        if w < self.min_scale or h < self.min_scale:
            return

        self.setFixedSize(w, h)

    def saveScreenBox(self):
        format = 'png'
        initial_path = QDir.currentPath() + "/untitled." + format

        file_name, _ = QFileDialog.getSaveFileName(self, "Save As",
                                                   initial_path,
                                                   "%s Files (*.%s);;All Files (*)" % (format.upper(), format))
        if file_name:
            self.screen.save(file_name, format)

    def copyScreenBox(self):
        QApplication.clipboard().setImage(self.screen.copy(0, 0, self.box_width, self.box_height).toImage())

    def mousePressEvent(self, event):
        self.start_pos = QCursor.pos()

    def mouseMoveEvent(self, event):
        self.end_pos = QCursor.pos()
        new_pos = self.end_pos - self.start_pos
        self.move(self.pos().x()+new_pos.x(), self.pos().y()+new_pos.y())
        self.start_pos = QCursor.pos()

    def mouseDoubleClickEvent(self, event):
        scale = self.min_scale
        if not self.is_double:
            self.box_width = self.width()
            self.box_height = self.height()

            self.diff_x = self.x() - QCursor.pos().x()
            self.diff_y = self.y() - QCursor.pos().y()

            self.setFixedSize(scale, scale)
            self.move(QCursor.pos().x()-scale/2.0, QCursor.pos().y()-scale/2.0)
            self.is_double = True
        else:
            self.setFixedSize(self.box_width, self.box_height)
            self.move(self.diff_x+QCursor.pos().x(), self.diff_y+QCursor.pos().y())
            self.is_double = False

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    win = GetScreenBox()
    win.show()
    sys.exit(app.exec_())
