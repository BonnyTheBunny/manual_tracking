#!/usr/bin/env python
import sys
sys.path.append('src')
sys.path.append('ui')
from control import main
from PyQt5 import QtWidgets


if __name__ == '__main__':
    ezdata = QtWidgets.QApplication(sys.argv)
    main_window = main.Main()
    main_window.show()
    sys.exit(ezdata.exec_())
