from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QCheckBox
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
        MainWindow.resize(300, 130)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Texto puro da janela
        plain_text("Nome", (20, 30, 71, 16))
        plain_text("Coordenadas", (20, 60, 71, 16))
        plain_text("obs: Coordenadas em formato (x1,y1) (x2,y2)...", (20, 80, 300, 16))

        # Botao de criar objeto
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(20, 100, 251, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("Criar")

        # Leitor do nome
        self.nome = QtWidgets.QLineEdit(self.centralwidget)
        self.nome.setGeometry(QtCore.QRect(100, 30, 171, 20))
        self.nome.setObjectName("Nome")

        # Leitor das coordenadas
        self.coords = QtWidgets.QLineEdit(self.centralwidget)
        self.coords.setGeometry(QtCore.QRect(100, 60, 171, 20))
        self.coords.setObjectName("Coordenadas")       

        # Checbox de check poligon
        self.close_polygon = QCheckBox(self.centralwidget)
        self.close_polygon.setGeometry(275, 63, 15, 15)

        # Dados sobre a Janela
        MainWindow.setCentralWidget(self.centralwidget)
        MainWindow.setWindowTitle("Novo Objeto")
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def PrintInput(self):
        '''
        emite os valores introduzidos nas caixas de texto para serem recebidos pela janela principal
        '''
        # print (self.nome.text(), self.coords.text(), self.close_polygon.checkState())
        self.submitClicked.emit((self.nome.text(), self.coords.text(), int(self.close_polygon.checkState()) == 2))
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
        
        #transformation quantities
        self.tqt: float = 0 #translation
        self.sqt: float = 0 #stretch
        self.rqt: float = 0 #rotation

        #center point for rotation
        self.center_x = None
        self.center_y = None
        
        self.objetos = {}
        self.setStyleSheet("background-color: light grey")
        self.UiComponents()
        self.show()
    
    @property
    def center_point(self):
        """
        Getter do ponto central
        """
        return (None if self.center_x.text() == "" else float(self.center_x.text()), None if self.center_y.text() == "" else float(self.center_y.text()))

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
            self.WindowInput()
            #nome, _ = QtWidgets.QInputDialog.getText(self, 'Nome do poligono','Digite um nome para o poligono: ')
            #coords, _ = QtWidgets.QInputDialog.getText(self, 'Coordenadas do poligono','Digite as coordenadas do poligono: ')
            # Transform number pairs into a list of lists
           # coords = [(int(x), int(y)) for x, y in re.findall(r'\((\d+),(\d+)\)', coords)]
            
            #self.objetos[nome]: wireframe = wireframe(nome,coords, False)
            #self.objetos[nome].update_viewport(self.viewport.x(), self.viewport.y(), self.viewport.width(), self.viewport.height(), self.window_width, self.window_height)
            #self.update()

        self.lista_objetos = ListWidget(self)
        self.lista_objetos.setGeometry(10,55,180,200)
        x = self.lista_objetos.itemClicked.connect(self.lista_objetos.clicked)
        # Botao de novo objeto
        self.New_button("Novo Objeto", 50,20,100,30, novo_objeto)

        # Botoes direcionais
        atx,aty = 45,300
        self.tqt = QtWidgets.QLineEdit(self) #quantidade pra mexer
        self.tqt.setGeometry(atx + 100, aty + 15, 30,30)
        
        self.New_button("↑", atx+30,aty,30,30, self.translacao, ("cim",))
        self.New_button("←", atx,aty+15,30,30, self.translacao, ("esq",))
        self.New_button("→", atx+60,aty+15,30,30, self.translacao, ("dir",))
        self.New_button("↓", atx+30,aty+30,30,30, self.translacao, ("bax",))

        # Botao de estica e encolhe
        self.sqt = QtWidgets.QLineEdit(self)
        self.sqt.setGeometry(atx + 100, aty + 75, 30,30)
        self.New_button("□", atx+10,aty+75,30,30, self.estica, (1))
        self.New_button("▫", atx+50,aty+75,30,30, self.estica, (-1))

        # Botao de giro
        self.rqt = QtWidgets.QLineEdit(self)
        self.rqt.setGeometry(atx + 100, aty + 120, 30,30)
        self.New_button("↻", atx+30,aty+120,30,30, self.girar, ())

        # Centro de transformação
        label_center_x = QtWidgets.QLabel(self)
        label_center_x.setGeometry(atx - 15, aty +185, 15, 10)
        label_center_x.setText("X: ")
        self.center_x = QtWidgets.QLineEdit(self)
        self.center_x.setGeometry(atx, aty + 175, 30,30)

        label_center_y = QtWidgets.QLabel(self)
        label_center_y.setGeometry(atx +45, aty +185, 15, 10)
        label_center_y.setText("Y: ")
        self.center_y = QtWidgets.QLineEdit(self)
        self.center_y.setGeometry(atx + 60, aty + 175, 30,30)

        self.render_center_point = QCheckBox(self)
        self.render_center_point.setGeometry(atx + 105, aty + 180, 15,15)
 
    def WindowInput(self):
        self.w = WindowInput()
        self.w.submitClicked.connect(self.instanciarNovoObjeto) #Quando recebe o sinal submitClicked, passa a mensagem como parametro para InstanciarNovoObjeto
        self.w.show()

    def instanciarNovoObjeto(self, pacote_n_c):
        nome = pacote_n_c[0]
        coords =  pacote_n_c[1]
        close = pacote_n_c[2]
        self.lista_objetos.addItem(str(nome))

        if nome =="" or coords == "":
            print("VALORES INVALIDOS")
        else:
            coords = [(int(x), int(y)) for x, y in re.findall(r'\((\d+),(\d+)\)', coords)]
                
            self.objetos[nome]: wireframe = wireframe(nome,coords, close)
            self.objetos[nome].update_viewport(self.viewport.x(), self.viewport.y(), self.viewport.width(), self.viewport.height(), self.window_width, self.window_height)
            self.update()
            
    def translacao(self, dir: str):
        """
        Move todos os objetos na tela horizontalmente.

        Args:
            value (int): delocamento.
        """
        tqt = 0 if self.tqt.text() == '' else float(self.tqt.text())

        args = (tqt if dir == "dir" else -tqt if dir == "esq" else 0, tqt if dir == "bax" else -tqt if dir == "cim" else 0)

        for objeto in self.objetos.values():
            if not objeto.selecionado: continue
            objeto.translade(*args)
        self.update()

    def estica(self, tipo: int):
        """
        Estica todos os objetos ao redor do proprio centro.

        Args:
            value (int): Fator de estique.
            center (tuple): Centro da transformacao.
        """
        value = 1 if self.sqt.text() == '' else float(self.sqt.text()) ** tipo
        for objeto in self.objetos.values():
            if not objeto.selecionado: continue
            objeto.stretch(value, value, self.center_point)
        self.update()
    
    def girar(self):
        """
        Gira todos os objetos ao redor do proprio centro.

        Args:
            value (int): Angulo.
            center(tuple): Ponto Cental da rotacao.
        """
        angle = 0 if self.rqt.text() == '' else -float(self.rqt.text())
        for objeto in self.objetos.values():
            if not objeto.selecionado: continue
            objeto.rotate(angle, self.center_point)
        self.update()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)

        # Desenha o retangulo preto da viewport
        qp.setPen(QtGui.QPen(Qt.black, 1))
        qp.setBrush(QtGui.QBrush(Qt.white, Qt.SolidPattern))
        qp.drawRect(self.viewport.x(),self.viewport.y(),self.viewport.width(),self.viewport.height())
        
        # Renderiza o centro de transformacoes caso ele exista e esteja selecionado
        if int(self.render_center_point.checkState()) == 2 and None not in self.center_point:
            qp.setPen(QtGui.QPen(Qt.black, 4))
            cx, cy = self.center_point[0], self.center_point[1]
            center_in_view = (self.viewport.x() + (cx  * (self.viewport.width()/self.window_width)), self.viewport.y() + (cy  * (self.viewport.height()/self.window_height)))
            qp.drawPoint(QtCore.QPointF(*center_in_view))
            self.update()

        # Itera sobre os wireframes renderizando-os
        for nome, objeto in self.objetos.items():
            if self.objetos[nome].selecionado:
                qp.setPen(QtGui.QPen(Qt.red,4))
            else:
                qp.setPen(QtGui.QPen(Qt.red,1))
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
