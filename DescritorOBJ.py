import os
from pathlib import Path

class DescritorOBJ:
    def __init__(self):
        pass

    def save_objs(self,objetos):
        '''
        objetos : dicionário de objetos da tela

        por enquanto vai funcionar só pros nossos objetos 2D acrescentando uma dimensão Z sempre igual a (0,0). Só mudar isso depois
        '''
        if not os.path.exists("objetos"):
            os.makedirs("objetos")
        arquivo_nome = os.path.join("objetos", "cena.obj")
        arquivo = open(arquivo_nome, "w")
        fila_para_escrita = list()
        dic_verticies = dict()
        contador_v = 1
        for key in objetos:
            objeto = objetos[key]
            escrita_futura_coords = "x "

            escrita_v = ""

            if len(objeto.coord_world) == 1:
                if objeto.coord_world not in dic_verticies:
                    dic_verticies[objeto.coord_world[0]] = contador_v
                    escrita_v +="\n" + str(contador_v) + " v "+ objeto.coord_world[0]
                    contador_v += 1
                    escrita_futura_coords = "p "+str(dic_verticies[objeto.coord_world]) #TESTAR

            else:

                for coord in objeto.coord_world:
                    if coord not in dic_verticies:
                        dic_verticies[coord] = contador_v
                        escrita_v += "\n" + str(contador_v) + " v "+ str(coord[0]) + " " + str(coord[1])
                        contador_v += 1
                    escrita_futura_coords += str(dic_verticies[coord]) + " " #TESTAR

                if objeto.closed and len(objeto.coord_world) == 3:
                    escrita_futura_coords="f" + escrita_futura_coords[1:]
                else:
                    escrita_futura_coords="l"+ escrita_futura_coords[1:]
            
            escrita_cores = objeto.color.getRgb()
            escrita_cores = "Kd " + str(escrita_cores[0]) + " " + str(escrita_cores[1]) + " " + str(escrita_cores[2])
            fila_para_escrita.append(escrita_cores)
            fila_para_escrita.append(escrita_futura_coords)
            escrita_futura_nome = "o "+objeto.label
            fila_para_escrita.append(escrita_futura_nome)

            arquivo.write(escrita_v) #isso definitivamente precisa
            print(escrita_v)
           #arquivo.write("color "+str(objeto.color.getRgb())+"\n") #precisa mas escrito diferente
        
        count_fila = contador_v
        while(fila_para_escrita):
            temp = fila_para_escrita.pop()
            arquivo.write("\n" + str(count_fila) + " " + temp )
            print(str(count_fila) + " " + temp)
            count_fila +=1

    
    def load_objs(self):
        diretorio = os.path.join("objetos")
        lista_arquivos = Path(diretorio).glob('*.obj')
        lista_retorno = []
        ##continuar já já. tem que ver se to salvando direito o negócio ali em cima##

