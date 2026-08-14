from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt
import sys

class Picture:
if __name__ == "__main__":
    app = QApplication(sys.argv)
 
    window = QDialog()
    window.resize(400, 300)
    window.setWindowFlag(window.windowFlags() | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowMaximizeButtonHint)
    #弹出窗口
    def show_msg():
        QMessageBox.information(window, "信息提示", "你点击了我")
 
    hbox = QHBoxLayout()
    button = QPushButton("点击我")
    button.clicked.connect(show_msg)
 
    hbox.addWidget(button)
    window.setLayout(hbox)
#展示窗口
    window.showMaximized()
 
    sys.exit(app.exec())