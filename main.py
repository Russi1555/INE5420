from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtCore import Qt
from wireframe import wireframe
import re
import sys
from collections.abc import Callable

class WindowInput(QMainWindow):    
    '''
    Janela secundário para input do novo objeto renderizavel
    '''
    submitClicked = QtCore.pyqtSignal(tuple) #Sinal para transferência de dados entre janelas do PyQt
    def __init__(self, parent = None):
        super().__init__()
        super().__init__(parent)
        self.nome = ""
        self.coords = ""
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
        '''
        emite os valores introduzidos nas caixas de texto para serem recebidos pela janela principal
        '''
        print ([self.nome.text(),self.coords.text()])
        self.submitClicked.emit((self.nome.text(), self.coords.text()))
        self.close()

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
        self.setStyleSheet("background-color: light grey")
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
            Invoca a janela de input.
            """
            global report
            self.WindowInput()
            #nome, _ = QtWidgets.QInputDialog.getText(self, 'Nome do poligono','Digite um nome para o poligono: ')
            #coords, _ = QtWidgets.QInputDialog.getText(self, 'Coordenadas do poligono','Digite as coordenadas do poligono: ')
            # Transform number pairs into a list of lists
           # coords = [(int(x), int(y)) for x, y in re.findall(r'\((\d+),(\d+)\)', coords)]
            
            #self.objetos[nome]: wireframe = wireframe(nome,coords, False)
            #self.objetos[nome].update_viewport(self.viewport.x(), self.viewport.y(), self.viewport.width(), self.viewport.height(), self.window_width, self.window_height)
            #self.update()

        self.lista_objetos = QtWidgets.QListWidget(self)
        self.lista_objetos.setGeometry(10,55,180,200)
        
        # Botao de novo objeto
        self.New_button("Novo Objeto", 50,20,100,30, novo_objeto)

        # Botoes direcionais
        self.New_button("↑", 75,185,30,30, self.incrementa_translacao_vertical, (-10))
        self.New_button("←", 45,200,30,30, self.incrementa_translacao_horizontal, (-10))
        self.New_button("→", 105,200,30,30, self.incrementa_translacao_horizontal, (10))
        self.New_button("↓", 75,215,30,30, self.incrementa_translacao_vertical, (10))

        # Botao de etica e encolhe
        self.New_button(">", 55,260,30,30, self.estica, (1.5))
        self.New_button("<", 95,260,30,30, self.estica, (1/1.5))

        # Botao de giro
        self.New_button("O", 75,320,30,30, self.girar, (30))
    
    def WindowInput(self):                                             # <===
        self.w = WindowInput()
        self.w.submitClicked.connect(self.instanciarNovoObjeto) #Quando recebe o sinal submitClicked, passa a mensagem como parametro para InstanciarNovoObjeto
        self.w.show()

    def instanciarNovoObjeto(self, pacote_n_c):
        nome = pacote_n_c[0]
        coords =  pacote_n_c[1]
        self.lista_objetos.addItem(str(nome))
        if nome =="" or coords == "":
            print("VALORES INVALIDOS")
        else:
            coords = [(int(x), int(y)) for x, y in re.findall(r'\((\d+),(\d+)\)', coords)]
                
            self.objetos[nome]: wireframe = wireframe(nome,coords, False)
            self.objetos[nome].update_viewport(self.viewport.x(), self.viewport.y(), self.viewport.width(), self.viewport.height(), self.window_width, self.window_height)
            self.update()

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
        qp.setPen(QtGui.QPen(Qt.black, 1))
        qp.setBrush(QtGui.QBrush(Qt.white, Qt.SolidPattern))
        qp.drawRect(self.viewport.x(),self.viewport.y(),self.viewport.width(),self.viewport.height())
        
        # Itera sobre os wireframes
        for nome, objeto in self.objetos.items():
            qp.setPen(QtGui.QPen(Qt.red,4))
            last_point = None
            last_point_sees_next = False

            # Desenha as linhas do objeto
            for i, (point, sees_next) in enumerate(objeto.points):
                if not i:
                    last_point = point
                    last_point_sees_next = sees_next
                    continue
                if last_point_sees_next: qp.drawLine(last_point, point)
                last_point = point
                last_point_sees_next = sees_next
            # qp.setPen(QtGui.QPen(Qt.blue,4))
            # for point in objeto.outersec_points:
            #     qp.drawPoint(point)
            
            # Desenha os pontos de intersecao 
            # qp.setPen(QtGui.QPen(Qt.yellow,4))
            # for point in objeto.intersec_points:
            #     qp.drawPoint(point)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
