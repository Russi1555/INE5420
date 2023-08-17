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
    
    def move(self, x_increment: int, y_increment: int):
        """
        Desloca o objeto.

        Args:
            x_increment (int): deslocamento x.
            y_increment (int): deslocamento y.
        """
        for i, (x, y) in enumerate(self.coord_world):
            self.coord_world[i] = (x+x_increment, y+y_increment)
    
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