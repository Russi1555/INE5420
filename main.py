from PyQt5 import QtGui
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtCore import Qt
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Trabalho 1.1"
        self.top= 150
        self.left= 150
        self.objetos = {}
        self.width = 1200
        self.height = 800
        self.InitWindow()

    def InitWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.setStyleSheet("background-color: grey")
        self.UiComponents()
        self.show()
    
    def UiComponents(self):
        b_novo_objeto = QPushButton("Novo Objeto", self)
        b_novo_objeto.setGeometry(50,50,100,100)
        b_novo_objeto.setStyleSheet("background-color: white")
        b_novo_objeto.clicked.connect(self.novo_objeto)

    def novo_objeto(self):
        self.wnewobject = Registro_Novo_Obj()
        self.wnewobject.show()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setPen(QtGui.QPen(Qt.green, 8))
        qp.drawRect(300,15,885,585)


class Ui_ChildWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(300, 130)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 30, 71, 16))
        self.label.setObjectName("label")

        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(20, 60, 71, 16))
        self.label_2.setObjectName("label_2")

        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(20, 80, 300, 16))
        self.label_3.setText("obs: Coordenadas em formato x1,y1 x2,y2...")

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(20, 100, 251, 23))
        self.pushButton.setObjectName("pushButton")

        self.tipo = QtWidgets.QComboBox(self.centralwidget)
        self.tipo.addItem("")
        self.tipo.addItem("Ponto")
        self.tipo.addItem("Reta")
        self.tipo.addItem("Poligono")
        self.tipo.setGeometry(QtCore.QRect(100, 30, 171, 20))
        self.tipo.setObjectName("Tipo")

        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(100, 60, 171, 20))
        self.lineEdit_2.setObjectName("Coordenadas")       

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("Novo Objeto")
        self.label.setText("Tipo")
        self.label_2.setText("Coordenadas")
        self.pushButton.setText("Criar")

class Registro_Novo_Obj(QtWidgets.QMainWindow, Ui_ChildWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.PrintInput)

    def PrintInput(self):
        print ([self.tipo.itemText(self.tipo.currentIndex()),self.lineEdit_2.text()])
        self.close()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
