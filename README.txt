Pre Requisitos:
PyQt5
numpy

Iniciando:
python3 main.py

Criando um novo objeto:
Clique em "Novo objeto" no canto superior esquerdo da tela
Insira seu nome
Insira as coordenadas (Formato: (x0, y0) (x1, y1) (x2, y2)...)
Uma check box ao lado das coordenadas pode ser selecionada pra fechar o poligono, unir o ponto final e inicial

Transformando objetos:
Selecione um ou mais objeto na lista (eles ficarão em negrito ou grossos)
Insira a quantia de transformacao em na transformacao desejada:
    Translacao (Setas): Unidades de deslocamento no mundo
    Escala (Quadrados): Proporção do aumento ou redução do objeto (Para um efeito de zoom centre o ponto central em algum lugar e tranforme todos os objetos)
    Rotação (Seta circular): Angulo em graus da rotação no sentido horario.
    
    Opcional: Ponto central da transformação.
    Escolha um ponto de referência que será o centro das trasnformações de Escala e Rotação.
    Se a check box ao lado das coordenadas for selecionada o ponto será renderizado como um ponto preto
    Se pelo menos uma coordenada for deixada em branco os objetos usarão seus próprios centros como centro da transformação.

Clipping:
O clipping é feito na função render_to_view de wireframe.