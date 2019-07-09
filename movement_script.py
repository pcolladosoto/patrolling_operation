#   Version 3.0 (Alberto) de generar mapa (Raspberry)     #

#   Librerias:
#   ----------------------------------------------------------
#   Libreria serial para la comunicacion portie con el Arduino.
#   Libreria numpy para trabajar con el mapa.
#   Libreria cv2 para trabajar con imagenes.
#   ----------------------------------------------------------

import serial, time, io, signal, sys, glob, os
from termcolor import colored
from re import findall

#   Puerto de comuniacion:
#   ------------------------------------------------------------
#   baudRate: Baudios de la comunicacion con el arduino. (Se
#             recomienda no tocar)

baudRate = 38400

#   Variables de configuracion:
#   ------------------------------------------------------------
#   CM: Escala a la que se quiere configurar el movil, si esta
#       a 0.1 significa que cada 10cm tenemos una celda del
#       array MAP. [casillas/cm] [Version mapa - Eliminado]

CM = 0.1

#   FLAGS:
#   --------------------------------
#   TOGGLE: Flag de control de giro.
#

TOGGLE = 0

#   TH_DIST: Distancia umbral de deteccion, distancia a la que
#            se quiere mantener alejado el movil del objeto
#            medido en casillas. [cm]
#
#       NOTA:   CM*TH_DIST > 1

TH_DIST = 110
TH_DIST_LAT = 50

#   offDel: Offset despues de la orden de ejecucion de algun
#           comando, normalmente a la espera de finalizar su
#           ejecucion.
#       [1]: Operaciones desplazamiento vertical.
#       [2]: Operaciones de rotacion.

offDel1 = 0.3
offDel2 = 6
offDel3 = 0.1

#   MPF: Cantidad de casillas que se desean avanzar en direccion
#        vertical o de rotacion. El formato es una string expresada en mm.
#   [1]: Operaciones desplazamiento vertical.
#   [2]: Operaciones de rotacion (SE RECOMIENDA NO TOCAR)

MPF1 = '0500'
MPF2 = '0700'

#   Ajuste de las variables:
#   --------------------------
#   TH_DIST: Pasada a casillas.

TH_DIST = int(TH_DIST * CM)
TH_DIST_LAT = int(TH_DIST_LAT * CM)

#       DEFINICION DE LAS FUNCIONES DEL PROGRAMA:
#   -----------------------------------------------------------------------------
#   1.- Funciones de movimiento.
#   2.- Funciones de lectura de sensores.
#   3.- Funciones de escritura del sistema.
#   -----------------------------------------------------------------------------

def find_N_open_portial_port(b_rate):
    candidates = glob.glob('/dev/tty[A-Za-z]*')
    for path in candidates:
        try:
            port = serial.Serial(path, baudrate = b_rate, timeout = None)
            if check_if_arduino():
                time.sleep(1)
                return port
            else:
                port.close()
        except(OSError, serial.SerialException):
            pass

    print(ERROR_MESSAGES["PORT_NOT_FOUND"])
    return exit()

def check_if_arduino():
    os.system("ls /dev/serial/by-id > tmp")
    if "USB2.0-Serial-if00" in open("tmp", "r").read():
        os.system("rm tmp")
        return True
    else:
        os.system("rm tmp")
        return False

port = find_N_open_portial_port(baudRate)
print colored(port.readline(),'blue')

#def IRQ_Handler(not_used0, not_used1):
#    port.write('?')
#    #port.write('?')
#    port.reset_input_buffer()
#    port.close()
#    print ''
#    print colored('Interrupcion por teclado recibida, puerto cerrado.', 'red')
#    sys.exit(0)
#    return 0

#       1.-Funciones de movimiento:
#   -----------------------------------------------------------------------------
#   Goup: Movimiento hacia delante.
#   Gown: Movimiento hacia atras.
#   Golef: Rotacion a la izquierda.
#   Gorig: Rotacion a la derecha.
#
#       NOTA1: La variable de entrada X esta en formato string pensada para que sea
#               usado MPFX.
#
#       NOTA2: La variable del puerto debe llamarse 'port', si es otra cosa port.write()
#              da error.
#

def Goup(X):
    mv = '4' + X
    time.sleep(offDel1)
    port.write(mv)
    time.sleep(offDel1)
    return 0


def Gown(X):
    mv = '5' + X
    time.sleep(offDel1)
    port.write(mv)
    time.sleep(offDel1)
    return 0


def Golef(X, togg):
#   togg = 0 # OJO - ESTO SI NO SE QUIERE USAR EL TOGGLE
    X = '0300'
    port.write('?')
    port.reset_input_buffer()
    print colored('Detenido', 'blue')
    time.sleep(offDel2 * 0.5)
    print colored('Girando a la izquierda...','blue')
    for i in range(0, 3):
        time.sleep(offDel2 * 0.5)
        if togg == 0:
            mv = 'K000' + X
            port.write(mv)
        else:
            mv = '0000' + X
            port.write(mv)
        time.sleep(offDel2 * 0.5)
        Abk()
    time.sleep(offDel2)
    return 0

def Gorig(X, togg):
#   togg = 0 # OJO - ESTO SI NO SE QUIERE USAR EL TOGGLE
    X = '0300'
    port.write('?')
    port.reset_input_buffer()
    print colored('Detenido', 'blue')
    time.sleep(offDel2 * 0.5)
    print colored('Girando a la derecha...', 'blue')
    for i in range(0, 3):
        time.sleep(offDel2 * 0.1)
        if togg == 0:
            mv = 'J000' + X
            port.write(mv)
        if togg == 1:
            mv = '1000' + X
            port.write(mv)
        time.sleep(offDel2 * 0.5)
        Abk()
    time.sleep(offDel2)
    return 0




#       2.-Funciones de lectura de sensores:
#   ------------------------------------------------------------------------------------
#   SensorX(): Detecta la distancia que recibe el sensor delantero y la compara
#                      con la umbral, si es menor, devuelve 1. Si es mayor o no detecta
#                      el objeto devuelve 0.
#
#       [Delantero]: Sensor de la parte delantera de la plataforma.
#
#       NOTA1: La variable del puerto debe llamarse 'port', si es otra cosa port.write()
#              da error, como otras funciones.

def SensorDelantero():
    retval = 0
    var = 0
    flag = True
    print colored('Entrando a sensor delantero...        Status:','green')
    while flag:
        port.reset_input_buffer()
        linea = '00000000000000000'
        port.write(':')
        time.sleep(offDel3 * 3)
        port.write(':')
        if port.in_waiting:
            linea = port.readline()
        print 'DEBUG:'
        print linea
        if "US Sensors" in linea:
            flag = False
            matches = findall(r"\d+", linea)
            var1 = int(matches[0]) #Var viene expresada en cm
            var2 = int(matches[1]) #izq
            var3 = int(matches[2]) #der
        if var1 == 0:
            retval = 0
            var1 = 3000
        if var2 == 0:
            retval = 0
            var2 = 3000
        if var3 == 0:
            retval = 0
            var3 = 3000

    if (var1 * CM < TH_DIST): # cm * [casillas/cm]
        retval = 1
        port.write('?') #Esta linea parece ignorarla, hay mas mecanismos para parar la plataforma.
        print 'Supuesta parada'
        if (var1 * CM > 8):
            print 'Primer ajuste...'
            time.sleep(offDel2 * 0.3)
            port.write('40100')
            time.sleep(offDel2 * 0.3)

    if (var2 * CM < TH_DIST_LAT):
        retval += 2
        port.write('?')
        print 'Supuesta parada'

    if (var3 * CM < TH_DIST_LAT):
        retval += 4
        port.write('?')
        print 'Supuesta parada'

    print colored(retval,'green')
    return retval

def Abk():
    flag = True
    while flag:
        port.reset_input_buffer
        linea = '0000000000000000000'
        port.write(':')
        time.sleep(offDel3)
        port.write(':')
        if port.in_waiting:
            linea = port.readline()
        if "US Sensors" in linea:
            matches = findall(r"\d+", linea)
            var2 = int(matches[1])
            var3 = int(matches[2])
            flag = False
    print 'Abk:'
    print var2
    print var3
    if (((var2 * CM < 4) and (var2 != 0)) or ((var3 * CM < 4) and (var3 != 0))):
        Gown('0100')
    else:
        port.write('?')


#   3.- Funciones de escritura del sistema:
#   -------------------------------------------------------------
#   En esta version se han eliminado.

#
#
#   1.- Abrir puertos.
#   2.- Inicializar el mapa. [Eliminado]
#   3.- Loop principal.
#

def movement(queue):

#   1.- Abrir puertos.
#   ------------------

# Toogle para hacer giros alternos si se desea... The toggle will be activated in any case...
    left_toggle = 0
    right_toggle = 0

    flag = True
#   3.- Loop principal.
#   -----------------------------------------------------------
    while True:
        time.sleep(0.7)
        while not queue.empty():

            if queue.get() == "Stop!":
                port.write("?")
                flag = False

            if queue.get == "Continue":
                flag = True
        if flag:
            SU = SensorDelantero()
            if SU == 0: #Caso sin nada delante
                Goup(MPF1)

            if (SU == 1 or SU == 2 or SU == 3): #Caso con algo delante, a la izq o ambas.
                Gorig(MPF2,right_toggle)
                right_toggle = 1 - right_toggle

            if (SU == 4 or SU == 5): #Caso con algo a la derecha o derecha y delante.
                Golef(MPF2,left_toggle)
                left_toggle = 1 - left_toggle

            if (SU == 6 or SU == 7): #Caso izq y derecha
                Gorig(MPF2,right_toggle)
                right_toggle = 1 - right_toggle
			#Gown(MPF2)
