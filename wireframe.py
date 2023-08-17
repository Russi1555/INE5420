"""
Modulo com as primitivas graficas.
"""

from PyQt5.QtCore import QPointF
import numpy as np
from math import sin, cos, radians

class wireframe:
    def __init__(self, label: str, coord_list: list[tuple[int]], closed: bool = False) -> None:
        """Construtor

        Args:
            label (str): Nome da primitiva grafica.
            coord_list (list[tuple[int]]): Lista de pontos da primitiva.
            closed (bool): Se o ponto final deve ser ligado ao ponto inicial ou nao.
        """

        self.label: str = label
        self.coord_world: list[tuple[int]] = coord_list
        self.coord_view: list[tuple[int]] = None
        self.center_point: tuple = (sum(map(lambda e: e[0], coord_list))/len(coord_list), sum(map(lambda e: e[1], coord_list))/len(coord_list))
        self.closed: bool = closed
        self.xvw: int = None
        self.yvw: int = None
        self.widthvw: int = None
        self.heigthvw: int = None
        self.widthwin: int = None
        self.heigthwin: int = None
    
    def render_to_view(self):
        """
        Atualiza a forma com que o objeto deve ser renderizado pela viewport.
        """
        self.coord_view = []
        for (x, y) in self.coord_world:
            
            self.coord_view.append((self.xvw + (x  * (self.widthvw/self.widthwin)), self.yvw + (y  * (self.heigthvw/self.heigthwin))))
    
    def center_transformation(self, transformation):
        """
        Recebe uma transformacao e coloca o centro do mundo no centro do objeto para a mesma

        Args:
            transformation (matriz): matriz transormacao. 
        """
        trans = np.array([[1,0,0],[0,1,0],[self.xvw-self.center_point[0], self.yvw-self.center_point[1], 1]])
        trans = np.matmul(trans, transformation)
        return np.matmul(trans, np.array([[1,0,0],[0,1,0],[self.center_point[0], self.center_point[1], 1]]))

    def translade(self, x_increment: int, y_increment: int):
        """
        Desloca o objeto.

        Args:
            x_increment (int): deslocamento x.
            y_increment (int): deslocamento y.
        """
        self.transform([np.array([[1,0,0],[0,1,0],[x_increment, y_increment, 1]])])
    
    def stretch(self, x_factor: int, y_factor: int):
        """
        Estica o objeto

        Args:
            x_factor (int): fator de mult no eixo x.
            y_factor (int): fator de mult no eixo x.
        """

        self.transform([self.center_transformation(np.array([[x_factor,0,0],[0,y_factor,0],[0,0,1]]))])
    
    def rotate(self, angle: float):
        """
        Rotates the object by an angle.

        Args:
            angle (float): angle to be rotated.
        """
        self.transform([self.center_transformation(np.array([[cos(radians(angle)), -sin(radians(angle)), 0], [sin(radians(angle)), cos(radians(angle)), 0], [0,0,1]]))])

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
    
    def points(self) -> list[QPointF]:
        """
        Retorna uma lista de pontos a serem renderizados. 
        Returns:
            list[QPointF]: lista de pontos retornados.
        """
        self.render_to_view()
        return [QPointF(x,y) for (x, y) in self.coord_view] if not self.closed else [QPointF(x,y) for (x, y) in self.coord_view] + [QPointF(*self.coord_view[0])]

    def transform(self, transform_list: list):
        """
        Transforms the objects

        Args:
            transform_list (list): list of numpy matrixes
        """

        for i, (x, y) in enumerate(self.coord_world):
            vector = np.array([x,y,1])
            for matrix in transform_list:
                vector = vector.dot(matrix)
            self.coord_world[i] = (vector[0], vector[1])