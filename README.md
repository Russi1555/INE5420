
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

3. Insira as coordenadas (Formato: (x0, y0, z0) (x1, y1, z1) (x2, y2, z2)...)
    - Coordenadas para um cubo, tetraedro e algumas curvas estão disponíveis no arquivo sample.

4. Um código RGB pode ser inserido para definir a cor do objeto, caso não inserido o padrão é 255 0 0.

5. Um seletor permite escolher o tipo de objeto criado a partir das coordenadas.

    - Para criar uma curva de bezier o número de pontos inseridores tem de ser múltiplo de 16. O simbolo ; é desconsiderado para curvas Bezier, de 16 em 16 pontos corridos será formado um retalho.

    - <strong> Para criar splines o simbolo ; é considerado, ele atua como um separador de linhas da matriz que cria a spline. Esta matriz tem de ter pelo menos 4x4 em dimensões.</strong>


<li><strong>Transformacoes:</strong> Há um pad com as transformações na esquerda da interface.</li>

  

- Translacao (Setas): Unidades de deslocamento no mundo (Considera coordenadas do mundo).

- Escala (Quadrados): Proporção do aumento ou redução.

- Rotação (Seta circular): Angulo em graus da rotação no sentido horario (Exige dois pontos diferentes nas caixas em baixo para definir o eixo de rotação).
    -  Botões de Rotação nos eixos canonicos realizam a rotação diretamente naqueles eixos, desconsiderando o eixo inserido pelo usuário.
    - Uma checkbox "Eixo próprio" quando selecionada fara que objetos realizem a rotação como se o eixo de rotação atravessasse seu ponto central ao invés de rodar de fato ao redor do eixo no mundo.

  

<li><strong>Transformando Objetos:</strong></li>

  

- Enquanto houver pelo menos um objeto selecionado as transformações serão aplicadas a esses objetos.

- Objetos de arame selecionados ficam com a borda grossa.

- Se não houver nenhum objeto selecionado as transformações serão feitas na window.

- Apenas objetos selecionados serão transformados (Eles ficam com a borda grossa).

<li><strong>Clipping:</li></strong>


- A tela toda é um canvas, o viewport é apenas um retângulo preto de fundo branco.

- Há três opções de *clipping* para wireframes, A opção de clipping selecionada é utilizada como base do clipping de poligonos preenchidos.

- <strong> Curvas de Bezier e Splines sempre são clipadas completamente </strong>

<li><strong>Persistência de Objetos:</li></strong>

- <strong>Os botões Salvar Objetos e Carregar objetos de versões anteriores foi restaurado e funciona como anteriormente.</strong>

- <strong>Os caracteres b para objetos identificam curvas de bezier e s splines. Objetos Spline tem de ter as dimensões de sua matriz de pontos de controle explicitamente ao lado do nome no formato:</strong>
        
        b nome x y



