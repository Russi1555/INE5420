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
            self.objetos[nome]: wireframe = wireframe(nome,coords, True)
            self.objetos[nome].update_viewport(self.viewport.x(), self.viewport.y(), self.viewport.width(), self.viewport.height(), self.window_width, self.window_height)
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
        # Desenha o retangulo verde da viewport
        qp.setPen(QtGui.QPen(Qt.green, 1))
        qp.drawRect(self.viewport.x(),self.viewport.y(),self.viewport.width(),self.viewport.height())
        
        qp.setPen(QtGui.QPen(Qt.red,4))
        for nome, objeto in self.objetos.items():
            #é bunda mas vou fazer a transformação de viewport sempre que for desenhar por enquanto só pra testar

            last_point = None
            for i, point in enumerate(objeto.points()):
                if not i: 
                    last_point = point
                    continue
                qp.drawLine(last_point, point)
                last_point = point

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
