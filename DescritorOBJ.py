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
        arquivo_nome = os.path.join("objetos", "cena.obj")
        arquivo = open(arquivo_nome, "r")
        dic_vetores = dict()
        dic_objetos = dict()
        contador_vetores = 1
        objeto_carregando_nome = ""
        objeto_carregando_vetores = []
        objeto_carregando_cor = QtGui.QColor(255,0,0) #se não específicado é vermelho
        objeto_carregando_close = False
        objeto_carregando_filled = False
        objeto_carregando_bezier = False
        objeto_carregando_spline = False
        for linha in arquivo:
           # print(linha)
            info = linha.split()
            if info == []:
                pass
            else:
                # print(info)
                identficador = info[0]
                if identficador == 'v':
                    dic_vetores[contador_vetores] = info[1:]
                    contador_vetores+=1
                elif identficador == 'o':
                    if objeto_carregando_nome != "": #adiciona o objeto pronto ao dicionario de objetos e limpa os buffers
                        dic_objetos[objeto_carregando_nome] = [objeto_carregando_nome, objeto_carregando_vetores,objeto_carregando_close, objeto_carregando_cor, objeto_carregando_filled, objeto_carregando_bezier, objeto_carregando_spline]
                        objeto_carregando_nome = ""
                        objeto_carregando_vetores = []
                        objeto_carregando_close = False
                        objeto_carregando_cor = QtGui.QColor(255,0,0)

                    objeto_carregando_nome = info[1]

                elif identficador == "Kd":
                    objeto_carregando_cor = QtGui.QColor(int(info[1]),int(info[2]),int(info[3]))

                else:
                    for key in info[1:]:
                        #print(info[1:])
                        #print(dic_vetores)
                        key = int(key)
                        tupla = (float(dic_vetores[key][0]), float((dic_vetores[key])[1]))
                        objeto_carregando_vetores.append(tupla)
                        #print(str(tupla))
                    if identficador == "f":
                        objeto_carregando_close = True
                        objeto_carregando_filled = True
                        objeto_carregando_bezier = False
                        objeto_carregando_spline = False
                    elif identficador == "l" and objeto_carregando_vetores[0] == objeto_carregando_vetores[-1]:
                        objeto_carregando_close = True
                        objeto_carregando_filled = False
                        objeto_carregando_bezier = False
                        objeto_carregando_spline = False
                    elif identficador == "b":
                        objeto_carregando_close = False
                        objeto_carregando_filled = False
                        objeto_carregando_bezier = True
                        objeto_carregando_spline = False
                    elif identficador == "s":
                        objeto_carregando_close = False
                        objeto_carregando_filled = False
                        objeto_carregando_bezier = False
                        objeto_carregando_spline = True
                        


        dic_objetos[objeto_carregando_nome] = [objeto_carregando_nome, objeto_carregando_vetores,objeto_carregando_close, objeto_carregando_cor, objeto_carregando_filled, objeto_carregando_bezier, objeto_carregando_spline]
        return dic_objetos

