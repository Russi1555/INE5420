from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QCheckBox, QSlider
from PyQt5.QtCore import Qt
from primitivas2D import *
from primitivas3D import *
from DescritorOBJ import DescritorOBJ
import re
import sys
from collections.abc import Callable
from widgets import ListWidget, WindowInput
from math import degrees, radians, inf

def round_vec(vec):
    return list(map(lambda e: round(e, 2), vec))

class MainWindow(QMainWindow):
    """
    Janela principal do programa.
    """ 
    def __init__(self):
        """
        Construtor, seta os elementos principais da janela.
        """
        super().__init__()
        self.title = "Trabalho 1.7"
        self.setWindowTitle(self.title)

        self.top= 150
        self.left= 150
        self.window_width = 1200
        self.window_height = 800
        self.setGeometry(self.top, self.left, self.window_width, self.window_height)

        # transformacoes da window
        self.viewer_window = ViewWindow3D(-50,-30,99,60)
        self.viewer_window.translade(0,0,-self.viewer_window.dist_focal)
        self.update()

        self.fake_window = Objeto3D("fake window", [(-50,-30,0),(50,-30,0),(50,30,0),(-50,30,0),(-50,-30,0)], QColor(0,0,0))
        muito = 100000
        self.yaxis = Objeto3D("y", [(0,muito,0),(0,-muito,0)], QColor(0,255,0))
        self.xaxis = Objeto3D("x", [(muito,0,0),(-muito,0,0)], QColor(255,0,0))
        self.zaxis = Objeto3D("z", [(0, 0,muito),(0,0,-muito)], QColor(0,0,255))
        self.default_objects = [self.yaxis, self.xaxis, self.zaxis, self.fake_window]
        
        # transformation quantities
        self.tqt: float = 0 #translation
        self.sqt: float = 0 #stretch
        self.rqt: float = 0 #rotation

        # center point for rotation
        self.center_x = None
        self.center_y = None

        self.stdobjcount = 0

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
    
    @property
    def rotation_axis(self):
        """
        Getter do eixo de rotacao
        """
        try:
            return [[float(self.axisAx.text()), float(self.axisAy.text()), float(self.axisAz.text())],
                    [float(self.axisBx.text()), float(self.axisBy.text()), float(self.axisBz.text())],
            ]
        except ValueError:
            return ((None, None, None), (None, None, None))

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
            objetos = self.descritor.load_objs()
            for nome, obj in objetos.items():
                novo_obj = obj["type"](obj["name"], obj["points"], obj["color"])
                self.objetos[nome] = novo_obj
                self.objetos[nome].update_viewport(self.viewport.x(), self.viewport.y(), self.viewport.width(), self.viewport.height())
                self.objetos[nome].update_window(self.viewer_window)
                self.lista_objetos.addItem(str(nome))
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

        def line_edit(x: int, y: int, w: int, h: int, text: str = None, text_width: int = None, def_value: str = None):
            if not text is None:
                label = QtWidgets.QLabel(self)
                label.setGeometry(int(x-text_width), y+5, int(text_width), 20)
                label.setText(f"{text}: ")
            le = QtWidgets.QLineEdit(def_value,self)  
            le.setGeometry(x,y,w,h)
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
        
        def slider(min,max,step,x,y,width,heigth):
            widget = QSlider(self)
            widget.setGeometry(x,y,width,heigth)
            widget.setMinimum(min)
            widget.setMaximum(max)
            widget.setSingleStep(step)
            widget.valueChanged.connect(self.update)
            return widget

        # Gera o objeto viewport
        self.viewport = QtWidgets.QLabel()
        self.viewport.setGeometry(QtCore.QRect(200,10,990,600))
        self.viewer_window.update_viewport(self.viewport.x(), self.viewport.y(), self.viewport.width(), self.viewport.height())
        self.world_viewer = ViewWindow3D(-495,-300,990,600)
        self.world_viewer.update_viewport(self.viewport.x(), self.viewport.y(), self.viewport.width(), self.viewport.height())

        self.lista_objetos = ListWidget(self)
        self.lista_objetos.setGeometry(10,55,180,200)
        self.lista_objetos.itemClicked.connect(self.lista_objetos.clicked)
        
        # Botao de novo objeto
        button("Novo Objeto", 50,20,100,30, novo_botao)
        
        # Bota de salvar objetos
        # button("Salvar Objetos",30,265,130,30, salvar_objetos )

        # # Bota de carregar objetos
        # button("Carregar Objetos",30,305,130,30, carregar_objetos )
        
        # Ancoras dos botoes
        atx, aty = 45, 350
        
        # Botoes direcionais
        self.tqt = line_edit(atx + 100, aty + 15, 30,30, def_value="1",text_width=1)
        button("↑", atx+30,aty,30,30, self.translacao, ("cim",))
        button("←", atx,aty+15,30,30, self.translacao, ("esq",))
        button("→", atx+60,aty+15,30,30, self.translacao, ("dir",))
        button("↓", atx+30,aty+30,30,30, self.translacao, ("bax",))
        button("↗", atx+60,aty-6,20,20, self.translacao, ("frn",))
        button("↙", atx+10,aty+45,20,20, self.translacao, ("trz",))

        # Botao de estica e encolhe
        self.sqt = line_edit(atx + 100, aty + 75, 30,30, def_value="1.5", text_width=1)
        button("□", atx+10,aty+75,30,30, self.estica, (1))
        button("▫", atx+50,aty+75,30,30, self.estica, (-1))

        # Botao de giro
        self.rqt = line_edit(atx + 100, aty + 120, 30, 30, def_value="15", text_width=1)
        button("↻", atx+30,aty+120,30,30, self.girar, ())
        self.axisAx = line_edit(atx+10, aty + 170, 30,30, text_width=1, def_value="-10")
        self.axisAy = line_edit(atx+40, aty + 170, 30,30, text_width=1, def_value="0")
        self.axisAz = line_edit(atx+70, aty + 170, 30,30, text_width=1, def_value="0")

        self.axisBx = line_edit(atx+10, aty + 224, 30,30, text_width=1, def_value="-10")
        self.axisBy = line_edit(atx+40, aty + 224, 30,30, text_width=1, def_value="10")
        self.axisBz = line_edit(atx+70, aty + 224, 30,30, text_width=1, def_value="0")
        label = QtWidgets.QLabel(self)
        label.setGeometry(atx-25, aty+170, 40, 30)
        label.setText(f"Eixo:")

        self.own_axis = check_box(atx+90, aty+206, 15,15, text="Eixo próprio", text_width=81)

        # Botao de giro
        # button("Ajustar aos Objetos", atx+410,aty+290,130,30, self.snap, ())
        # self.DDDtqt = line_edit(atx + 365, aty + 290, 30,30, def_value="1",text_width=1)
        button("3D ↻ X", atx+155,aty+290,60,30, self.girar_x3D, ())
        button("3D ↻ Y", atx+225,aty+290,60,30, self.girar_y3D, ())
        button("3D ↻ Z", atx+295,aty+290,60,30, self.girar_z3D, ())

        # Centro de transformação
        # self.center_x = line_edit(atx, aty + 195, 30, 30, text="X", text_width=15)
        # self.center_y = line_edit(atx + 60, aty + 195, 30, 30, text="Y", text_width=15)

        # Checkbox de visao de mundo
        # self.world_view_check_box = check_box(atx + 105, aty + 235, 15,15, "Visao de Mundo", 105)

        # Slider de Clipping
        self.slider_clip = slider(1, 3, 1, atx - 50, aty + 270, 105, 60)
        self.slider_label_1 = QtWidgets.QLabel(self)
        self.slider_label_1.setText("Clipping C")
        self.slider_label_1.setGeometry(atx + 40, aty + 312, 145, 20)

        self.slider_label_1 = QtWidgets.QLabel(self)
        self.slider_label_1.setText("Clipping LB")
        self.slider_label_1.setGeometry(atx + 40, aty + 288, 145, 20)

        self.slider_label_1 = QtWidgets.QLabel(self)
        self.slider_label_1.setText("No Clipping")
        self.slider_label_1.setGeometry(atx + 40, aty + 265, 145, 20)

        # Slider de Clipping curvas
        # self.slider_clip_curvas = slider(1, 3, 1, atx + 170, aty + 270, 105, 60)
        # self.slider_label_1 = QtWidgets.QLabel(self)
        # self.slider_label_1.setText("Completo")
        # self.slider_label_1.setGeometry(atx + 240, aty + 312, 145, 20)

        # self.slider_label_1 = QtWidgets.QLabel(self)
        # self.slider_label_1.setText("Parcial")
        # self.slider_label_1.setGeometry(atx + 240, aty + 288, 145, 20)

        # self.slider_label_1 = QtWidgets.QLabel(self)
        # self.slider_label_1.setText("Sem clipping de curvas")
        # self.slider_label_1.setGeometry(atx + 240, aty + 265, 145, 20)

        self.lista_objetos.addItem("fake window")
        self.objetos["fake window"] = self.fake_window
        self.update()

    def instanciarNovoObjeto(self, pacote_n_c):
        nome, coords, cor, object_type, closed = pacote_n_c
        if nome == "":
            nome = f"objeto_{self.stdobjcount}"
            self.stdobjcount += 1
        coords = list(map(lambda p: tuple(map(lambda v: float(v), p[1:-1].split(","))), coords.split()))
        if cor[0] == cor[1] == cor[2] == "":
            cor = QtGui.QColor(255,0,0)
        else:
            cor = list(map(lambda e: 0 if e == "" else min(int(e),255), cor))
            cor = QtGui.QColor(cor[0],cor[1],cor[2])
        if coords == "" or object_type == Curved2D and (len(coords)-4) % 3:
            print("VALORES INVALIDOS")
        else:
            self.lista_objetos.addItem(str(nome))
            if closed:
                self.objetos[nome] = Wireframe(nome,coords, cor, True)
            else:
                self.objetos[nome] = object_type(nome, coords, cor)
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

        args = (tqt if dir == "dir" else -tqt if dir == "esq" else 0, 
                tqt if dir == "bax" else -tqt if dir == "cim" else 0,
                tqt if dir == "frn" else -tqt if dir == "trz" else 0,
                )

        algum_selecionado = any(list(map(lambda o: o.selecionado, self.objetos.values())))
        if not algum_selecionado:
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
        algum_selecionado = any(list(map(lambda o: o.selecionado, self.objetos.values())))
        if not algum_selecionado:
            self.viewer_window.stretch(value, value, value)
        else:
            for objeto in self.objetos.values():
                if not objeto.selecionado: continue
                objeto.stretch(value, value, value)
        self.update()

    def rotation_matrix(self, angle, eixo):
        head = np.array(eixo[1]+[1])
        step_1 = np.array([[1,0,0,0],
                            [0,1,0,0],
                            [0,0,1,0],
                            [-eixo[0][0],-eixo[0][1],-eixo[0][2],1]])
        head = np.matmul(head, step_1)

        ang_x = angle_between_vec(np.array([0, 1]), np.array([head[2],head[1]]))
        
        step_2 = np.array([[1, 0, 0, 0],
                           [0, cos(ang_x), sin(ang_x), 0],
                           [0, -sin(ang_x), cos(ang_x), 0],
                           [0, 0, 0, 1]])
        head = np.matmul(head, step_2)

        ang_z = angle_between_vec(np.array([0,1]), np.array([head[0],head[1]]))

        step_3 = np.array([[cos(ang_z),sin(ang_z),0,0],
                           [-sin(ang_z),cos(ang_z),0,0],
                           [0,0,1,0],
                           [0,0,0,1]])
        
        step_4 = np.array([[cos(angle),0,-sin(angle),0],
                           [0,1,0,0],
                           [sin(angle),0,cos(angle),0],
                           [0,0,0,1]])

        step_5 = np.array([[cos(-ang_z),sin(-ang_z),0,0],
                           [-sin(-ang_z),cos(-ang_z),0,0],
                           [0,0,1,0],
                           [0,0,0,1]])
        
        step_6 = np.array([[1, 0, 0, 0],
                           [0, cos(-ang_x), sin(-ang_x), 0],
                           [0, -sin(-ang_x), cos(-ang_x), 0],
                           [0, 0, 0, 1]])

        step_7 = np.array([[1,0,0,0],
                           [0,1,0,0],
                           [0,0,1,0],
                           [eixo[0][0],eixo[0][1],eixo[0][2],1]])

        return reduce(np.matmul, [step_1, step_2, step_3, step_4, step_5, step_6, step_7])

    def girar(self, eixo = None):
        if eixo is None:
            eixo = self.rotation_axis
        algum_selecionado = any(list(map(lambda o: o.selecionado, self.objetos.values())))
        matrix = self.rotation_matrix(radians(float(self.rqt.text())),eixo)
        
        if algum_selecionado:
            for objeto in self.objetos.values():
                if objeto.selecionado:
                # print(int(self.own_axis.checkState()), int(self.own_axis.checkState()) == 2)
                    objeto.rotate(matrix, None if int(self.own_axis.checkState()) != 2 else eixo)
        else:
            self.viewer_window.rotate(matrix)
        self.update()

    def girar_x3D(self):
        self.girar([[0,0,0],[1,0,0]])
    
    def girar_y3D(self):
        self.girar([[0,0,0],[0,1,0]])
    
    def girar_z3D(self):
        self.girar([[0,0,0],[0,0,1]])

    def snap(self):
        wx, wy = self.viewer_window.coord_world[0][0], self.viewer_window.coord_world[0][1]
        ww, wh = self.viewer_window.coord_world[2][0]-wx, self.viewer_window.coord_world[3][1]-wy
        cx, cy = wx + ww/2, wy+wh/2

        icx = (self.limiares[0]+self.limiares[1])/2
        icy = (self.limiares[2]+self.limiares[3])/2
        iw = (self.limiares[1]-self.limiares[0]) * 1.1
        ih = (self.limiares[3]-self.limiares[2]) * 1.1
        self.viewer_window.translade(icx-cx, icy-cy)
        self.viewer_window.stretch(max(iw/ww, ih/wh), max(iw/ww, ih/wh))
        self.update()
    
    def paintEvent(self, _):
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
        valor_clip = int(self.slider_clip.value())
        # valor_clip_curva = int(self.slider_clip_curvas.value())
        valor_clip_curva = 1
        # world_view: bool = int(self.world_view_check_box.checkState()) == 2
        world_view = False
        used_window = self.world_viewer if world_view else self.viewer_window
        
        # Renderiza o centro de transformacoes quando necessario
        # if None not in self.center_point:
        #     qp.setPen(QtGui.QPen(Qt.black, 4))
        #     cx, cy = used_window.to_window_coords([self.center_point])[0]
        #     center_in_view = (self.viewport.x() + ((cx+1)*self.viewport.width()/2), self.viewport.y() + (cy+1)*(self.viewport.height()/2))
        #     qp.drawPoint(QtCore.QPointF(*center_in_view))
        #     self.update()
        
        for obj in self.default_objects:
            obj.update_window(self.viewer_window)
            obj.update_viewport(self.viewport.x(), self.viewport.y(), self.viewport.width(), self.viewport.height())
        
        # Renderiza o eixo de rotacoes quando necessario
        if None not in self.rotation_axis[0] and None not in self.rotation_axis[1]:
            self.objetos["eixo"] = Objeto3D("axis", self.rotation_axis, Qt.black)
            self.objetos["eixo"].update_window(self.viewer_window)
            self.objetos["eixo"].update_viewport(self.viewport.x(), self.viewport.y(), self.viewport.width(), self.viewport.height())
            self.update()

        # Inclui a window como um objeto a ser renderizado caso nao estejamos vendo o mundo de sua perspectiva
        objetos = {} if not world_view else {"window": self.viewer_window}
        objetos.update(self.objetos)
        objetos["x"] = self.xaxis
        objetos["y"] = self.yaxis
        objetos["z"] = self.zaxis
        objetos["fake window"] = self.fake_window
        
        # Itera sobre os Wireframes renderizando-os        
        self.limiares = [10000000, -10000000, 10000000, -1000000]
        for nome, objeto in objetos.items():
            
            objeto.update_window(used_window)
            
            # Determina qual a cor e grossura da caneta
            if nome == "window": qp.setPen(QtGui.QPen(Qt.black,2))
            elif objeto.selecionado: qp.setPen(QtGui.QPen(objeto.color,4))
            else: qp.setPen(QtGui.QPen(objeto.color,1))
            
            # Wireframe_filled/Polygon precisa ter outra rotina de renderizacao por ser preenchido
            if type(objeto) == Wireframe_filled:
                qp.setBrush(QtGui.QBrush(objeto.color))
                linhas, limiares = objeto.render_to_view(valor_clip, limiar_points=[])
                if linhas != [[]]:
                    qp.drawPolygon(QtGui.QPolygonF(list(map(lambda l: l[0], linhas))))
                
                # Renderiza a borda preta de quando o polygon eh selecionado
                if self.objetos[nome].selecionado:
                    qp.setPen(QtGui.QPen(Qt.black,4))
                    linhas , _ = objeto.render_to_view(valor_clip, limiar_points=[])
                    for linha in linhas:
                        if linha != []: qp.drawLine(*linha)

            else:
                # Renderizacao de wireframes e curvas de bezier normais
                linhas, limiares = objeto.render_to_view(valor_clip if type(objeto) == Wireframe else valor_clip_curva, limiar_points=[])
                for linha in linhas:
                    qp.drawLine(*linha)
            
            # Calcula os limites que a window deveria ter para que todos os objetos coubessem na tela
            if nome not in {"window", "eixo"} and len(limiares) == 4:
                self.limiares[0] = min(self.limiares[0], limiares[0])
                self.limiares[1] = max(self.limiares[1], limiares[1])
                self.limiares[2] = min(self.limiares[2], limiares[2])
                self.limiares[3] = max(self.limiares[3], limiares[3])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())