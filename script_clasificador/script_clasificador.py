import sys
sys.path.append('../')
import json
from os import listdir
from os.path import join
import pickle
from modelo_entrenado import ModeloEntrenado
import textblob
import click

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

def reformatear_json(lista):
    """
    Recibe una lista del archivo JSON y la reformatea con los soguientes campos:
    [{comentario, aspectos, clas_modelo, clas_tb, clas_tb_no_neutro}].
    @param lista: un list()
    @return: un list() con nuevo contenido.
    """
    lista_vieja = lista
    lista_nueva = list()
    
    for lista in lista_vieja:
        dict_campos = dict()
        # indice 0 es el comentario
        dict_campos["comentario"] = lista[0]
        # indice 1 son los aspectos
        dict_campos["aspectos"] = lista[1]
        # agregamos los nuevos campos para las polaridades
        dict_campos["clas_modelo"] = _fabrica_dicts()
        dict_campos["clas_modelo_neutro"] = _fabrica_dicts()
        dict_campos["clas_tb"] = _fabrica_dicts()
        dict_campos["clas_tb_no_neutro"] = _fabrica_dicts()
        lista_nueva.append(dict_campos)
        
    return lista_nueva

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
    

def cargar_modelo_entrenado(direccion):
    """
    Lee todos los archivos en el directorio recibido con extension .clasif. Si no encuentra archivos, levanta una
    excepcion. Carga el modelo mas reciente en el directorio.
    @param direccion: direccion hacia el directorio con los archivos .clasif.
    @return: una instancia de modelo_entrenado.
    """
    archivos = list(listdir(direccion))
    ult_clasif = ""
    mod_en = None
    for n in range(len(archivos)):
        # se recorre desde atras la lista de archivos
        nombre = archivos[(n+1)*-1]
        # si el ultimo elemento tiene la extension, se usa ese. Si no continua.
        if nombre.endswith(".clasif"):
            ult_clasif = join(direccion, nombre)
            break
        n += 1
    try:
        with open(file=ult_clasif, mode="rb") as fl:
            mod_en = pickle.load(fl)
    except:
        raise ValueError("No se encontro ningÃºn archivo con extensions '.clasif'")
    return mod_en
    
def clasificar_json_con_nb(comentarios, modelo_entrenado):
    """
    Clasifica los aspectos de los comentarios utilizando el clasificador NB.
    @param comentarios: la lista de dicts con los comentarios y aspectos.
    @param modelo_entrenado: la instancia del modelo entrenado Naïve Bayes.
    @return: el dict con los aspectos clasificados.
    """
    # recorrer lista de dicts
    for n in range(len(comentarios)):
        # recorrer aspectos
        for aspecto in comentarios[n]["aspectos"]:
            print("aspecto: ".format(aspecto))
            strings_aspectos = comentarios[n]["aspectos"][aspecto]
            # si los aspectos no son None 
            if strings_aspectos:
                # clasificar aspectos concatenados por que es una lista de strings
                comentarios[n]["clas_modelo"][aspecto] = modelo_entrenado.clasificar_comentario(" ".join(strings_aspectos))
    
    return comentarios

def clasificar_json_con_nb_neutros(comentarios, modelo_entrenado):
    """
    Clasifica los aspectos de los comentarios utilizando el clasificador NB y permite el soporte para comentarios neutros.
    @param comentarios: la lista de dicts con los comentarios y aspectos.
    @param modelo_entrenado: la instancia del modelo entrenado Naïve Bayes.
    @return: el dict con los aspectos clasificados.
    """
    # recorrer lista de dicts
    for n in range(len(comentarios)):
        # recorrer aspectos
        for aspecto in comentarios[n]["aspectos"]:
            strings_aspectos = comentarios[n]["aspectos"][aspecto]
            # si los aspectos no son None 
            if strings_aspectos:
                # clasificar aspectos concatenados por que es una lista de strings
                comentarios[n]["clas_modelo_neutro"][aspecto] = modelo_entrenado.clasificar_comentario(" ".join(strings_aspectos), neutro=True)
    
    return comentarios

def clasificar_json_con_tb(comentarios):
    """
    Clasifica los aspectos de los comentarios usando TextBlob.
    @param comentario: La lista de dicts con comentarios y aspectos.
    @return: la lista de dicts actualizada con los aspectos clasificados por textblob.
    """
    # recorrer lista de dicts
    for n in range(len(comentarios)):
        # recorrer aspectos
        for aspecto in comentarios[n]["aspectos"]:
            strings_aspectos = comentarios[n]["aspectos"][aspecto]
            # si los aspectos no son None 
            if strings_aspectos:
                # clasificar aspectos concatenados por que es una lista de strings
                polaridad = textblob.TextBlob(" ".join(strings_aspectos)).sentiment.polarity
                # 1 para positivo, 0 para neutral y -1 para negativo
                if polaridad > 0:
                    comentarios[n]["clas_tb"][aspecto] = 1
                elif polaridad < 0:
                    comentarios[n]["clas_tb"][aspecto] = -1
                else:
                    comentarios[n]["clas_tb"][aspecto] = 0
                    
    return comentarios

def clasificar_json_con_tb_no_neutro(comentarios):
    """
    Clasifica los aspectos de los comentarios usando TextBlob. Convierte los comentarios neutrales en negativos.
    @param comentario: La lista de dicts con comentarios y aspectos.
    @return: la lista de dicts actualizada con los aspectos clasificados por textblob.
    """
    # recorrer lista de dicts
    for n in range(len(comentarios)):
        # recorrer aspectos
        for aspecto in comentarios[n]["aspectos"]:
            strings_aspectos = comentarios[n]["aspectos"][aspecto]
            # si los aspectos no son None 
            if strings_aspectos:
                # clasificar aspectos concatenados por que es una lista de strings
                polaridad = textblob.TextBlob(" ".join(strings_aspectos)).sentiment.polarity
                # 1 para positivo, 0 para negativo y neutro
                if polaridad > 0:
                    comentarios[n]["clas_tb_no_neutro"][aspecto] = 1
                else:
                    comentarios[n]["clas_tb_no_neutro"][aspecto] = 0
                    
    return comentarios

@click.command()
@click.argument("direccion_json")
@click.argument("direccion_dir_modelos")
@click.argument("dir_salida")
def main(direccion_json, direccion_dir_modelos, dir_salida):
    """
    Inicia la clasificación de los aspectos de los comentarios de un archivo .json. Requiere especificar
    la dirección del archivo json, la carpeta con los modelos Naïve Bayes y la dirección del directorio de salida.
    """
    # cargar comentarios
    direccion_com_asp = direccion_json
    punto_json = leer_json(direccion=direccion_com_asp)
    # dar formato al json
    json_remodelado = reformatear_json(punto_json)
    # cargar modelo
    direccion_modelo = direccion_dir_modelos
    modelo = cargar_modelo_entrenado(direccion=direccion_modelo)
    # calsificar nb
    json_remodelado = clasificar_json_con_nb(comentarios=json_remodelado, modelo_entrenado=modelo)
    json_remodelado = clasificar_json_con_nb_neutros(comentarios=json_remodelado, modelo_entrenado=modelo)
    # clasificar con tb
    json_remodelado = clasificar_json_con_tb(comentarios=json_remodelado)
    # clasificar con tb sin neutros
    json_remodelado = clasificar_json_con_tb_no_neutro(comentarios=json_remodelado)
    
    with open(file=join(dir_salida,"comentarios_clasificados.json"), mode="wt", encoding="utf-8") as archivo:
        json.dump(json_remodelado, archivo)
    
                
if __name__ == "__main__":
    main()     
        
    