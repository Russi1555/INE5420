# INE5420 - COMPUTAÇÃO GRÁFICA

<li><STRONG>Requisitos:</STRONG></li>

		PyQt5
		numpy

<li><strong>Iniciando:</strong></li>
	
		make

<li><strong>Criando um novo objeto:</strong></li>

 1. Clique em "Novo objeto" no canto superior esquerdo da tela
 2. Insira seu nome
 3. Insira as coordenadas (Formato: (x0, y0) (x1, y1) (x2, y2)...)
 4. Uma check box ao lado das coordenadas pode ser selecionada pra fechar o poligono, unir o ponto final e inicial
 5. Um código RGB pode ser inserido para definir a cor do objeto, caso não inserido o padrão é 255 0 0.


<li><strong>Transformacoes:</strong> Há um pad com as transformações na esquerda da interface.</li>

 - Translacao (Setas): Unidades de deslocamento no mundo (Considera coordenadas do mundo).
 - Escala (Quadrados): Proporção do aumento ou redução.
 - Rotação (Seta circular): Angulo em graus da rotação no sentido horario.

<li><strong>Ponto Central:</strong></li>

 - O Usuário pode inserir coordenadas de um ponto central em cima da check box "Mostrar ponto central"
 - Enquanto as coordenadas estiverem inseridas transformações de escala e rotação o usuarão como centro.
 - Caso não inserido objetos usam seus próprio centros como centro.
 - Transformações da window <strong>SEMPRE</strong> usam o centro da própria window.

<li><strong>Visão de Mundo:</strong></li>

 - A check box visão de mundo permite enxergar o mundo no sistema de coordenadas da viewport.
 - A própria window será renderizada no mundo como um retângulo preto de borda grossa.

<li><strong>Transformar Objetos:</strong></li>

 - A check box clicar objetos permite transformar objetos ao inves da window.
Enquanto ele estiver selecionado não é possível transformar a window.
 - O pad de transformacoes passa a valer para os objetos.
 - Apenas objetos selecionados serão transformados (Eles ficam com a borda grossa).
 - Se existir um ponto central descrito (renderizado ou não)eles usarão o ponto como centro de transformações.

<li><strong>Clipping:</li></strong>

 - A tela toda é um canvas, o viewport é apenas um retângulo preto de fundo branco.
 - O clipping é feito de maneira *rustica* ainda.
