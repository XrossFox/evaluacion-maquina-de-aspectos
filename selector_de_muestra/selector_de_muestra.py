
from os import listdir
from os.path import join, isdir, isfile
import re
import json
import click
from random import shuffle


def cargar_comentarios(direccion):
        """
        Lee los comentarios de cada tecnología en su respectiva carpeta, en el directorio especificado.
        @param direccion: el directorio donde se buscan los comentarios.
        @return: dict() de listas. Cada llave es una tecnologia, como valor se tiene una lista con los comentarios
        de cada tecnología encontrada.
        """
        dir_tec = [join(direccion, directorio) for directorio in listdir(direccion)]
        comentarios = dict()
        
        # revisar los directorios y remover los que no lo son
        for directorio in dir_tec:
            if not isdir(directorio):
                dir_tec.remove(directorio)
                
        # cargar los comentarios dentro de la lista de directorios en su respectiva llave
        for directorio in dir_tec:
            tmp = _aux_cargar_comentarios(directorio)
            comentarios[tmp[0]] = tmp[1]
        
        return comentarios
        
def _aux_cargar_comentarios(directorio):
        """
        Lee todos los comentarios con extension .json en un directorio, y devuelve una tupla: (nombre, [lista_comentarios])
        @param directorio: direccion del directorio
        @return: una tupla (nombre, [lista_de_comentarios])
        """
        nom_tec = re.split(r"[\\/]", directorio)
        archivos = [join(directorio, archivo) for archivo in listdir(directorio)]
        
        # eliminar no-archivos y los que no tienen la extension apropiada
        for archivo in archivos:
            if not isfile(archivo):
                archivos.remove(archivo)
            if not archivo.endswith(".json"):
                archivos.remove(archivo)
        
        # leer todos los .json
        tmp_list = list()
        # archivo por archivo
        for archivo in archivos:
            # se abre el archivo actual
            with open(file=archivo, mode="r", encoding="utf-8") as fl:
                com = json.load(fl)
                
                # revisa que sea un json array
                if not isinstance(com, list):
                    raise ValueError("Uno de los elementos en '{}' no es un json array".format(archivo))
                
                for el in com:
                    # revisa que sean strings
                    if not isinstance(el, str):
                        raise ValueError("Uno de los elementos en '{}' no es un string".format(archivo))
                    
                    # agrega los comentarios a un set para evitar duplicados
                    if el not in tmp_list:
                        tmp_list.append(el)
        
        return (nom_tec[-1], tmp_list)

import sys

def extraer_aspectos(dir_extractor_aspectos, lista_comentarios, numero_comentarios):
    """
    Recibe una lista de comentarios, y extrae los aspectos de 'n' comentarios.
    @param dir_extractor_aspectos: dirección a la carpeta raíz de Extractor de Aspectos
    @param lista_comentarios: lista de los comentarios a buscar.
    @param numero_comentarios: solo n numero de comentarios CON ASPECTOS se mantendran al final, el resto no se analiza.
    @return: lista de tuplas con el comentario y el diccionario de aspectos.
    """
    # importamos extractor de aspectos
    sys.path.append(dir_extractor_aspectos)
    from extractor import extractor_de_aspectos

    ex = extractor_de_aspectos.ExtractorDeAspectos()
    
    # aqui van los comentarios y sus aspectos
    lista_comentarios_aspectos = list()
    # se recorren los comentarios, se agregan al diccionario SOLO si poseen al menos un aspecto
    for comentario in lista_comentarios:
        diccionario = ex.iniciar_extraccion(texto=comentario)
        # si se encuentra al menos un aspecto que no sea None. entonces se agrega al dict
        for llave in diccionario.keys():
            if diccionario[llave]:
                lista_comentarios_aspectos.append((comentario, diccionario))
        # si se agregan n comentarios, se ignora el resto.
        if len(lista_comentarios_aspectos) >= numero_comentarios:
            break
    ex.cerrar()
    return lista_comentarios_aspectos

def salida(lista_comentarios_aspectos, dir_salida="./"):
    """
    escribe la lista de comentarios y aspectos a dsco duro. Escribe un archivo .json solo con los comentarios
    y otro con los comentarios mas su diccionario de aspectos.
    @param lista_comentarios_aspectos: la lista con la tupla (comentario, dict aspectos). 
    """
    comentarios = [tupla[0] for tupla in lista_comentarios_aspectos]
    
    with open(join(dir_salida,"comentarios.json"), "wt", encoding="utf-8") as arc:
        json.dump(comentarios, arc)
    
    with open(file=join(dir_salida,"lista_com_asp.json"), mode="wt", encoding="utf-8") as arc:
        json.dump(lista_comentarios_aspectos, arc)
    
@click.command()
@click.argument("dir_comentarios")
@click.argument("dir_extractor_de_aspectos")
@click.option("-n", default=200, help="Cantidad de comentarios a seleccionar. 200 por defecto")
@click.option("-o", default="./", help="directorio de salida. ./ por defecto")
def main(dir_comentarios, dir_extractor_de_aspectos, o, n):
    print("cargando comentarios... dirección: {}".format(dir_comentarios))
    dict_comentarios = cargar_comentarios(dir_comentarios)
    comentarios = []
    for llave in dict_comentarios.keys():
        comentarios.extend(dict_comentarios[llave])
    
    print("Se encontraron: {} comentario/s".format(str(len(comentarios))))
    
    lista_tuplas = extraer_aspectos(dir_extractor_aspectos=dir_extractor_de_aspectos,
                                    lista_comentarios=comentarios,
                                    numero_comentarios=n)
    shuffle(lista_tuplas)
    
    print("Se seleccionaron: {} comentarios.".format(str(len(lista_tuplas))))
    
    salida(lista_comentarios_aspectos=lista_tuplas, dir_salida=o)
    
    print("Guardado comentarios seleccionados en: {}".format(o))


if __name__ == "__main__":
    main()