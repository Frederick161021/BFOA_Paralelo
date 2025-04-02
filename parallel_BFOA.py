from copy import copy
from multiprocessing import Manager, Pool
import time
from bacteria import bacteria
import numpy
import copy
from fastaReader import fastaReader
from documentoExcel import documentoExcel
import psutil
import time
import threading

uso_cpu_por_nucleo = []
uso_memoria_total = []

def ejecutar_bfoa(numeroEjecuciones):
    resultados_fitness = []
    resultados_nfe = []
    resultados_blosum = []
    resultados_cpu = []
    resultados_nucleos = []
    resultados_memoria = []

    for ejecucion in range(numeroEjecuciones):
        numeroDeBacterias = 4
        numRandomBacteria = 1
        iteraciones = 3
        tumbo = 2                                             #numero de gaps a insertar
        nado = 3
        secuencias = list()

        secuencias = fastaReader().seqs
        names = fastaReader().names







        #hace todas las secuencias listas de caracteres
        for i in range(len(secuencias)):
            #elimina saltos de linea
            secuencias[i] = list(secuencias[i])




        globalNFE = 0                            #numero de evaluaciones de la funcion objetivo



        dAttr= 0.1 #0.1
        wAttr= 0.002 #0.2
        hRep=dAttr
        wRep= .001    #10





        manager = Manager()
        numSec = len(secuencias)
        print("numSec: ", numSec)

        poblacion = manager.list(range(numeroDeBacterias))
        names = manager.list(names)
        NFE = manager.list(range(numeroDeBacterias))


        # print(secuencias)



        def poblacionInicial():    #lineal
            #crece la poblacion al numero de bacterias
            for i in range(numeroDeBacterias):
                bacterium = []
                for j in range(numSec):
                    bacterium.append(secuencias[j])
                poblacion[i] = list(bacterium)






        def printPoblacion():
            for i in range(numeroDeBacterias):
                print(poblacion[i])



        #---------------------------------------------------------------------------------------------------------
        operadorBacterial = bacteria(numeroDeBacterias)
        veryBest = [None, None, None] #indice, fitness, secuencias

        #registra el tiempo de inicio
        start_time = time.time()

        print("poblacion inicial ...")
        poblacionInicial()

        for it in range(iteraciones):
            print("poblacion inicial creada - Tumbo ...")
            operadorBacterial.tumbo(numSec, poblacion, tumbo)
            print("Tumbo Realizado - Cuadrando ...")
            operadorBacterial.cuadra(numSec, poblacion)
            print("poblacion inicial cuadrada - Creando granLista de Pares...")
            operadorBacterial.creaGranListaPares(poblacion)
            print("granList: creada - Evaluando Blosum Parallel")
            operadorBacterial.evaluaBlosum()  #paralelo
            print("blosum evaluado - creando Tablas Atract Parallel...")

            operadorBacterial.creaTablasAtractRepel(poblacion, dAttr, wAttr,hRep, wRep)


            operadorBacterial.creaTablaInteraction()
            print("tabla Interaction creada - creando tabla Fitness")
            operadorBacterial.creaTablaFitness()
            print("tabla Fitness creada ")
            globalNFE += operadorBacterial.getNFE()
            bestIdx, bestFitness = operadorBacterial.obtieneBest(globalNFE)
            if (veryBest[0] == None) or (bestFitness > veryBest[1]): #Remplaza el mejor
                veryBest[0] = bestIdx
                veryBest[1] = bestFitness
                veryBest[2] = copy.deepcopy(poblacion[bestIdx])
            operadorBacterial.replaceWorst(poblacion, veryBest[0])
            operadorBacterial.resetListas(numeroDeBacterias)

        print("Very Best: ", veryBest)
        #imprime el tiempo de ejecucion
        print("--- %s seconds ---" % (time.time() - start_time))



        resultados_fitness.append(veryBest[1])
        resultados_nfe.append(globalNFE)
        resultados_blosum.append(veryBest[1])
        

        uso_cpu_promedio = [sum(n) / len(n) for n in zip(*uso_cpu_por_nucleo)]
        uso_cpu_promedio_total =  sum(map(sum, uso_cpu_por_nucleo)) / sum(map(len, uso_cpu_por_nucleo))
        # uso_cpu_maximo = [max(n) for n in zip(*uso_cpu_por_nucleo)]
        uso_memoria_promedio = sum(uso_memoria_total) / len(uso_memoria_total)
        # uso_memoria_maxima = max(uso_memoria_total)

        resultados_cpu.append(uso_cpu_promedio_total)
        resultados_nucleos.append(uso_cpu_promedio)
        resultados_memoria.append(uso_memoria_promedio)

    documentoExcel(numeroEjecuciones, resultados_fitness, resultados_nfe, resultados_blosum, resultados_cpu, resultados_nucleos, resultados_memoria)

def monitorear_recursos(intervalo=0.5):
    global uso_cpu_por_nucleo, uso_memoria_total
    while monitoreando:
        uso_cpu_por_nucleo.append(psutil.cpu_percent(percpu=True))  # Uso de cada núcleo
        uso_memoria_total.append(psutil.virtual_memory().used / (1024 * 1024))  # Memoria en MB
        time.sleep(intervalo)  # Se actualiza cada 0.5 segundos


if __name__ == "__main__":
    numeroEjecuciones = 100

    monitoreando = True
    hilo_monitoreo = threading.Thread(target=monitorear_recursos, args=(0.5,))
    hilo_monitoreo.start()

    ejecutar_bfoa(numeroEjecuciones)

    monitoreando = False
    hilo_monitoreo.join()