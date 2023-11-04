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