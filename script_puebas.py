from selector_de_muestra import selector_de_muestra

dic_comentarios = selector_de_muestra.cargar_comentarios('./datasets/pre-seleccion')
print("Ultimo comentario:")
print(dic_comentarios['java'][-1])
print("+"*50)
dir_extractor = "C:/David/Repos/Tesis-Analisis-Aspectos/extractor_de_aspectos/extractor_de_aspectos"
tuplas = selector_de_muestra.extraer_aspectos(dir_extractor_aspectos=dir_extractor,
                                              lista_comentarios=dic_comentarios['java'],
                                              numero_comentarios=200)
print(tuplas)

selector_de_muestra.salida(lista_comentarios_aspectos=tuplas, dir_salida="C:/David/Repos/evaluacion-maquina-de-aspectos/datasets/seleccion")