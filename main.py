from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtCore import Qt
from wireframe import wireframe
import re
import sys
from collections.abc import Callable

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
    
    def New_button(self, label: str, x: int, y: int, w: int, h: int, func: Callable, args: list or None = None) -> QPushButton:
        """
        Cria um novo botao

        Args:
            label (str): Nome.
            x (int): coordenada x.
            y (int): coordenada y.
            w (int): largura.
            h (int): altura.
            func (Callable): funcao associada ao botao.
            args (listorNone, optional): argumentos da funcao.

        Returns:
            QPushButton: The button created
        """
        
        # Caso o dev seja bobo e coloque (10) como argumento
        if args:
            try:
                iter(args)
            except TypeError:
                args = (args,)
        
        botao = QPushButton(label, self)
        botao.setGeometry(x, y, w, h) 
        botao.setStyleSheet("background-color: white")
        if args: botao.clicked.connect(lambda: func(*args))
        else: botao.clicked.connect(lambda: func())
    
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
        
        # Botao de novo objeto
        self.New_button("Novo Objeto", 50,50,100,100, novo_objeto)

        # Botoes direcionais
        self.New_button("↑", 75,185,30,30, self.incrementa_translacao_vertical, (-10))
        self.New_button("←", 45,200,30,30, self.incrementa_translacao_horizontal, (-10))
        self.New_button("→", 105,200,30,30, self.incrementa_translacao_horizontal, (10))
        self.New_button("↓", 75,215,30,30, self.incrementa_translacao_vertical, (10))

        # Botao de etica e encolhe
        self.New_button(">", 55,260,30,30, self.estica, (1.5))
        self.New_button("<", 95,260,30,30, self.estica, (-1.5))

        # Botao de giro
        self.New_button("O", 75,320,30,30, self.girar, (30))

    def incrementa_translacao_horizontal(self, value: int):
        """
        Move todos os objetos na tela horizontalmente.

        Args:
            value (int): deslocamento.
        """
        for objeto in self.objetos.values():
            objeto.translade(value, 0)
        self.update()
            
    def incrementa_translacao_vertical(self, value: int):
        """
        Move todos os objetos na tela horizontalmente.

        Args:
            value (int): delocamento.
        """
        for objeto in self.objetos.values():
            objeto.translade(0, value)
        self.update()

    def estica(self, value: int):
        """
        Estica todos os objetos ao redor do proprio centro.

        Args:
            value (int): fator de estique.
        """
        for objeto in self.objetos.values():
            objeto.stretch(value, value)
        self.update()
    
    def girar(self, angle: int):
        """
        Gira todos os objetos ao redor do proprio centro.

        Args:
            value (int): angulo
        """
        for objeto in self.objetos.values():
            objeto.rotate(angle)
        self.update()

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
