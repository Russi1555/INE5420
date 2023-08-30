"""
Modulo com as primitivas graficas.
"""

from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QColor
import numpy as np
from math import sin, cos, radians

def line_intersection(line1, line2, paint = False):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if not div: return None, None

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div

    # TODO: Descobrir a tolerancia ideal
    tol: float = 10e-5

    if not paint:
        l1r, l1l = min(line1[0][0],line1[1][0])-tol, max(line1[0][0],line1[1][0])+tol
        l1t, l1b = min(line1[0][1],line1[1][1])-tol, max(line1[0][1],line1[1][1])+tol
        l2r, l2l = min(line2[0][0],line2[1][0])-tol, max(line2[0][0],line2[1][0])+tol
        l2t, l2b = min(line2[0][1],line2[1][1])-tol, max(line2[0][1],line2[1][1])+tol
        if not (l1r <= x <= l1l) or not (l1t <= y <= l1b) or not (l2r <= x <= l2l) or not (l2t <= y <= l2b): 
            
            return None, None
    return x, y

def unit_vector(vector):
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

def distancia_eucl(ponto1, ponto2):
    return ((ponto1[0]-ponto2[0])**2 + (ponto1[1]-ponto2[1])**2) ** (1/2)

class Wireframe:
    def __init__(self, label: str, coord_list: list[tuple[int]], closed: bool = False, color = QColor) -> None:
        """Construtor

        Args:
            label (str): Nome da primitiva grafica.
            coord_list (list[tuple[int]]): Lista de pontos da primitiva.
            closed (bool): Se o ponto final deve ser ligado ao ponto inicial ou nao.
            color (QColor): Cor do objeto
        """

        self.label: str = label
        self.coord_world: list[tuple[int]] = coord_list if not closed else coord_list + [coord_list[0]]
        self.coord_view: list[tuple[int]] = None
        self.intersec_points: list = None
        # self.outersec_points: list = None
        self.center_point: tuple = np.array([sum(map(lambda e: e[0], coord_list))/len(coord_list), sum(map(lambda e: e[1], coord_list))/len(coord_list)])
        self.clipped_points: list = None
        self.closed: bool = closed
        self.xvw: int = None
        self.yvw: int = None
        self.widthvw: int = None
        self.heigthvw: int = None
        self.widthwin: int = None
        self.heigthwin: int = None
        self.selecionado: bool = False
        self.color: QColor = color #Vermelho como valor padrão
    
    def points(self, world_view = False):
        self.render_to_view(world_view)
        return self.clipped_points

    def render_to_view(self, world_view = False):
        """
        Atualiza a forma com que o objeto deve ser renderizado pela viewport.
        """

        self.coord_view = []
        self.intersec_points = []
        self.clipped_points = []
        # self.outersec_points = []

        if world_view:
            for (x, y) in self.coord_world:
                self.coord_view.append((self.xvw + (x  * (self.widthvw/self.widthwin)), self.yvw + (y  * (self.heigthvw/self.heigthwin))))

        else:
            # Muda as coordenadas para viewport
            for (x, y) in self.window.to_window_coords(self.coord_world):
                self.coord_view.append((self.xvw + ((1+x)  * (self.widthvw/2)), self.yvw + ((1+y)  * (self.heigthvw/2))))

        # Linhas que compoe a viewport
        vpSE, vpSD, vpID, vpIE = (self.xvw,self.yvw), (self.xvw+self.widthvw,self.yvw), (self.xvw+self.widthvw,self.yvw+self.heigthvw), (self.xvw,self.yvw+self.heigthvw)
        vplinhas = [(vpSE, vpSD), (vpSD, vpID), (vpID, vpIE), (vpIE, vpSE)]
        
        last_point = None
        for i, (x, y) in enumerate(self.coord_view):
            if not i:
                last_point = (x,y)
                continue
            # Coloca o ponto da iteracao anterior como um dos pontos candidatos a renderizacao
            linha = ((x,y),last_point)
            self.clipped_points.append({"coord": last_point, "visible": self.point_in_viewport(last_point), "sees": None})
            
            my_intersec = []
            # Determina os pontos de intersecao entre a linha e a viewport
            for vplinha in vplinhas:
                xi, yi = line_intersection(linha, vplinha)
                if not xi is None:
                    self.intersec_points.append(QPointF(xi,yi))
                    my_intersec.append((xi,yi))
            
            # Coloca os pontos de intersecao na lista de candidatos a renderizacao
            my_intersec.sort(key=lambda e: distancia_eucl(e, (x,y)))
            for p in my_intersec:
                self.clipped_points.append({"coord": p, "visible": True, "sees": None})
            
            last_point = (x,y)
        
        # Coloca o ultimo ponto na lista de candidatos a renderizacao
        self.clipped_points.append({"coord": last_point, "visible": self.point_in_viewport(last_point), "sees": None})

        # Determina se um ponto deve ou nao conectar no proximo (se o proximo ponto na lista eh visivel ou nao)
        for i, point in enumerate(self.clipped_points):
            if i == len(self.clipped_points) - 1: break

            # So conecta se o proximo ponto for de fato visivel
            self.clipped_points[i]["sees"] = self.clipped_points[i+1]["visible"]

        # Filtra pontos invisiveis
        self.clipped_points = list(filter(lambda e: e["visible"], self.clipped_points))

        # Gera os pontos objeto finais
        self.clipped_points = list(map(lambda e: (QPointF(*e["coord"]), e["sees"]), self.clipped_points))

    def center_transformation(self, transformation, center: tuple[int] = (None, None)):
        """
        Recebe uma transformacao e coloca o centro do mundo no centro do objeto para a mesma

        Args:
            transformation (matriz): matriz transormacao. 
        """
        x = 0 if None in center else -center[0]+self.center_point[0]
        y = 0 if None in center else -center[1]+self.center_point[1]
        trans = np.array([[1,0,0],
                        [0,1,0],
                        [x-self.center_point[0], y-self.center_point[1], 1]])
        trans = np.matmul(trans, transformation)
        return np.matmul(trans, np.array([[1,0,0],[0,1,0],[-x+self.center_point[0], -y+self.center_point[1], 1]]))

    def translade(self, x_increment: int, y_increment: int):
        """
        Desloca o objeto.

        Args:
            x_increment (int): deslocamento x.
            y_increment (int): deslocamento y.
        """
        self.transform([np.array([[1,0,0],[0,1,0],[x_increment, y_increment, 1]])])
    
    def stretch(self, x_factor: int, y_factor: int, center: tuple[int] = (None, None)):
        """
        Estica o objeto

        Args:
            x_factor (int): fator de mult no eixo x.
            y_factor (int): fator de mult no eixo x.
        """

        matrix = np.array([[x_factor,0,0],[0,y_factor,0],[0,0,1]])
        self.transform([self.center_transformation(matrix, center=center)])
    
    def rotate(self, angle: float, center: tuple[int] = (None, None)):
        """
        Rotates the object by an angle.

        Args:
            angle (float): angle to be rotated.
        """
        
        matrix = np.array([[cos(radians(angle)), -sin(radians(angle)), 0], [sin(radians(angle)), cos(radians(angle)), 0], [0,0,1]])
        self.transform([self.center_transformation(matrix, center=center)])

    def update_viewport(self, xvw: int, yvw: int, widthvw: int, heigthvw: int, widthwin: int, heigthwin: int) -> None:
        """
        Atualiza as informacao da viewport para qual o objeto será renderizado.

        Args:
            xvw (int): coordenada x da viewport.
            yvw (int): coordenada y da viewport.
            widthvw (int): largura da viewport.
            heigthvw (int): altura da viewport.
            widthwin (int): largura da janela.
            heigthwin (int): altura da janela.
        """
        self.xvw: int = xvw
        self.yvw: int = yvw
        self.widthvw: int = widthvw
        self.heigthvw: int = heigthvw
        self.widthwin: int = widthwin
        self.heigthwin: int = heigthwin

    def update_window(self, window):
        self.window = window

    def transform(self, transform_list: list):
        """
        Transforms the objects

        Args:
            transform_list (list): list of numpy matrixes
        """

        # Junta todas as tranformacoes numa unica matriz
        matrix = transform_list[0]
        for i, trans in enumerate(transform_list):
            if not i: continue
            matrix = np.matmul(matrix, trans)
        
        # Aplica as trasformacoes
        for i, (x, y) in enumerate(self.coord_world):
            vector = np.array([x,y,1])
            vector = vector.dot(matrix)
            self.coord_world[i] = (vector[0], vector[1])

        self.center_point: tuple = np.array([sum(map(lambda e: e[0], self.coord_world))/len(self.coord_world), sum(map(lambda e: e[1], self.coord_world))/len(self.coord_world)])
    
    def point_in_viewport(self, point: tuple[int]):
        return self.xvw <= point[0] <= self.xvw+self.widthvw and self.yvw <= point[1] <= self.yvw+self.heigthvw

class ViewWindow(Wireframe):
    def __init__(self, x0: float, y0: float, width: float, heigth: float) -> None:
        self.SE = (x0, y0)
        self.SD = (x0+width, y0)
        self.ID = (x0+width, y0+heigth)
        self.IE = (x0, y0+heigth)
        self.width = width
        self.heigth = heigth
        self.angle = 0
        super().__init__("window", [self.SE, self.SD, self.ID, self.IE], True, QColor)
        self.desloc = np.array([[1,0,0],[0,1,0],[-self.center_point[0],-self.center_point[1],1]])
        self.rot = np.array([[cos(radians(self.angle)), -sin(radians(self.angle)), 0], [sin(radians(self.angle)), cos(radians(self.angle)), 0], [0,0,1]])
        self.stret = np.array([[2/(self.width),0,0],[0,2/(self.heigth),0],[0,0,1]])    
    
    def to_window_coords(self, points: list):
        points = list(map(lambda p: np.array((*p, 1)), points))
        matrix = np.matmul(self.desloc, self.rot)
        matrix = np.matmul(matrix, self.stret)
        new_points = list(map(lambda vec: vec.dot(matrix), points))
        new_points = list(map(lambda p: (p[0], p[1]), new_points))
        return new_points

    def stretch(self, x_factor: int, y_factor: int, center: tuple[int] = (None, None)):
        super().stretch(x_factor, y_factor, center)
        self.width *= x_factor
        self.heigth *= y_factor
        self.stret = np.array([[2/(self.width),0,0],[0,2/(self.heigth),0],[0,0,1]])
    
    def rotate(self, angle: float, center: tuple[int] = (None, None)):
        super().rotate(angle, center)
        self.angle += angle
        self.rot = np.array([[cos(radians(self.angle)), -sin(radians(self.angle)), 0], [sin(radians(self.angle)), cos(radians(self.angle)), 0], [0,0,1]])
    
    def transform(self, transform_list: list):
        super().transform(transform_list)
        self.desloc = np.array([[1,0,0],[0,1,0],[-self.center_point[0],-self.center_point[1],1]])
        
    