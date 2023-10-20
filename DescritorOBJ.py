import os
from pathlib import Path
from PyQt5 import QtGui, QtWidgets, QtCore
from wireframe import Wireframe, Wireframe_filled, Curved2D, BSpline

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

            if type(objeto) == Curved2D:
                coordenadas = []
                for segmento in objeto.curvas:
                    for ponto in segmento:
                        if ponto not in coordenadas:
                            coordenadas.append(ponto)
                print(coordenadas)
            elif type(objeto) == BSpline:
                coordenadas = objeto.control_points
            else:
                coordenadas = objeto.coord_world


            escrita_v = ""

            if len(coordenadas) == 1:
                if coordenadas not in dic_verticies:
                    dic_verticies[coordenadas[0]] = contador_v
                    escrita_v +="\n" + " v "+ coordenadas[0]
                    contador_v += 1
                    escrita_futura_coords = "p "+str(dic_verticies[coordenadas]) #TESTAR

            else:

                for coord in coordenadas:
                    if coord not in dic_verticies:
                        dic_verticies[coord] = contador_v
                        escrita_v += "\n" + "v "+ str(coord[0]) + " " + str(coord[1]) + " " + "0"
                        contador_v += 1
                    escrita_futura_coords += str(dic_verticies[coord]) + " " #TESTAR

                if type(objeto) == Wireframe_filled:
                    escrita_futura_coords="f"+ escrita_futura_coords[1:]
                elif type(objeto) == Curved2D:
                    escrita_futura_coords="b"+escrita_futura_coords[1:]
                elif type(objeto) == BSpline:
                    escrita_futura_coords="s"+escrita_futura_coords[1:]
                else:
                    escrita_futura_coords="l"+ escrita_futura_coords[1:]

            
            
            escrita_cores = objeto.color.getRgb()
            escrita_cores = "Kd " + str(escrita_cores[0]) + " " + str(escrita_cores[1]) + " " + str(escrita_cores[2])
            fila_para_escrita.append(escrita_cores)
            fila_para_escrita.append(escrita_futura_coords)
            escrita_futura_nome = "o "+objeto.label
            fila_para_escrita.append(escrita_futura_nome)

            arquivo.write(escrita_v) #isso definitivamente precisa
            # print(escrita_v)
           #arquivo.write("color "+str(objeto.color.getRgb())+"\n") #precisa mas escrito diferente
        
        count_fila = contador_v
        while(fila_para_escrita):
            temp = fila_para_escrita.pop()
            arquivo.write("\n" + temp )
            # print(temp)
            count_fila +=1

    def load_objs(self):
        with open("objetos/cena.obj", "r") as arquivo:
            vetores, objetos = {}, {}
            contador_vetores = 1
            current_object = {"name": "", "points": None, "color": QtGui.QColor(255,0,0), "type": None}
            for linha in arquivo:

                info = linha.split()
                if info == []: continue
                # print(info)
                identficador = info[0]
                # Identifica as coordenadas 3D de um ponto
                if identficador == 'v':
                    vetores[contador_vetores] = info[1:]
                    contador_vetores+=1

                # Identifica o inicio da descricao de um objeto
                elif identficador == 'o':
                    current_object["name"] = info[1]

                # Indetifica uma cor RGB a ser lida
                elif identficador == "Kd":
                    current_object["color"] = QtGui.QColor(int(info[1]),int(info[2]),int(info[3]))
                    objetos[current_object["name"]] = current_object
                    current_object = {"name": "", "points": None, "color": QtGui.QColor(255,0,0), "type": None}
                   

                # Identifica a lista de pontos do objeto e seu tipo e o carrega
                else:
                    for key in info[1:]:
                        ponto = (float(vetores[int(key)][0]), float((vetores[int(key)])[1]))
                        if current_object["points"] is None: current_object["points"] = []
                        current_object["points"].append(ponto)

                    if identficador == "s": current_object["type"] = "BSpline"
                    elif identficador == "f": current_object["type"] = "Polygon"
                    elif identficador == "b": current_object["type"] = "Curved2D"
                    elif identficador == "l": 
                        if current_object["points"][0] == current_object["points"][-1]:
                            current_object["type"] = "Wireframe Closed"
                        else:
                            current_object["type"] = "Wireframe Open"
                             
        return objetos

