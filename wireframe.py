"""
Modulo com as primitivas graficas.
"""

from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QColor
import numpy as np
from math import sin, cos, radians, pi

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
        self.selecionado: bool = False
        self.color: QColor = color #Vermelho como valor padrão
    
    def window2view(self, point: tuple) -> tuple:
        """
        Converte os pontos da coordenada de window para viwport

        Args:
            point (tuple): ponto (x,y)

        Returns:
            tuple: ponto (x,y)
        """

        x, y = point

        return (self.xvw + ((1+x)  * (self.widthvw/2)), self.yvw + ((1+y)  * (self.heigthvw/2)))
    
    def points(self, world_view = False):
        self.render_to_view(world_view)
        return self.clipped_points

    def lines(self, world_view = False):
        """
        Retorna as linhas do poligono

        Args:
            world_view (bool, optional): Se a renderizacao sera referente ao mundo. Defaults to False.
        """

        lines = self.render_to_view(world_view)
        return lines
    
    def clip_CS(self, line: list, window: list = [(-1,-1),(-1,1),(1,1),(1,-1)]):
        """
        Recebe uma lista de pontos e os clippa

        Args:
            points (list): Lista de pontos que formam o poligono a ser clippado
            window (list, optional): Lista dos quatro pontos que formam a window (A clippagem eh feita)
        """
        wxmin, wxmax = min(map(lambda e: e[0], window)), max(map(lambda e: e[0], window))
        wymin, wymax = min(map(lambda e: e[1], window)), max(map(lambda e: e[1], window))

        enumESQ, enumDIR, enumBAX, enumCIM = 1, 2, 4, 8
        
        def in_window(point: tuple):
            return wxmin <= point[0] <= wxmax and wymin <= point[1] <= wymax


        # Gera o valor de CS para cada ponto
        CS = {point: 0 for point in line}
        for (x,y) in line:
            if x < wxmin: CS[(x,y)] += enumESQ
            elif x > wxmax: CS[(x,y)] += enumDIR
            if y < wymin: CS[(x,y)] += enumBAX
            elif y > wymax: CS[(x,y)] += enumCIM

        # Guardas para casos triviais
        if not CS[line[0]] and not CS[line[1]]: return line
        elif CS[line[0]] & CS[line[1]]: return None
        
        def clip(point, outro):
            if not CS[point]: return point
            x, y = outro
            # coef_a = (y-y0)/(x-x0)
            (x0, y0), (x1, y1) = line
            if x0 != x1:
                ESQ = (wxmin, (y1-y0)/(x1-x0) * (wxmin - x) + y)
                if CS[point] & enumESQ and in_window(ESQ): return ESQ
                DIR = (wxmax, (y1-y0)/(x1-x0) * (wxmax - x) + y)
                if CS[point] & enumDIR and in_window(DIR): return DIR
            if y0 != y1:
                BAX = (x + (x1-x0)/(y1-y0) * (wymin - y), wymin)
                if CS[point] & enumBAX and in_window(BAX): return BAX
                CIM = (x + (x1-x0)/(y1-y0) * (wymax - y), wymax)
                if CS[point] & enumCIM and in_window(CIM): return CIM
            return None

        return (clip(line[0], line[1]), clip(line[1], line[0]))
    
    def clip_LB(self, line: list, window: list = [(-1,-1),(-1,1),(1,1),(1,-1)]):
        
        xmin, xmax = min(map(lambda e: e[0], window)), max(map(lambda e: e[0], window))
        ymin, ymax = min(map(lambda e: e[1], window)), max(map(lambda e: e[1], window))
        l1 = line[0]
        x1 = l1[0]
        y1 = l1[1]
        l2 = line[1]
        x2 = l2[0]
        y2 = l2[1]
        dx = x2 - x1
        dy = y2 - y1
        u1 = 0.0
        u2 = 1.0
        p = [-dx ,dx, -dy, dy]
        q = [x1-xmin, xmax - x1, y1-ymin, ymax - y1]
        r = [ q[0]/p[0], q[1]/p[1], q[2]/p[2], q[3]/p[3]]
        #param1 = max(0,r[0],r[1],r[2],r[3])
        #param2 = min(1,r[0],r[1],r[2],r[3])
        i = 0
        f_d = [0]
        d_f = [1]
        for val in r:
            if p[i]<0:
                f_d.append(val)
            elif p[i]> 0:
                d_f.append(val)
            else:
                if q[i] <0:
                    if abs(val)==float("inf"):
                        return None, None
            i+=1
        
        param1 = max(f_d)
        param2 = min(d_f)   

        ret_1 = (x1,y1)
        ret_2 = (x2,y2)

        if param1 > param2:
            return None, None
        if param1 != 0:
            ret_1 = (x1+param1*(dx), y1+param1*(dy))
        if param2 != 1:
            ret_2 = (x1+param2*(dx), y1+param2*(dy))
        

        return ret_1, ret_2


    def linearize(self, points: list) -> list:
        """Dada uma lista de pontos ordenados devolve todas as linhas que os ligam

        Args:
            points (list): lista de pontos

        Returns:
            list: lista de linhas no formato ((x0,y0), (x1,y1))
        """
        lines: list = []
        for i, point in enumerate(points):
            if i == len(points) - 1: break
            line = (point, points[i+1])
            lines.append(line)
        return lines
          
    def render_to_view(self, world_view = False):
        """
        Atualiza a forma com que o objeto deve ser renderizado pela viewport.
        """

        points = self.window.to_window_coords(self.coord_world)
        # Clipa todos os pontos linearizados
        lines = list(map(lambda line: self.clip_CS(line), self.linearize(points)))
        # Filtra linhas nulas
        lines = list(filter(lambda line: line is not None and line[0] is not None and line[1] is not None, lines))
        # Transforma as linhas em objetos renderizaveis
        lines = list(map(lambda line: (tuple(map(lambda p: QPointF(*self.window2view(p)), line))), lines))
        
        return lines

    ######### METODOS DE TRANSFORMACAO ########

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

    def translade(self, dx: int, dy: int):
        """
        Desloca o objeto.

        Args:
            x_increment (int): deslocamento x.
            y_increment (int): deslocamento y.
        """
        
        if not isinstance(self, ViewWindow):
            theta = radians(self.window.angle)
            dx, dy = dx * cos(theta) - dy * sin(theta), dy * cos(theta) + dx * sin(theta)
        self.transform([np.array([[1,0,0],[0,1,0],[dx, dy, 1]])])
    
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

        coords = self.coord_world if not self.closed else self.coord_world[:-1]
        self.center_point: tuple = np.array([sum(map(lambda e: e[0], coords))/len(coords), sum(map(lambda e: e[1], coords))/len(coords)])
    
    ########### METODOS DE UPDATE #######

    def update_viewport(self, xvw: int, yvw: int, widthvw: int, heigthvw: int) -> None:
        """
        Atualiza as informacao da viewport para qual o objeto será renderizado.

        Args:
            xvw (int): coordenada x da viewport.
            yvw (int): coordenada y da viewport.
            widthvw (int): largura da viewport.
            heigthvw (int): altura da viewport.
        """
        self.xvw: int = xvw
        self.yvw: int = yvw
        self.widthvw: int = widthvw
        self.heigthvw: int = heigthvw

    def update_window(self, window):
        self.window = window

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

    def translade(self, dx: int, dy: int):
        theta = radians(self.angle)
        ndx = dx * cos(theta) - dy * sin(theta)
        ndy = dy * cos(theta) + dx * sin(theta)
        super().translade(ndx, ndy)
    
    def stretch(self, x_factor: int, y_factor: int, center: tuple[int] = (None, None)):
        super().stretch(x_factor, y_factor, center)
        self.width *= x_factor
        self.heigth *= y_factor
        self.stret = np.array([[2/(self.width),0,0],[0,2/(self.heigth),0],[0,0,1]])
    
    def rotate(self, angle: float, center: tuple[int] = (None, None)):
        super().rotate(angle, center)
        self.angle -= angle
        self.rot = np.array([[cos(radians(self.angle)), -sin(radians(self.angle)), 0], [sin(radians(self.angle)), cos(radians(self.angle)), 0], [0,0,1]])
    
    def transform(self, transform_list: list):
        super().transform(transform_list)
        self.desloc = np.array([[1,0,0],[0,1,0],[-self.center_point[0],-self.center_point[1],1]])

    def points(self, _):
        return super().points(True)
        
class Wireframe_filled(Wireframe):
    def __init__(self, label: str, coord_list: list[tuple[int]], closed: bool = False, color = QColor, additional_data: str = "") -> None:
        super().__init__(label, coord_list, closed, color)
    def poligons(self):
        return self.render_to_view()
    
    def render_to_view(self, world_view=False):

        # Lista de poligonos a serem renderizados
        poligons: list = []

        # Sabe como eh floatin point ne, ruim comparar valores diretamente, isso aqui eh cheio de conversao
        precision = 1e-10                

        # Clipa todos os pontos de acordo com Cohen Sutherland
        points = self.window.to_window_coords(self.coord_world)
        lines = self.linearize(points)
        lines = list(map(lambda line: self.clip_CS(line), self.linearize(points)))
        lines = list(filter(lambda line: line is not None and line[0] is not None and line[1] is not None, lines))

        if lines == []: return [lines]

        # TODO poligono completamente fora da janela

        # Separa o poligonos nos poligonos menores a serem renderizados
        this_poligon = []
        for i, line in enumerate(lines):
            # Ignora a primeira linha
            if not i: continue
            # Coloca a linha atual como parte do poligono atual
            this_poligon.append(lines[i-1])
            # Implica discontinuade nas linhas, houve clipagem, separaremos ambos poligonos
            if (lines[i-1][1] != line[0]):
                poligons.append(this_poligon)
                this_poligon = []
        this_poligon.append(lines[-1])
        poligons.append(this_poligon)

        # Confere se o ultimo poligono e o primeiro sao o mesmo, se sim os une
        print("bordas: ",poligons[0][0][0], poligons[-1][-1][-1])
        if len(poligons) > 1 and poligons[0][0][0] == poligons[-1][-1][-1]:
            poligons[0] = poligons[-1] + poligons[0]
            poligons.pop()

        # Dada a lista de poligonos os completa com a borda
        print("poli: ", poligons)
        for poligon in poligons:
            ponta_inicial, ponta_final = poligon[0][0], poligon[-1][-1]
            x0, y0 = ponta_inicial
            x1, y1 = ponta_final
            # print("pontas: ", ponta_inicial, ponta_final)
            # Nao houve clipping
            if ponta_inicial == ponta_final: continue
            # Dividem uma borda, basta criar uma linha que una os pontos
            elif abs(x0-x1) < precision or abs(y0-y1) < precision:
                # print("Borda")
                poligon.append(((x1, y1), (x0, y0)))
            # Nao dividem borda :'(
            else:
                # Descobre em quina tem que conectar
                xq = 1 if abs(x0-1) < precision or abs(x1-1) < precision else -1
                yq = 1 if abs(y0-1) < precision or abs(y1-1) < precision else -1

                # Conecta o fim a quina e a quina ao inicio
                poligon.append(((x1, y1), (xq, yq)))
                poligon.append(((xq, yq), (x0, y0)))

        # Transforma todos os pontos do poligono em ponto QpointF
        poligons = list(map(lambda pol: list(map(lambda line: (tuple(map(lambda p: QPointF(*self.window2view(p)), line))), pol)), poligons))  

        return poligons
