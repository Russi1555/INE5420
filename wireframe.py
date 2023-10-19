"""
Modulo com as primitivas graficas.
"""

from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QColor
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QPointF
import sys
from math import sin, cos, radians

class Wireframe:
    def __init__(self, label: str, coord_list: list[tuple[int]], closed: bool = False, color = QColor(255,0,0)) -> None:
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
    
    def __getitem__(self, key):
        return self.coord_world[key]

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
    
    def clip_CS(self, line: list):
        """
        Recebe uma lista de pontos e os clippa

        Args:
            points (list): Lista de pontos que formam o poligono a ser clippado
            window (list, optional): Lista dos quatro pontos que formam a window (A clippagem eh feita)
        """
        wxmin, wxmax = -1, 1
        wymin, wymax = -1, 1
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
    
    def clip_LB(self, line: list):
        
        xmin, xmax = -1, 1
        ymin, ymax = -1, 1
        l1 = line[0]
        x1 = l1[0]
        y1 = l1[1]
        l2 = line[1]
        x2 = l2[0]
        y2 = l2[1]
        dx = x2 - x1
        dy = y2 - y1
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
          
    def render_to_view(self, clip_key : int, points: list = None):
        """
        Atualiza a forma com que o objeto deve ser renderizado pela viewport.
        """
        if points is None: 
            points = self.window.to_window_coords(self.coord_world)
        clip = self.clip_CS if clip_key==1 else self.clip_LB if clip_key==2 else lambda e:  e
        # Clipa todos os pontos linearizados
        lines = list(map(lambda line: clip(line), self.linearize(points)))
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
    def __init__(self, label: str, coord_list: list[tuple[int]], closed: bool = False, color = QColor(255,0,0), additional_data: str = "") -> None:
        super().__init__(label, coord_list, closed, color)

    
    def render_to_view(self, clip_key = False): 
        
        clip = self.clip_CS if clip_key == 1 else self.clip_LB if clip_key==2 else lambda e:  e
        
        # Lista de poligonos a serem renderizados
        poligons: list = []

        # Sabe como eh floatin point ne, ruim comparar valores diretamente, isso aqui eh cheio de conversao
        precision = 1e-10                

        # Clipa todos os pontos de acordo com Cohen Sutherland
        points = self.window.to_window_coords(self.coord_world)
        lines = self.linearize(points)
        lines = list(map(lambda line: clip(line), self.linearize(points)))
        lines = list(filter(lambda line: line is not None and line[0] is not None and line[1] is not None, lines))

        # Poligono completamente fora
        if lines == []: return [lines]

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
        if len(poligons) > 1 and poligons[0][0][0] == poligons[-1][-1][-1]:
            poligons[0] = poligons[-1] + poligons[0]
            poligons.pop()

        final_lines = []
        # Dada a lista de poligonos une todos
        for i, poligon in enumerate(poligons):
            if not i: 
                final_lines += poligon
                continue
            ponta_inicial, ponta_final = poligon[0][0], final_lines[-1][-1]
            x0, y0 = ponta_inicial
            x1, y1 = ponta_final
            if ponta_inicial == ponta_final: continue
            # Dividem uma borda, basta criar uma linha que una os pontos
            elif abs(x0-x1) < precision or abs(y0-y1) < precision:
                # print("Borda")
                final_lines.append(((x1, y1), (x0, y0)))
            else:
                # Descobre em quina tem que conectar
                xq = 1 if abs(x0-1) < precision or abs(x1-1) < precision else -1
                yq = 1 if abs(y0-1) < precision or abs(y1-1) < precision else -1

                # Conecta o fim a quina e a quina ao inicio
                final_lines.append(((x1, y1), (xq, yq)))
                final_lines.append(((xq, yq), (x0, y0)))
            final_lines += poligon

        ponta_inicial, ponta_final = final_lines[0][0], final_lines[-1][-1]
        x0, y0 = ponta_inicial
        x1, y1 = ponta_final
        if ponta_inicial == ponta_final: 
            pass
        # Dividem uma borda, basta criar uma linha que una os pontos
        elif abs(x0-x1) < precision or abs(y0-y1) < precision:
            final_lines.append(((x1, y1), (x0, y0)))
        else:
            # Descobre em quina tem que conectar
            xq = 1 if abs(x0-1) < precision or abs(x1-1) < precision else -1
            yq = 1 if abs(y0-1) < precision or abs(y1-1) < precision else -1

            # Conecta o fim a quina e a quina ao inicio
            final_lines.append(((x1, y1), (xq, yq)))
            final_lines.append(((xq, yq), (x0, y0)))
        
        # Transforma todos os pontos do poligono em ponto QpointF
        final_lines = list(map(lambda line: (tuple(map(lambda p: QPointF(*self.window2view(p)), line))), final_lines))  

        return final_lines
    
class Bezier(Wireframe):

    def T(self, t: float):
        """
        Gera a matriz T

        Args:
            t (float): valor t (0 <= t <= 1)
        """
        return np.array([t**3, t**2, t, 1])
    
    def K(self, Gk, t: float):
        """
        Dada uma matriz arbitraria de uma das dimensoes gera o ponto da dimensao em t

        Args:
            t (float): valor t (0 <= t <= 1)
        """
        return np.matmul(np.matmul(self.T(t), self.Mb), np.transpose(Gk))

    def __init__(self, label: str, points: list, color = QColor(255,0,0)):
        """
        Construtor

        Args:
            label (str): Nome da curva de bezier
            points (list): Lista de tuplas onde p = (x,y) no e lista = (p1, p2, p3, p4)
            precision_points (int): Numero de pontos na curva de bezier
            color (QColor, optional): Cor da curva renderizada. Defaults to QColor.
        """
        self.closed = False
        self.label = label
        self.color = color
        self.selecionado: bool = False
        self.coord_world = points
        self.center_point: tuple = np.array([(points[0][0]+points[3][0])/2, (points[0][1]+points[3][1])/2])
        self.Mb = np.array([[-1,3,-3,1],[3,-6,3,0],[-3,3,0,0],[1,0,0,0]])

    def total_clip(self, n_points: float, no_clip: bool = False):
        """
        Clippa cada linha da curva de bezier (custoso mas clippa tudo naturalmente)

        Args:
            step (float): distancia entre cada ponto
            no_clip (bool): se deve haver clipping ou nao. Defaults to False
        """
        rendered_points = []
        current_point = 0
        step = 1/(n_points-1)
        for p in range(0, n_points):
            current_point = p * step 
            rendered_points.append((float(self.K(self.Gbx, current_point)),float(self.K(self.Gby, current_point))))
        
        points = list(map(lambda p: (p[0], p[1]), rendered_points))

        return super().render_to_view(3 if no_clip else 1, points)
        
    def partial_clip(self, n_points: float, _):
        """
        Clippa de acordo com o algoritmo que o professor mostrou em sala

        Args:
            step (float): distancia entre cada ponto
        """

        def in_window(point: tuple):
            return -1 <= point[0] <= 1 and -1 <= point[1] <= 1

        ponto_inicial = (float(self.K(self.Gbx, 0)),float(self.K(self.Gby, 0)))
        ponto_final = (float(self.K(self.Gbx, 1)),float(self.K(self.Gby, 1)))

        # Clippa o ponto final e inicial pra ver o que acontece
        linha_clippada = self.clip_CS([ponto_inicial, ponto_final])
        
        step = 1/(n_points-1)

        # Ponto inicial na window, portanto propagamos a renderizacao a partir dele
        encountered_window = False
        points_from_start = []
        if not linha_clippada is None and linha_clippada[0] == ponto_inicial:
            for p in range(0, n_points):
                current_scale = p * step
                current_point = (float(self.K(self.Gbx, current_scale)),float(self.K(self.Gby, current_scale)))
                if not in_window(current_point):            
                    points_from_start.append(self.clip_CS([points_from_start[-1], current_point])[1])
                    encountered_window = True
                    break 
                points_from_start.append(current_point)
        
        # A propagacao da curva encontrou uma borda, mas o ponto final da curva ainda esta na window
        points_from_end = []
        if (encountered_window or points_from_start == []) and not linha_clippada is None and linha_clippada[1] == ponto_final:
            # print("Im rendering from end")
            for p in range(n_points-1, -1, -1):
                current_scale = p * step
                current_point = (float(self.K(self.Gbx, current_scale)),float(self.K(self.Gby, current_scale)))
                if not in_window(current_point):
                    points_from_end.append(self.clip_CS([points_from_end[-1], current_point])[1])
                    encountered_window = True
                    break 
                points_from_end.append(current_point)

        # lineariza o conjunto de pontos:
        start_lines = []
        end_lines = []
        if points_from_start != []: start_lines = self.linearize(points_from_start)
        if points_from_end != []: end_lines = self.linearize(points_from_end)
        
        lines = start_lines + end_lines
        # Filtra linhas nulas
        lines = list(filter(lambda line: line is not None and line[0] is not None and line[1] is not None, lines))
        # Transforma as linhas em objetos renderizaveis
        lines = list(map(lambda line: (tuple(map(lambda p: QPointF(*self.window2view(p)), line))), lines))
        
        return lines
    
    def render_to_view(self, clip_key : int):
        """
        Atualiza a forma com que o objeto deve ser renderizado pela viewport.
        """
        clip = self.partial_clip if clip_key==2 else self.total_clip
        
        # Converte pontos para coordenadas da window
        points = self.window.to_window_coords(self.coord_world)

        # Calcula o numero de pontos adequado baseado no tamanho relativo da curva para a window
        points_distance = ((points[0][0]-points[3][0])**2 + (points[0][1]-points[3][1])**2)**0.5
        n_points =  int(max(30 * (points_distance/(2*2**0.5))**0.5, 4))

        # Gera os vetores para o eixo x e y
        self.Gbx = np.array(list(map(lambda p: p[0], points)))
        self.Gby = np.array(list(map(lambda p: p[1], points)))
        # self.Gbz = np.array(list(map(lambda p: p[2], self.pontos_controle)))

        # Calcula todos os pontos a serem renderizados

        return clip(n_points, clip_key==3)

class BSpline(Wireframe):
    def __init__(self, label: str, points: list, color = QColor(255,0,0), delta: float = 0.001):
        """
        Construtor

        Args:
            label (str): Nome da curva
            points (list): Lista de tuplas onde p = (x,y) no e lista = (p1, p2, p3, p4)
            precision_points (int): Numero de pontos na curva
            color (QColor, optional): Cor da curva renderizada. Defaults to QColor.
        """
        self.closed = False
        self.label = label
        self.color = color
        self.selecionado: bool = False
        self.coord_world = points
        self.control_points = points
        self.delta = [delta, delta**2, delta**3]
        self.Ed = np.array([[0,0,0,1],
                            [self.delta[2], self.delta[1], self.delta[0], 0],
                            [6*self.delta[2], 2*self.delta[1], 0, 0],
                            [6*self.delta[2], 0, 0, 0]])
        # self.center_point: tuple = np.array([(points[0][0]+points[3][0])/2, (points[0][1]+points[3][1])/2])
        self.Mb = np.array([[-1/6, 3/6, -3/6, 1/6],
                            [3/6, -1, 3/6, 0],
                            [-3/6, 0, 3/6, 0],
                            [1/6, 4/6, 1/6, 0]])

    def DesenhaCurvaFwdDiff(self, n, x, y):
        """
        Calcula os pontos de um subsegmento da B-Spline
        """
        # Pontos
        points = [(x[0],y[0])]
        for _ in range(1, n):
            for i in range(3):
                x[i] += x[i+1]
                y[i] += y[i+1]
                # z[i] += z[i+1]
            points.append((x[0],y[0]))
        return points

    def Get_Window_Points(self, points: list):
        """
        Dada uma janela de 4 pontos de controle retorna os pontos a serem renderizados

        Args:
            points (list[tuple]): uma lista de 4 pontos de controle

        Returns:
            list[tuple]: os pontos renderizaveis
        """
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        # zs = [p[2] for p in points]
        # print(np.array(xs))
        # print(self.Mb)
        Cx = np.matmul(self.Mb, np.array(xs))
        Cy = np.matmul(self.Mb, np.array(ys))
        # Cz = np.matmul(self.Mb, np.array(zs))
        Dx = np.matmul(self.Ed, Cx)
        Dy = np.matmul(self.Ed, Cy)
        # Dz = np.matmul(self.Ed, Cz)
        return self.DesenhaCurvaFwdDiff(int(1/self.delta[0]), Dx, Dy)
      
    def render_to_view(self, clip_key: int, points: list = None):
        points = []
        for i in range(len(self.control_points)-3):
            cpoints = self.window.to_window_coords(self.control_points[i:i+4]) 
            points += self.Get_Window_Points(cpoints)
        lines = self.linearize(points)

        lines = list(map(lambda line: (tuple(map(lambda p: QPointF(*self.window2view(p)), line))), lines))

        return lines

class Curved2D(Wireframe):
    
    def __init__(self, label: str, coord_list: list[tuple[int]], spline: bool = False, closed: bool = False, color = QColor(255,0,0), additional_data: str = "") -> None:
        self.label = label
        self.color = color
        self.__selecionado = False
        self.closed = False

        if spline:
            spline = BSpline(self.label,coord_list,color)
        else:
        # Cria uma lista de curvas de bezier a partir da entrada
            self.curvas = [coord_list[:4]]
            coord_list = coord_list[4:]
            while coord_list != []:
                self.curvas.append([self.curvas[-1][-1]] + coord_list[:3])
                coord_list = coord_list[3:]
            


                self.curvas = list(map(lambda pontos: Bezier("parte", pontos, color), self.curvas))
        
        self.update_center_point()

    def update_center_point(self):
        cxacc, cyacc = self.curvas[0][0]
        for curva in self.curvas:
            cxacc += curva[-1][0]
            cyacc += curva[-1][1]
        self.center_point = [cxacc/(len(self.curvas)+1), cyacc/(len(self.curvas)+1)]

    @property
    def selecionado(self):
        return self.__selecionado
        
    @selecionado.setter
    def selecionado(self, v: bool):
        for curva in self.curvas:
            curva.selecionado = v
        self.__selecionado = v

    def translade(self, dx: int, dy: int):
        theta = radians(self.window.angle)
        dx, dy = dx * cos(theta) - dy * sin(theta), dy * cos(theta) + dx * sin(theta)
        self.center_point[0] += dx
        self.center_point[1] += dy
        for curva in self.curvas:
            curva.transform([np.array([[1,0,0],[0,1,0],[dx, dy, 1]])])

    def stretch(self, x_factor: int, y_factor: int, center: tuple[int] = (None, None)):
        matrix = np.array([[x_factor,0,0],[0,y_factor,0],[0,0,1]])
        if center == (None, None):
            center = self.center_point

        for curva in self.curvas:
            curva.transform([curva.center_transformation(matrix, center=center)])
        
        self.update_center_point()
    
    def rotate(self, angle: float, center: tuple[int] = (None, None)):
        matrix = np.array([[cos(radians(angle)), -sin(radians(angle)), 0], [sin(radians(angle)), cos(radians(angle)), 0], [0,0,1]])
        if center == (None, None):
            center = self.center_point
        for curva in self.curvas:
            curva.transform([curva.center_transformation(matrix, center=center)])
        
        self.update_center_point()

    def update_viewport(self, xvw: int, yvw: int, widthvw: int, heigthvw: int) -> None:
        super().update_viewport
        for curva in self.curvas:
            curva.update_viewport(xvw, yvw, widthvw, heigthvw)
    
    def render_to_view(self, clip_key: int, points: list = None):
        lines = []
        for curva in self.curvas:
            lines += curva.render_to_view(clip_key)
        return lines

    def update_window(self, window):
        self.window = window
        for curva in self.curvas:
            curva.update_window(window)
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    control_points = [(1,0), (3,3), (6,3), (8,1), (15,5), (6,6), (15,2)]
    # window = B_SplineDrawer(control_points)
    # window.show()
    # window.update()
    sys.exit(app.exec_())