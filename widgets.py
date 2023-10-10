"""
Modulo com especializacoes de alguns widgets usados no projeto.
"""

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow, QCheckBox

class WindowInput(QMainWindow):    
    '''
    Janela secundaria para input do novo objeto renderizavel
    '''
    submitClicked = QtCore.pyqtSignal(tuple) #Sinal para transferência de dados entre janelas do PyQt
    def __init__(self, parent = None):
        super().__init__(parent)
        self.nome = ""
        self.coords = ""
        self.setupUi(self)
        self.pushButton.clicked.connect(self.PrintInput)

    def setupUi(self, MainWindow):
        
        def plain_text(text: str, dim: tuple):
            widget = QtWidgets.QLabel(self.centralwidget)
            widget.setGeometry(QtCore.QRect(*dim))
            widget.setObjectName(text)
            widget.setText(text)

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(320, 220)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Texto puro da janela
        plain_text("Nome", (20, 30, 71, 16))
        plain_text("Coordenadas", (20, 60, 91, 16))
        plain_text("obs: Coordenadas em formato (x1,y1) (x2,y2)...", (20, 80, 300, 16))
        plain_text("Cor:  R:           G:             B:", (20,100,200,16))
        plain_text("Poligono fechado? ",(20, 120, 200, 17))
        plain_text("Poligono preenchido? ",(20, 140, 200, 17))
        plain_text("Objeto Curvado?",(20,160,200,17))

        # Leitores da cor
        self.r = QtWidgets.QLineEdit(self.centralwidget)
        self.r.setGeometry(QtCore.QRect(66,100,30,16))
        self.r.setObjectName("R")

        self.g = QtWidgets.QLineEdit(self.centralwidget)
        self.g.setGeometry(QtCore.QRect(126,100,30,16))
        self.g.setObjectName("G")

        self.b = QtWidgets.QLineEdit(self.centralwidget)
        self.b.setGeometry(QtCore.QRect(186,100,30,16))
        self.b.setObjectName("B")

        # Botao de criar objeto
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(20, 190, 251, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("Criar")

        # Leitor do nome
        self.nome = QtWidgets.QLineEdit(self.centralwidget)
        self.nome.setGeometry(QtCore.QRect(110, 30, 181, 20))
        self.nome.setObjectName("Nome")

        # Leitor das coordenadas
        self.coords = QtWidgets.QLineEdit(self.centralwidget)
        self.coords.setGeometry(QtCore.QRect(110, 60, 181, 20))
        self.coords.setObjectName("Coordenadas")       

        # Checbox de check poligon
        self.close_polygon = QCheckBox(self.centralwidget)
        self.close_polygon.setGeometry(170, 120, 15, 15)
        self.close_polygon.setToolTip("Marque essa caixa para fechar o poligono (ex: transformar 2 linhas em um triangulo)")

        # Checbox de check filled
        self.filled_polygon = QCheckBox(self.centralwidget)
        self.filled_polygon.setGeometry(170, 140, 200, 17)
        self.filled_polygon.setToolTip("Marque essa caixa para preencher o poligono com a cor escolhida")

        # Checbox de Curved2D
        self.curvado = QCheckBox(self.centralwidget)
        self.curvado.setGeometry(170, 160, 200, 17)
        self.curvado.setToolTip("Marque essa caixa para que as coordenadas sejam interpretadas como objeto curvado")

        # Dados sobre a Janela
        MainWindow.setCentralWidget(self.centralwidget)
        MainWindow.setWindowTitle("Novo Objeto")
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def PrintInput(self):
        '''
        emite os valores introduzidos nas caixas de texto para serem recebidos pela janela principal
        '''
        self.submitClicked.emit((self.nome.text(), self.coords.text(), int(self.close_polygon.checkState()) == 2, [self.r.text(),self.g.text(),self.b.text()],int(self.filled_polygon.checkState()) == 2, int(self.curvado.checkState()) == 2))
        self.close()

class ListWidget(QtWidgets.QListWidget, QMainWindow):
    """
    Widget especializado para a listagem de objetos no canvas.
    Responsavel por determinar que objetos estao selecionados.
    """
    def __init__(self, mainwindow):
        super().__init__(mainwindow)
        self.mainwindow = mainwindow

    def clicked(self, item):
        self.mainwindow.objetos[str(item.text())].selecionado = not self.mainwindow.objetos[str(item.text())].selecionado
        self.mainwindow.update()

