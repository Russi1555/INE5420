from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtCore import Qt
from wireframe import wireframe
import re
import sys

report = True

class MainWindow(QMainWindow):
    """
    Janela principal do programa.
    """
    def __init__(self):
        """
        Construtor, seta os elementos principais da janela.
        """
        super().__init__()
        self.title = "Trabalho 1.1"
        self.setWindowTitle(self.title)

        self.top= 150
        self.left= 150
        self.window_width = 1200
        self.window_height = 800
        self.setGeometry(self.top, self.left, self.window_width, self.window_height)
        
        self.objetos = {}
        self.setStyleSheet("background-color: grey")
        self.UiComponents()
        self.show()
    
    def UiComponents(self):
        """
        Inicia os componentes padroes da janela principal.
        """
        self.viewport = QtWidgets.QLabel()
        self.viewport.setGeometry(QtCore.QRect(200,10,990,600))

        # Cria o botar que gera novos objetos
        def novo_objeto():
            """
            Funcao de leitura do botao de novo objeto.
            """
            global report
            nome, _ = QtWidgets.QInputDialog.getText(self, 'Nome do poligono','Digite um nome para o poligono: ')
            coords, _ = QtWidgets.QInputDialog.getText(self, 'Coordenadas do poligono','Digite as coordenadas do poligono: ')
            # Transform number pairs into a list of lists
            coords = [(int(x), int(y)) for x, y in re.findall(r'\((\d+),(\d+)\)', coords)]
            
            if report: print(nome,coords)
            self.objetos[nome] = (wireframe(nome,coords))
            if report: print(self.objetos[nome])
            self.update()
        
        botao_novo_objeto = QPushButton("Novo Objeto", self)
        botao_novo_objeto.setGeometry(50,50,100,100)
        botao_novo_objeto.setStyleSheet("background-color: white")
        botao_novo_objeto.clicked.connect(novo_objeto)

    def paintEvent(self, event):
        """
        Eu nao tenho certeza de quando exatamente isso aqui eh chamado.
        """
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setPen(QtGui.QPen(Qt.green, 8))
        qp.drawRect(self.viewport.x(),self.viewport.y(),self.viewport.width(),self.viewport.height())
        qp.setPen(QtGui.QPen(Qt.red,4))
        for nome in self.objetos:
            #é bunda mas vou fazer a transformação de viewport sempre que for desenhar por enquanto só pra testar
            x1, y1 = self.objetos[nome].coords[0][0], self.objetos[nome].coords[0][1]
            x2, y2 = self.objetos[nome].coords[1][0],self.objetos[nome].coords[1][1]
            xv1 = self.viewport.x() + (x1  * (self.viewport.width()/self.window_width))
            yv1 = self.viewport.y() + (y1 * (self.viewport.height()/self.window_height))
            xv2 = self.viewport.x() + (x2 * (self.viewport.width()/self.window_width))
            yv2 = self.viewport.y() + (y2 * (self.viewport.height()/self.window_height))


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
