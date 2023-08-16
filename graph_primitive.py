"""
Module com as primitivas graficas.
"""

class GraphicPrimitive:
    def __init__(self, label: str, coord_list: list[tuple[int]], closed: bool = False) -> None:
        """Construtor

        Args:
            label (str): Nome da primitiva grafica.
            coord_list (list[tuple[int]]): Lista de pontos da primitiva.
            closed (bool): Se o ponto final deve ser ligado ao ponto inicial ou nao.
        """

        self.label: str = label
        self.coord_list: list[tuple[int]] = coord_list
        self.closed: bool = closed
    
    def __iter__(self):
        return self.coord_list.__iter__()
    
if __name__ == "__main__":
    g = GraphicPrimitive("nome", [(0,0),(10,10),(100,10)])
    for x, y in g:
        print(x,y)