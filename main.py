from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QCheckBox
from PyQt5.QtCore import Qt
from wireframe import Wireframe, ViewWindow, Wireframe_filled
from DescritorOBJ import DescritorOBJ
import re
import sys
from collections.abc import Callable
from widgets import ListWidget, WindowInput

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

        # transformacoes da window
        self.viewer_window = ViewWindow(200,200,330,200)
        
        # transformation quantities
        self.tqt: float = 0 #translation
        self.sqt: float = 0 #stretch
        self.rqt: float = 0 #rotation

        # center point for rotation
        self.center_x = None
        self.center_y = None

        self.descritor = DescritorOBJ()
        self.objetos = {}
        self.setStyleSheet("background-color: light grey")
        self.UiComponents()
        self.show()
    
    @property
    def center_point(self):
        """
        Getter do ponto central
        """
        try:
            return (float(self.center_x.text()), float(self.center_y.text()))
        except ValueError:
            return (None, None)
    
    def UiComponents(self):
        """
        Inicia os componentes padroes da janela principal.
        """
        def novo_botao():
            self.janela = WindowInput()
            self.janela.submitClicked.connect(self.instanciarNovoObjeto) #Quando recebe o sinal submitClicked, passa a mensagem como parametro para InstanciarNovoObjeto
            self.janela.show()

        def salvar_objetos():
            self.descritor.save_objs(self.objetos)

        def carregar_objetos():
            self.objetos = dict()
            self.lista_objetos.clear()
            novos_obs = self.descritor.load_objs()
            for key in novos_obs:
                # print(novos_obs[key])
                obj = novos_obs[key]
                novo_obj = Wireframe(obj[0],obj[1],obj[2],obj[3])
                self.objetos[key] = novo_obj
                self.objetos[key].update_viewport(self.viewport.x(), self.viewport.y(), self.viewport.width(), self.viewport.height())
                self.objetos[key].update_window(self.viewer_window)
                self.lista_objetos.addItem(str(key))
            self.update()

        def button(label: str, x: int, y: int, w: int, h: int, func: Callable, args: list or None = None) -> QPushButton:
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

        def line_edit(x: int, y: int, w: int, h: int, text: str = None, text_width: int = None):
            if not text is None:
                label = QtWidgets.QLabel(self)
                label.setGeometry(int(x-text_width), y+5, int(text_width), 20)
                label.setText(f"{text}: ")
            le = QtWidgets.QLineEdit(self)
            le.setGeometry(x, y, w,h)
            le.setStyleSheet("QLineEdit""{""border: 1px solid;""border-color: black""}")
            return le

        def check_box(x: int, y: int, w: int, h: int, text: str = None, text_width: int = None):
            if not text is None:
                label = QtWidgets.QLabel(self)
                label.setGeometry(int(x-text_width), y-5, int(text_width), 20)
                label.setText(f"{text}: ")
            
            check_box = QCheckBox(self)
            check_box.setGeometry(x,y,w,h)
            check_box.stateChanged.connect(self.update)
            return check_box

        # Gera o objeto viewport
        self.viewport = QtWidgets.QLabel()
        self.viewport.setGeometry(QtCore.QRect(200,10,990,600))
        self.viewer_window.update_viewport(self.viewport.x(), self.viewport.y(), self.viewport.width(), self.viewport.height())

        self.lista_objetos = ListWidget(self)
        self.lista_objetos.setGeometry(10,55,180,200)
        self.lista_objetos.itemClicked.connect(self.lista_objetos.clicked)
        
        # Botao de novo objeto
        button("Novo Objeto", 50,20,100,30, novo_botao)
        
        # Bota de salvar objetos
        button("Salvar Objetos",30,265,130,30, salvar_objetos )

        # Bota de carregar objetos
        button("Carregar Objetos",30,305,130,30, carregar_objetos )
        
        # Ancoras dos botoes
        atx,aty = 45,350
        
        # Botoes direcionais
        self.tqt = line_edit(atx + 100, aty + 15, 30,30)
        button("↑", atx+30,aty,30,30, self.translacao, ("cim",))
        button("←", atx,aty+15,30,30, self.translacao, ("esq",))
        button("→", atx+60,aty+15,30,30, self.translacao, ("dir",))
        button("↓", atx+30,aty+30,30,30, self.translacao, ("bax",))

        # Botao de estica e encolhe
        self.sqt = line_edit(atx + 100, aty + 75, 30,30)
        button("□", atx+10,aty+75,30,30, self.estica, (1))
        button("▫", atx+50,aty+75,30,30, self.estica, (-1))

        # Botao de giro
        self.rqt = line_edit(atx + 100, aty + 120, 30, 30)
        button("↻", atx+30,aty+120,30,30, self.girar, ())

        # Centro de transformação
        self.center_x = line_edit(atx, aty + 175, 30, 30, "X", 15)
        self.center_y = line_edit(atx + 60, aty + 175, 30, 30, "Y", 15)
        self.render_center_point = check_box(atx + 105, aty + 225, 15, 15, "Mostrar Ponto Central", 142)

        # Checkbox de visao de mundo
        self.world_view_check_box = check_box(atx + 105, aty + 250, 15,15, "Visao de Mundo", 105)
        
        # Checkbox de transformacoes em objetos
        self.transform_object_check_box = check_box(atx + 105, aty + 275, 15,15, "Transformar Objetos", 134)

        self.update()

    def instanciarNovoObjeto(self, pacote_n_c):
        nome, coords, close, cor, filled = pacote_n_c
        self.lista_objetos.addItem(str(nome))
        if cor[0]==cor[1]==cor[2] and cor[0]=="":
            cor = QtGui.QColor(255,0,0)
        else:
            cor = list(map(lambda e: 0 if e == "" else int(e), cor))
            cor = QtGui.QColor(cor[0],cor[1],cor[2])

        if nome =="" or coords == "":
            print("VALORES INVALIDOS")
        else:
            coords = list(map(lambda p: tuple(map(lambda v: float(v), p[1:-1].split(","))), coords.split()))
        
            if filled:
                self.objetos[nome]: Wireframe = Wireframe_filled(nome,coords, close,cor)
            else:
                self.objetos[nome]: Wireframe = Wireframe(nome,coords, close,cor)

            self.objetos[nome].update_viewport(self.viewport.x(), self.viewport.y(), self.viewport.width(), self.viewport.height())
            self.objetos[nome].update_window(self.viewer_window)
            self.update()
            
    def translacao(self, dir: str):
        """
        Move todos os objetos na tela horizontalmente.

        Args:
            value (int): delocamento.
        """
        tqt = 0 if self.tqt.text() == '' else float(self.tqt.text())

        args = (tqt if dir == "dir" else -tqt if dir == "esq" else 0, tqt if dir == "bax" else -tqt if dir == "cim" else 0)

        if int(self.transform_object_check_box.checkState()) == 0:
            self.viewer_window.translade(*args)
        else:
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
        if int(self.transform_object_check_box.checkState()) == 0:
            self.viewer_window.stretch(value, value)
        else:
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
        if int(self.transform_object_check_box.checkState()) == 0:
            self.viewer_window.rotate(angle)
        else:
            for objeto in self.objetos.values():
                if not objeto.selecionado: continue
                objeto.rotate(angle, self.center_point)
        self.update()

    def paintEvent(self, event):
        """
        Responsavel por renderizar os wireframes
        """
        qp = QtGui.QPainter()
        qp.begin(self)

        # Desenha o retangulo preto da viewport (Note que a viewport nao eh um objeto Canvas)
        qp.setPen(QtGui.QPen(Qt.black, 1))
        qp.setBrush(QtGui.QBrush(Qt.white, Qt.SolidPattern))
        qp.drawRect(self.viewport.x(),self.viewport.y(),self.viewport.width(),self.viewport.height())
        
        # Le as checkbox da interface
        show_cp: bool = int(self.render_center_point.checkState()) == 2
        world_view: bool = int(self.world_view_check_box.checkState()) == 2
        
        # Renderiza o centro de transformacoes quando necessario
        if show_cp and None not in self.center_point:
            qp.setPen(QtGui.QPen(Qt.black, 4))
            if world_view:
                center_in_view = (self.viewport.x() + self.center_point[0], self.viewport.y() + self.center_point[1])
            else:
                cx, cy = self.viewer_window.to_window_coords([self.center_point])[0]
                center_in_view = (self.viewport.x() + ((cx+1)*self.viewport.width()/2), self.viewport.y() + (cy+1)*(self.viewport.height()/2))
            qp.drawPoint(QtCore.QPointF(*center_in_view))
            self.update()

        # Inclui a window como um objeto a ser renderizado caso nao estejamos vendo o mundo de sua perspectiva
        objetos = {} if not world_view else {"window": self.viewer_window}
        objetos.update(self.objetos)
        
        # Itera sobre os Wireframes renderizando-os
        for nome, objeto in objetos.items():
            if nome == "window":
                qp.setPen(QtGui.QPen(Qt.black,2))
            elif self.objetos[nome].selecionado:
                qp.setPen(QtGui.QPen(self.objetos[nome].color,4))
            else:
                qp.setPen(QtGui.QPen(self.objetos[nome].color,1))
            last_point = None
            last_point_sees_next = False

            if nome != "window" and isinstance(self.objetos[nome], Wireframe_filled):
                pontos = [x for x, y in objeto.points(world_view)]
                polygon = QtGui.QPolygonF(pontos)
                fill_color = QtGui.QBrush(self.objetos[nome].color)
                qp.setBrush(fill_color)
                qp.drawPolygon(polygon)
            else:
                # Desenha as linhas do objeto
                for i, (point, sees_next) in enumerate(objeto.points(world_view)):
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