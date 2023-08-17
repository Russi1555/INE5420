"""
Modulo com as primitivas graficas.
"""

from PyQt5.QtCore import QPointF

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
    
    def update_viewport(self, xvw: int, yvw: int, widthvw: int, heigthvw: int, widthwin: int, heigthwin: int) -> None:
        self.coord_view = []
        for (x, y) in self.coord_world:
            self.coord_view.append((xvw + (x  * (widthvw/widthwin)), yvw + (y  * (heigthvw/heigthwin))))
    
    def points(self):
        return [QPointF(x,y) for (x, y) in self.coord_view] if not self.closed else [QPointF(x,y) for (x, y) in self.coord_view] + [QPointF(*self.coord_view[0])]
    
if __name__ == "__main__":
    g = wireframe("nome", [(0,0),(10,10),(100,10)])
    for x, y in g:
        print(x,y)