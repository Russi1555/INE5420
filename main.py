from PyQt5 import QtGui
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtCore import Qt, QTimer
from wireframe import wireframe
import re
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Trabalho 1.1"
        self.top= 150
        self.left= 150
        self.objetos = {}
        self.x_translacao = 0
        self.y_translacao = 0
        self.rotacao = 0
        self.width = 1200
        self.height = 800
        self.InitWindow()
        

    def InitWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.setStyleSheet("background-color: grey")
        self.UiComponents()
        self.show()
    
    def incrementa_translacao_horizontal(self, value):
            self.x_translacao += value
            self.update()
            
    def incrementa_translacao_vertical(self, value):
            self.y_translacao += value
            self.update()

    def UiComponents(self):


        self.viewport = QtWidgets.QLabel()
        self.viewport.setGeometry(QtCore.QRect(200,10,990,600))

        b_novo_objeto = QPushButton("Novo Objeto", self)
        b_novo_objeto.setGeometry(50,50,100,100)
        b_novo_objeto.setStyleSheet("background-color: white")
        b_novo_objeto.clicked.connect(self.novo_objeto)

        b_translacao_cima = QPushButton("↑", self)
        b_translacao_cima.setGeometry(75,185,30,30)
        b_translacao_cima.setStyleSheet("background-color: white")
        b_translacao_cima.clicked.connect(lambda: self.incrementa_translacao_vertical(-10))
        
        
        b_translacao_esquerda = QPushButton("←",self)
        b_translacao_esquerda.setGeometry(45,200,30,30)
        b_translacao_esquerda.setStyleSheet("background-color: white")
        b_translacao_esquerda.clicked.connect(lambda: self.incrementa_translacao_horizontal(-10))

        b_translacao_direita = QPushButton("→",self)
        b_translacao_direita.setGeometry(105,200,30,30)
        b_translacao_direita.setStyleSheet("background-color: white")
        b_translacao_direita.clicked.connect(lambda: self.incrementa_translacao_horizontal(10))

        print(self.x_translacao)
        b_translacao_baixo = QPushButton("↓",self)
        b_translacao_baixo.setGeometry(75,215,30,30)
        b_translacao_baixo.setStyleSheet("background-color: white")
        b_translacao_baixo.clicked.connect(lambda: self.incrementa_translacao_vertical(10))

    def novo_objeto(self):
        nome,coords = self.take_inputs()
        print(nome,coords)
        self.objetos[nome] = (wireframe(nome,coords))
        print(self.objetos[nome])



    def take_inputs(self):
        nome,inserido1 = QtWidgets.QInputDialog.getText(self, 'Nome do poligono','Digite um nome para o poligono: ')
        coords,inserido2 = QtWidgets.QInputDialog.getText(self, 'Coordenadas do poligono','Digite as coordenadas do poligono: ')
        number_pairs = re.findall(r'\((\d+),(\d+)\)', coords)
        # Transform number pairs into a list of lists
        coords = [[int(x), int(y)] for x, y in number_pairs]
        return([nome, coords])

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setPen(QtGui.QPen(Qt.green, 8))
        qp.drawRect(self.viewport.x(),self.viewport.y(),self.viewport.width(),self.viewport.height())
        qp.setPen(QtGui.QPen(Qt.red,4))
        for nome in self.objetos:
            #é bunda mas vou fazer a transformação de viewport sempre que for desenhar por enquanto só pra testar
            x1, y1 = self.objetos[nome].coords[0][0] + self.x_translacao, self.objetos[nome].coords[0][1] + self.y_translacao
            x2, y2 = self.objetos[nome].coords[1][0] + self.x_translacao,self.objetos[nome].coords[1][1] + self.y_translacao
            xv1 = self.viewport.x() + (x1  * (self.viewport.width()/self.width))
            yv1 = self.viewport.y() + (y1 * (self.viewport.height()/self.height))
            xv2 = self.viewport.x() + (x2 * (self.viewport.width()/self.width))
            yv2 = self.viewport.y() + (y2 * (self.viewport.height()/self.height))


            print(xv1,yv1, xv2, yv2)
            p1 = QtCore.QPointF(xv1,yv1)
            p2 = QtCore.QPointF(xv2,yv2)
            qp.drawLine(p1,p2)


class Registro_Novo_Obj(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.PrintInput)

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
        self.label_3.setText("obs: Coordenadas em formato (x1,y1) (x2,y2)...")

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(20, 100, 251, 23))
        self.pushButton.setObjectName("pushButton")

        self.nome = QtWidgets.QLineEdit(self.centralwidget)
        self.nome.setGeometry(QtCore.QRect(100, 30, 171, 20))
        self.nome.setObjectName("Nome")

        self.coords = QtWidgets.QLineEdit(self.centralwidget)
        self.coords.setGeometry(QtCore.QRect(100, 60, 171, 20))
        self.coords.setObjectName("Coordenadas")       

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("Novo Objeto")
        self.label.setText("Nome")
        self.label_2.setText("Coordenadas")
        self.pushButton.setText("Criar")

    def PrintInput(self):
        print ([self.nome.text(),self.coords.text()])
        self.close()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
