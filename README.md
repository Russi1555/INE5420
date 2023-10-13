# INE5420 - COMPUTAÇÃO GRÁFICA

<li><strong>NOVIDADES DO README ESTARÃO EM NEGRITO</strong></li>

<li><STRONG>Requisitos:</STRONG></li>

		PyQt5
		numpy

<li><strong>Iniciando:</strong></li>
	
		make

<li><strong>Criando um novo objeto:</strong></li>

 1. Clique em "Novo objeto" no canto superior esquerdo da tela
 2. Insira seu nome
 3. Insira as coordenadas (Formato: (x0, y0) (x1, y1) (x2, y2)...)
 4. Um código RGB pode ser inserido para definir a cor do objeto, caso não inserido o padrão é 255 0 0.
 5. Uma check box pode ser selecionada pra fechar o poligono, unir o ponto final e inicial.
 6. Uma checkbox pode ser selecionada para dar preenchimento ao poligono.
 7. <strong>Uma checkbox pode ser selecionada para interpretar as coordenadas como pontos de controle de Bezier de uma curva, neste caso o número de pontos tem de seguir o padrão 4 + 3 * k onde k é um inteiro qualquer. O conjunto de curvas terá continuidade C(0), o ponto final de uma é o inicial de outra. Não selecione essa checkbox se selecionar outra.</strong>

<li><strong>Curvas:</strong></li>
 
 - <strong>Todas as curvas renderizada sao curvas de Bezier.</strong>
 - <strong>A quantidade de pontos por curva é decidida dinâmicamente dado o zoom da window de forma que a curva sempre fique em qualidade razoável.</strong>

<li><strong>Transformacoes:</strong> Há um pad com as transformações na esquerda da interface.</li>

 - Translacao (Setas): Unidades de deslocamento no mundo (Considera coordenadas do mundo).
 - Escala (Quadrados): Proporção do aumento ou redução.
 - Rotação (Seta circular): Angulo em graus da rotação no sentido horario.

<li><strong>Transformando Objetos:</strong></li>

 - Enquanto houver pelo menos um objeto selecionado as transformações serão aplicadas a esses objetos.
 - Objetos de arame selecionados ficam com a borda grossa.
 - Objetos preenchidos selecionados ficam com uma borda preta.
 - Se não houver nenhum objeto selecionado as transformações serão feitas na window.
 - Apenas objetos selecionados serão transformados (Eles ficam com a borda grossa).
 - Se existir um ponto central descrito eles usarão o ponto como centro de transformações.

<li><strong>Ponto Central:</strong></li>

 - O Usuário pode inserir coordenadas de um ponto central nas caixas X: e Y:
 - Enquanto as coordenadas estiverem inseridas transformações de escala e rotação o usuarão como centro.
 - Caso não inserido objetos usam seus próprio centros como centro.
 - Transformações da window <strong>SEMPRE</strong> usam o centro da própria window.

<li><strong>Visão de Mundo:</strong></li>

 - A check box visão de mundo permite enxergar o mundo no sistema de coordenadas da viewport.
 - A própria window será renderizada no mundo como um retângulo preto de borda grossa.

<li><strong>Clipping:</li></strong>

 - A tela toda é um canvas, o viewport é apenas um retângulo preto de fundo branco.
 - Há três opções de *clipping* para wireframes, A opção de clipping selecionada é utilizada como base do clipping de poligonos preenchidos.
 - <strong>Há também três opções de *clipping* para curvas, A opção de Completa faz o clipping como se as curvas fossem wireframes, assim todo segmento da curva é clippado individualmente. A opção parcial é a apresentada em sala, a curva é percorrida das extremidades para dentro e encerra quando uma borda é encontrada, esta opção pode fazer com que partes da curva que deveriam ser renderizadas não sejam</strong>
