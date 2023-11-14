from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import QApplication, QMainWindow
import numpy as np
from math import sin, cos, radians, degrees, atan2, pi
from functools import reduce
from primitivas2D import Wireframe

class Ponto3D(Wireframe):
    def __init__(self, coordenada):
        self.coord_world = coordenada
    
    def transform(self, matrix):
        ponto = np.array([*self.coord_world,1])
        ponto = ponto.dot(matrix)
        x,y,z,_ = ponto
        self.coord_world = (x,y,z)

    def __repr__(self):
        return repr(self.coord_world)

class Objeto3D(Wireframe):
    
    def __init__(self, label: str, coord_list: list[tuple[int]], color = QColor(255,0,0)) -> None:
        super().__init__(label, coord_list, color, True)
        self.coord_world = [Ponto3D(p) for p in coord_list]

    @property
    def center_point(self):
        unique_points = set(map(lambda p: p.coord_world, self.coord_world))
        x, y, z = [sum(map(lambda e: e[i], unique_points))/len(unique_points) for i in range(3)]
        return (x,y,z)

    def translade(self, dx: int, dy: int, dz:int):
        matrix = np.array([[1,0,0,0],
                           [0,1,0,0],
                           [0,0,1,0],
                           [dx,dy,dz,1]])
        self.transform(matrix)
            
    def stretch(self, dx: int, dy: int, dz: int, center_point: tuple[float] = None):
        
        matrix = np.array([[dx,0,0,0],
                           [0,dy,0,0],
                           [0,0,dz,0],
                           [0,0,0,1]])
        
        if center_point is not None or True:
            x, y, z = self.center_point
            to_cp = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[-x,-y,-z,1]])
            from_cp = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[x,y,z,1]])
            matrix = reduce(np.matmul,[to_cp, matrix,from_cp])
        self.transform(matrix)
    
    def rotate(self, rotation_matrix, rotation_axis: list[tuple[float]] = None):
        if rotation_axis is not None:
            x0, y0, z0 = rotation_axis[0]
            dx = self.center_point[0]-x0
            dy = self.center_point[1]-y0
            dz = self.center_point[2]-z0
            to_own_axis = np.array([[1,0,0,0],
                                    [0,1,0,0],
                                    [0,0,1,0],
                                    [-dx,-dy,-dz,1]])
            from_own_axis = np.linalg.inv(to_own_axis)
            rotation_matrix = reduce(np.matmul, [to_own_axis, rotation_matrix, from_own_axis])
        self.transform(rotation_matrix)

    def transform(self, matrix):
        for ponto in self.coord_world:
            ponto.transform(matrix)
    
class ViewWindow3D(Objeto3D):

    def __init__(self, x0: float, y0: float, width: float, heigth: float) -> None:
        self.dist_focal = 100
        self.SE, self.SD, self.ID, self.IE = (x0,y0,self.dist_focal), (x0+width,y0,self.dist_focal), (x0+width,y0+heigth,self.dist_focal), (x0,y0+heigth,self.dist_focal)
        self.revert_transformation = np.array([[2/width,0,0,0],[0,2/heigth,0,0],[0,0,1,0],[0,0,0,1]])
        super().__init__("window",[Ponto3D(self.SE), Ponto3D(self.SD), Ponto3D(self.ID), Ponto3D(self.IE)], QColor(0,0,0))   
    
    def ortogonal(self, points: list):
        points = list(map(lambda p: np.array((*p, 1)), points))
        new_points = list(map(lambda vec: vec.dot(self.revert_transformation), points))
        new_points = list(filter(lambda p: p[2] > 0, new_points))
        new_points = list(map(lambda p: (p[0]/(p[2]/self.dist_focal), p[1]/(p[2]/self.dist_focal)), new_points))
        return new_points
    
    def transform(self, matrix: list):
        self.revert_transformation = np.matmul(np.linalg.inv(matrix), self.revert_transformation)
        super().transform(matrix)

    def points(self, _):
        return super().points(True)

class Bezier3D(Objeto3D):

    def T(self, t: float):
        return np.array([t**3, t**2, t, 1])
    
    def K(self, Gk, pre, post):
        Gk = [Gk[0:4], Gk[4:8], Gk[8:12], Gk[12:16]]
        return reduce(np.matmul, [pre, Gk, post])

    def __init__(self, label: str, points: list, color = QColor(255,0,0)):
        self.closed = False
        self.label = label
        self.color = color
        self.selecionado: bool = False
        self.coord_world = list(map(lambda p: Ponto3D(p), points))
        self.Mb = np.array([[-1,3,-3,1],
                            [3,-6,3,0],
                            [-3,3,0,0],
                            [1,0,0,0]])
    
    def render_to_view(self, clip_key : int, limiar_points: list = None):
        """
        Atualiza a forma com que o objeto deve ser renderizado pela viewport.
        """

        points = self.coord_world
        n_points = 3


        # Gera os vetores para o eixo x e y
        Gx = np.array(list(map(lambda p: p[0], points)))
        Gy = np.array(list(map(lambda p: p[1], points)))
        Gz = np.array(list(map(lambda p: p[2], points)))
        Gx = [Gx[0:4], Gx[4:8], Gx[8:12], Gx[12:16]]
        Gy = [Gy[0:4], Gy[4:8], Gy[8:12], Gy[12:16]]
        Gz = [Gz[0:4], Gz[4:8], Gz[8:12], Gz[12:16]]

        # Calcula todos os pontos a serem renderizados
        rendered_lines = []
        step = 1/(n_points-1)
        # fixa s varia t

        for p in range(0, n_points):
            this_curve = []
            s = p * step
            pre = reduce(np.matmul, [self.T(s), self.Mb])
            prex, prey, prez = [reduce(np.matmul, [pre, Gk]) for Gk in [Gx, Gy, Gz]]
            for p in range(0, n_points):
                t = p * step
                post = reduce(np.matmul, [self.Mb, np.transpose(self.T(t))])
                this_curve.append([float(np.matmul(prek, post)) for prek in [prex, prey, prez]])

            rendered_lines.append(this_curve)
        
        # fixa t varia s
        for p in range(0, n_points):
            this_curve = []
            t = p * step
            post = reduce(np.matmul, [self.Mb, np.transpose(self.T(t))])
            postx, posty, postz = [reduce(np.matmul, [Gk, post]) for Gk in [Gx, Gy, Gz]]
            for p in range(0, n_points):
                s = p * step
                pre = reduce(np.matmul, [self.T(s), self.Mb])
                this_curve.append([float(np.matmul(pre, postk)) for postk in [postx, posty, postz]])

            rendered_lines.append(this_curve)

        for i, curve in enumerate(rendered_lines):
            rendered_lines[i] = list(map(lambda p: (p[0], p[1], p[2]), curve))

        f = super().render_to_view
        curves = [f(1, curve)[0] for curve in rendered_lines]

        return curves, None

class Curved3D(Wireframe):
    def __init__(self, label: str, points: list, color = QColor(255,0,0)):
        self.closed = False
        self.label = label
        self.color = color
        self.__selecionado: bool = False
        self.coord_world = list(map(lambda p: Ponto3D(p), points))
        self.retalhos = [points[:16]]
        points = points[16:]
        while points != []:
            self.retalhos.append(points[:16])
            points = points[16:]
        
        self.retalhos = list(map(lambda pontos: Bezier3D("parte", pontos, color), self.retalhos))
    
        self.update_center_point()

    def update_center_point(self):
        cxacc, cyacc, czacc = self.retalhos[0][0]
        for curva in self.retalhos:
            cxacc += curva[-1][0]
            cyacc += curva[-1][1]
            czacc += curva[-1][2]
        self.center_point = [cxacc/(len(self.retalhos)+1), 
                             cyacc/(len(self.retalhos)+1),
                             czacc/(len(self.retalhos)+1)]

    def update_window(self, window):
        self.window = window
        for retalho in self.retalhos:
            retalho.update_window(window)
        
    def update_viewport(self, xvw: int, yvw: int, widthvw: int, heigthvw: int) -> None:
        super().update_viewport
        for retalho in self.retalhos:
            retalho.update_viewport(xvw, yvw, widthvw, heigthvw)

    @property
    def selecionado(self):
        return self.__selecionado
        
    @selecionado.setter
    def selecionado(self, v: bool):
        for retalho in self.retalhos:
            retalho.selecionado = v
        self.__selecionado = v
    
    def translade(self, dx: float, dy: float, dz: float):
        self.center_point[0] += dx
        self.center_point[1] += dy
        self.center_point[2] += dz
        for retalho in self.retalhos:
            retalho.translade(dx, dy, dz)
    
    def stretch(self, dx: int, dy: int, dz: int, center_point: tuple[float] = None):
        matrix = np.array([[dx,0,0,0],
                           [0,dy,0,0],
                           [0,0,dz,0],
                           [0,0,0,1]])
        
        if center_point is not None or True:
            self.update_center_point()
            x, y, z = self.center_point
            to_cp = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[-x,-y,-z,1]])
            from_cp = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[x,y,z,1]])
            matrix = reduce(np.matmul,[to_cp, matrix,from_cp])
        
        self.transform(matrix)
    
    def rotate(self, rotation_matrix, rotation_axis: list[tuple[float]] = None):
        if rotation_axis is not None:
            self.update_center_point()
            x0, y0, z0 = rotation_axis[0]
            dx = self.center_point[0]-x0
            dy = self.center_point[1]-y0
            dz = self.center_point[2]-z0
            to_own_axis = np.array([[1,0,0,0],
                                    [0,1,0,0],
                                    [0,0,1,0],
                                    [-dx,-dy,-dz,1]])
            from_own_axis = np.linalg.inv(to_own_axis)
            rotation_matrix = reduce(np.matmul, [to_own_axis, rotation_matrix, from_own_axis])
        self.transform(rotation_matrix)
    
    def transform(self, matrix):
        for retalho in self.retalhos:
            retalho.transform(matrix)

    def render_to_view(self, clip_key: int, _: list = None, limiar_points: list = None):
        retalhos = []
        for retalho in self.retalhos:
            curvas, _ = retalho.render_to_view(0, [])
            curvas = list(filter(lambda l: l is not None, curvas))
            retalhos += [curvas]
 
        return retalhos, limiar_points

class Spline3D(Objeto3D):
    def __init__(self, label: str, points: list, color = QColor(255,0,0)):
        self.closed = False
        self.label = label
        self.color = color
        self.selecionado: bool = False
        self.coord_world = points
        self.control_points = points
        # self.center_point: tuple = np.array([(points[0][0]+points[3][0])/2, (points[0][1]+points[3][1])/2])
        self.Mb = np.array([[-1,3,-3,1],
                            [3,-6,3,0],
                            [-3,3,0,0],
                            [1,0,0,0]])

    def update_window(self, window):
        super().update_window(window)
        # self.translade(0,0,0)

    def accDD(self, DD):
        for DDk in DD:
            for i in range(3):
                for j in range(4):
                    DDk[i][j] += DDk[i+1][j]
        return DD
    
    def DesenhaCurvaFwdDiff(self, n, xo, yo, zo):
        x = [k for k in xo]
        y = [k for k in yo]
        z = [k for k in zo] 
        points = [(x[0],y[0],z[0])]
        for _ in range(1, n):
            for i in range(3):
                x[i] += x[i+1]
                y[i] += y[i+1]
                z[i] += z[i+1]
            points.append((x[0],y[0],z[0]))
        return points
    
    def DesenhaSuperficieFwdDiff(self, n, Ck, Es, Et):
        curves = []
        DD = [reduce(np.matmul, [Es, C, Et]) for C in Ck]
        for _ in range(n):
            this_curve = self.DesenhaCurvaFwdDiff(n, DD[0][0], DD[1][0], DD[2][0])
            curves.append(this_curve)
            DD = self.accDD(DD)
        DD = [np.transpose(reduce(np.matmul, [Es, C, Et])) for C in Ck]
        for _ in range(n):
            this_curve = self.DesenhaCurvaFwdDiff(n, DD[0][0], DD[1][0], DD[2][0])
            curves.append(this_curve)
            DD = self.accDD(DD)
        return curves
        
    def render_to_view(self, clip_key: int, points: list = None, limiar_points: list = None):
        control_points = self.control_points
        n_points = 11
        self.delta = [1/(n_points-1), (1/(n_points-1))**2, (1/(n_points-1))**3]

        ks = [[p[i] for p in control_points] for i in range(3)]
        ks = [np.array([ks[i][0:4], ks[i][4:8], ks[i][8:12], ks[i][12:16]]) for i in range(3)]
        Ck = [reduce(np.matmul, [self.Mb, np.array(ks[i]), self.Mb]) for i in range(3)]

        Ed = np.array([[0,0,0,1],
                       [self.delta[2], self.delta[1], self.delta[0], 0],
                       [6*self.delta[2], 2*self.delta[1], 0, 0],
                       [6*self.delta[2], 0, 0, 0]])
        
        Edt = np.transpose(Ed)

        curves = self.DesenhaSuperficieFwdDiff(n_points, Ck, Ed, Edt)
        # print(len(curves))
        # print([len(curve) for curve in curves])
        
        for i, curve in enumerate(curves):
            # for point in curve:
            #     print(point)
            curves[i] = list(map(lambda p: (p[0], p[1], p[2]), curve))

        f = super().render_to_view
        curves = [f(1, curve)[0] for curve in curves]

        return curves, None