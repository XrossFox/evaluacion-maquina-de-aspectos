# leer json
# agregar dict de aspectos vacio para clasificacion manual
# recorrer cada comentario
## imprimir comentario y numero de comentario.
## recorrer cada aspecto y preguntarle al usuario que polaridad asignarle.
## asignar la polaridad desde la entrada del usuario, si no es valida, repetir hasta que de una que si lo sea
# imprimir json con otro nombre

import json
from os.path import join
import click

@click.command()
@click.argument("archivo_json")
@click.argument("dir_salida")
def starto(archivo_json, dir_salida):
    print("Leyendo archivo en: {}".format(archivo_json))
    lista_dicts = leer_json(direccion=archivo_json)
    print("Agregando nueva llave.")
    lista_dicts = agregar_dict_manual(lista_dicts)
    print("Recorriendo aspectos.")
    lista_dicts = recorredor(lista_dicts)
    print("Guardando Json en: {}".format(dir_salida))
    guardar_json(lista_dict=lista_dicts, dir_salida=dir_salida)
    print("Listo!")
    

def recorredor(lista_dicts):
    """
    Recorre cada elemento de la lista de dicts y permite que el usuario asigne una polaridad al
    aspecto a traves de la linea de comandos.
    @param lista_dicts: la lista de los dicts con los comentarios y sus aspectos.
    @return: lista de dicts con la clasificación manual.
    """
    
    for ind in range(len(lista_dicts)):
        print("+"*70)
        print("Comentario {} de {}:\n{}".format(ind+1, len(lista_dicts), lista_dicts[ind]["comentario"]))
        
        for aspecto in lista_dicts[ind]["aspectos"]:
            
            while True:
                if lista_dicts[ind]["aspectos"][aspecto]:
                    print("-"*70)
                    print("Aspecto: {}-{}\nTeclee: 0 Negativo, 1 Neutral, 2 Positivo.".format(aspecto," ".join(
                                                                                            lista_dicts[ind]["aspectos"][aspecto])))
                    respuesta = input(">>> ")
                    
                    try:
                        if int(respuesta) in (0, 1, 2):
                            lista_dicts[ind]["clas_manual"][aspecto] = decodificador(int(respuesta))
                            print("Respuesta guardada: {} como {}".format(lista_dicts[ind]["aspectos"][aspecto],
                                                                          lista_dicts[ind]["clas_manual"][aspecto]))
                            break
                        else:
                            print("Opción invalida")
                    except:
                        print("Error: Entrada invalida")
                else:
                    break
                
    return lista_dicts

def decodificador(entero):
    if entero == 0:
        return -1
    elif entero == 1:
        return 0
    else:
        return 1
                        
def guardar_json(lista_dict, dir_salida):
    with open(file=join(dir_salida,"comentarios_clasificados_con_manual.json"), mode="wt", encoding="utf-8") as archivo:
        json.dump(lista_dict, archivo)

def leer_json(direccion):
    """
    Lee un archivo con extension .json y lo parsea a una estructura nativa de python.
    @param direccion: dirección hacia el archivo .json
    @return: list|dict
    """
    contenido = None
    with open(direccion, mode="rt", encoding="utf-8") as fp:
        contenido = json.load(fp)
    
    return contenido

def _fabrica_dicts():
    """
    Crea dicts con los aspectos con valores None.
    """
    return {"AvailabilityAndScalability":None,
                              "Maintainability":None,
                              "Performance":None,
                              "Reliability":None,
                              "Deployability":None,
                              "Securability":None,
                              "Interoperability":None}
    
def agregar_dict_manual(lista_dicts):
    """
    Agrega un dict a la lista de dicts con la key clas_manual
    @param lista_dicts: la lista con los dicts.
    @return: lista con el nuevo dict agregado.
    """
    
    for objeto in lista_dicts:
        objeto["clas_manual"] = _fabrica_dicts()
    
    return lista_dicts
    
    

if __name__ == '__main__':
    starto()