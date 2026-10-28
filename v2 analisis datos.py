# =============================================================================================
# --------------------------------- DOCUMENTACIÓN INTERNA -------------------------------------
# =============================================================================================
# AUTOR: Cynthia Ayerdi. 
#   e12.cynthiamaria.ayerdih@suizoamericano.edu.gt / ayerdicynthia@gmail.com
# ASESORÍA: Héctor Gómez
# FIN EN MENTE: Ejemplificar el análisis de datos satelitales enviados con LoRa
# DESCRIPCIÓN: Interfaz inicial con tkinter para mostrar los datos de un Excel en un DataFrame.
# Estos se pueden graficar usando Matplotlib, agregando opciones iniciales de encontrar y 
# enfocar el mínimo; regresar a la vista original
# LENGUAJE: Python 3.14
# RECURSOS: Intérprete de Python 3.14
# PROCESOS PREVIOS: N/A
# HISTORIA
#   versión 1: 3.6.26
#       - Graficar cuatro datos enviados en el paquete de algún satélite junto con la fecha y 
#         hora de recibido (eje x). En el eje y:
#           *Potencia de la celda solar
#           *Capacidad de la batería
#           *Voltaje del bus
#           *Potencia del bus
#   versión 2: 3.6.26
#       - Programación orientada a objetos (uso de clases)
#       - Permite buscar y mostrar el dato mínimo
#       - Botón de reset a la vista original
#       - Mejora en la documentación

#Librería que permite crear Dataframes
import pandas as pd 

#Librería para darle un formato bonito al dataframe
from tabulate import tabulate

#Librería que permite graficar fácilmente los datos
import matplotlib.pyplot as plt, matplotlib.widgets as wid

#Librería para la interfaz inicial
from tkinter import Tk, filedialog as fd, Button
from tkinter import scrolledtext as st, messagebox as msg

# Constantes para la interfaz
COLOR_FONDO = "#F5EF92"
COLOR_BOTON = "#E7410A"
LETRA_BOTON = "Arial 14 bold"
ANCHO_BOTON = 20

class App(Tk):
    def __init__(self):
        super().__init__()
        
        # Elementos de la interfaz de la ventana inicial
        self.config(bg=COLOR_FONDO)
        self.title("Datos del Satélite")
        self.geometry("1300x600+20+20")

        Button(
            self, text="Obtener datos",
            command=self.obtener_datos,
            bg=COLOR_BOTON,font=LETRA_BOTON,width=ANCHO_BOTON
        ).pack()

        self.muestra_tabla= st.ScrolledText(
            self, width=155, height=30
        )
        self.muestra_tabla.pack(pady=2)

        Button(
            self, text="Graficar",
            command=self.graficar,
            bg=COLOR_BOTON,font=LETRA_BOTON,width=ANCHO_BOTON
        ).pack()

    def obtener_datos(self):
        
        # El usuario selecciona un archivo para abrir
        ruta= fd.askopenfilename()
        
        # Obtener datos de un archivo de Excel
        # Dataframe (tablita) con los datos extraídos del archivo
        # tomando en cuenta que la primera fila son los encabezados
        self.datos= pd.read_excel(ruta)
        
        # Nombre de cada columna
        # además será el encabezado de cada una de ellas
        self.datos.columns = [
            "Potencia de la celda solar (mW)",
            "Capacidad de la batería (mAh)",
            "Voltaje del bus (mV)",
            "Potencia del bus (mW)",
            "Fecha y hora"
        ]
        
        # Se convierte a un tipo de dato de fecha y hora
        self.datos["Fecha y hora"]= pd.to_datetime(
            self.datos["Fecha y hora"],
            dayfirst = False # Excel coloca el mes primero
        )
        
        # Una tabla en donde se formatea de forma "bonita" el Dataframe
        tabla = tabulate( 
            self.datos,
            
            # Los encabezados son los mismos que los nombres de 
            # las columnas definidos anteriormente
            headers=self.datos.columns, 
            
            tablefmt="pipe"
        )
        
        self.muestra_tabla.insert(1.0, tabla)
    
    def minimos(
        self,
        columna, # La columna en donde buscaremos el mínimo
        grafica # En qué gráfica queremos obtener el mínimo
    ):
        # Devuelve el dato mínimo y el índice en donde está
        
        # Obtiene el dato mínimo de la columna
        dato_minimo = self.datos[columna].min()
        
        # y la posición (índice) en donde éste se encuentra        
        indice_minimo = self.datos[columna].idxmin()
        
        # Las posiciones (índices) adyacentes al mínimo para que éstos correspondan a 
        # la fecha inferior y superior de la nueva gráfica
        
        # Toma el máximo entre 0 y uno menos que el mínimo 
        # para que no se salga de los datos (no tome un -1)
        indice_inferior = max(0, indice_minimo - 1) 
        
        # Toma el mínimo entre la última posición y uno más que el mínimo 
        # para que no se salga de los datos
        indice_superior = min(len(self.datos)-1, indice_minimo + 1)
        
        # Fechas correspondientes a los índices inferior y superior
        fecha_inferior = self.datos.loc[indice_inferior]["Fecha y hora"]
        fecha_superior = self.datos.loc[indice_superior]["Fecha y hora"]
        
        # Colocar esas fechas como límites en el eje x
        grafica.set_xlim(left=fecha_inferior,right=fecha_superior)
        
        # Límites en el eje y (según los valores del dato analizado)
        grafica.set_ylim(
            bottom = max(-10,dato_minimo-50), # Para que el inferior no disminuya de -10
            top=dato_minimo+50
        )
            
        plt.draw() # Actualizar la gráfica
        
        return [dato_minimo,indice_minimo]
     
    def enfocar_minimo(self, event):
        # Enfocar los valores mínimos de cada gráfica
        
        # Llama a la función que devuelve una lista con
        # el valor mínimo y su posición para cada gráfica
        dato_indice_minimo_potencia_celdas = self.minimos(
            "Potencia de la celda solar (mW)",grafica = self.potencia_celda
        )
        minima_potencia_celdas = dato_indice_minimo_potencia_celdas[0]
        indice_minima_potencia_celdas = dato_indice_minimo_potencia_celdas[1]               
        info_potencia_celda_min = f'Mínima potencia de las celdas solares: {minima_potencia_celdas}mW en fecha {self.datos.loc[indice_minima_potencia_celdas]["Fecha y hora"]}'
        
        dato_indice_minimo_capacidad_bateria = self.minimos(
            "Capacidad de la batería (mAh)",grafica=self.capacidad_bateria
        )
        minima_capacidad_bateria = dato_indice_minimo_capacidad_bateria[0]
        indice_minima_capacidad_bateria = dato_indice_minimo_capacidad_bateria[1]               
        info_capacidad_bateria_min = f'Mínima capacidad de la batería: {minima_capacidad_bateria}mAh en fecha {self.datos.loc[indice_minima_capacidad_bateria]["Fecha y hora"]}'
        
        dato_indice_minimo_voltaje_bus = self.minimos(
            "Voltaje del bus (mV)",grafica=self.voltaje_bus
        )
        minimo_voltaje_bus = dato_indice_minimo_voltaje_bus[0]
        indice_minimo_voltaje_bus= dato_indice_minimo_voltaje_bus[1]              
        info_voltaje_bus_min = f'Mínimo voltaje del bus: {minimo_voltaje_bus}mV en fecha {self.datos.loc[indice_minimo_voltaje_bus]["Fecha y hora"]}'

        dato_indice_minimo_potencia_bus = self.minimos(
            "Potencia del bus (mW)",grafica=self.potencia_bus
        )
        minima_potencia_bus = dato_indice_minimo_potencia_bus[0]
        indice_minima_potencia_bus = dato_indice_minimo_potencia_bus[1]              
        info_potencia_bus_min = f'Mínima potencia del bus: {minima_potencia_bus}mW en fecha {self.datos.loc[indice_minima_potencia_bus]["Fecha y hora"]}'
        
        # Mostrar los valores mínimos
        msg.showinfo(
            "MÍNIMOS",
            f"{info_potencia_celda_min}\n{info_capacidad_bateria_min}\n{info_voltaje_bus_min}\n{info_potencia_bus_min}"
        )
        
    def reset(self, columna, grafica):
        
        # La fecha del primer y último paquete que se tiene
        fecha_inicial = self.datos["Fecha y hora"].min()
        fecha_final = self.datos["Fecha y hora"].max()
        
        # Restablecer esas fechas como los límites en x de la gráfica
        grafica.set_xlim(
            left=fecha_inicial, right=fecha_final
        )
        
        # Valores para los límites en y
        # Aumentarlos o disminuirlos 
        # para que no queden muy "a la orilla"
        valor_minimo = self.datos[columna].min() -50
        valor_maximo = self.datos[columna].max() +50
        grafica.set_ylim(
            bottom=max(0,valor_minimo), # para que no hayan negativos 
            top=valor_maximo
        )
        
        plt.draw() # Actualizar
        
    def reiniciar_graficas(self, event):
        # Restablecer límites de las gráficas
        # Llamadas a la función para resetear una gráfica
        self.reset(
            "Potencia de la celda solar (mW)", grafica=self.potencia_celda
        )        
        self.reset(
            "Capacidad de la batería (mAh)", grafica=self.capacidad_bateria
        )        
        self.reset(
            "Voltaje del bus (mV)", grafica=self.voltaje_bus
        )        
        self.reset(
            "Potencia del bus (mW)", grafica=self.potencia_bus
        )
        
    def graficar(self):
        
        # Para colocar varias gráficas en una misma ventanita
        fig, self.ax = plt.subplots(
            2,2, # 2 de ancho y 2 de alto
            figsize=(12,6.5) # tamaño en pulgadas
        ) 
        
        # - - - BOTONES DE ANÁLISIS DE DATOS - - -
        
        # Espacio en la interfaz exclusivo para el botón de mínimos
        eje_boton_minimo = fig.add_axes([0.40, 0.01, 0.1, 0.04]) 
        self.btn_minimo = wid.Button(
            eje_boton_minimo,
            label="Mínimos"
        )
        # Función a la que llama
        self.btn_minimo.on_clicked(self.enfocar_minimo) 
        
        # Espacio en la interfaz exclusivo para el botón de resetear
        eje_boton_res = fig.add_axes([0.55, 0.01, 0.1, 0.04])
        self.btn_reset = wid.Button(
            eje_boton_res,
            label="Reset"
        )
        self.btn_reset.on_clicked(self.reiniciar_graficas)
        
        # Para el límite inferior de x se toma la fecha menor
        # La más temprana
        # El paquete más antiguo
        fecha_inicial = self.datos["Fecha y hora"].min()
        
        # - - - GRÁFICA POTENCIA DE LA CELDA - - -
        self.potencia_celda = self.ax[0, 0] # Arriba a la izquierda
        
        self.datos.plot(
            y="Potencia de la celda solar (mW)",
            x="Fecha y hora",
            marker="o", # Para los puntitos
            color="red",
            ax = self.potencia_celda # En qué espacio está la gráfica
        )
        
        # Límite inferior en x, el superior se coloca automáticamente
        self.potencia_celda.set_xlim(left=fecha_inicial) 
        
        # Límites del eje y
        self.potencia_celda.set_ylim(
            bottom=0,
            top=self.datos["Potencia de la celda solar (mW)"].max() + 50
        )
        
        self.potencia_celda.set_ylabel(
            "Potencia de la celda solar (mW)"
        )
        self.potencia_celda.set_xlabel(
            "Fecha y hora"
        )
        self.potencia_celda.grid(True)
        
        # - - - GRÁFICA CAPACIDAD DE LA BATERÍA - - -
        self.capacidad_bateria = self.ax[0, 1] # Gráfica de arriba a la derecha
        self.datos.plot(
            y="Capacidad de la batería (mAh)", 
            x="Fecha y hora",
            marker="o",
            ax = self.capacidad_bateria,
            color="green"
        )
        
        # Colocar los límites como los valores inferiores y superiores
        # con algo de "holgura" de +/- 50
        self.capacidad_bateria.set_ylim(
            bottom=self.datos["Capacidad de la batería (mAh)"].min()-50,
            top=self.datos["Capacidad de la batería (mAh)"].max()+50
        )
        self.capacidad_bateria.set_xlim(left=fecha_inicial)
        self.capacidad_bateria.set_ylabel("Capacidad de la batería (mAh)")
        self.capacidad_bateria.set_xlabel("Fecha y hora")
        self.capacidad_bateria.grid(True)
        
        # - - - GRÁFICA VOLTAJE DEL BUS - - -
        self.voltaje_bus = self.ax[1, 0] # Gráfica de abajo a la izquierda
        self.datos.plot(
            y="Voltaje del bus (mV)",
            x="Fecha y hora",
            marker="o",
            ax = self.voltaje_bus,
            color="blue"
        )
        self.voltaje_bus.set_ylim(
            bottom=self.datos["Voltaje del bus (mV)"].min()-50,
            top=self.datos["Voltaje del bus (mV)"].max()+50
        )
        self.voltaje_bus.set_xlim(left=fecha_inicial)
        self.voltaje_bus.set_ylabel("Voltaje del bus (mV)")
        self.voltaje_bus.set_xlabel("Fecha y hora")
        self.voltaje_bus.grid(True)
        
        # - - - GRÁFICA POTENCIA DEL BUS - - -
        self.potencia_bus = self.ax[1, 1] # Gráfica de abajo a la derecha
        self.datos.plot(
            y="Potencia del bus (mW)",
            x="Fecha y hora",
            marker="o",
            ax = self.potencia_bus,
            color="violet"
        )
        self.potencia_bus.set_ylim(
            bottom=self.datos["Potencia del bus (mW)"].min()-50,
            top=self.datos["Potencia del bus (mW)"].max()+50
        )
        self.potencia_bus.set_xlim(left=fecha_inicial)
        self.potencia_bus.set_ylabel("Potencia del bus (mW)")
        self.potencia_bus.set_xlabel("Fecha y hora")
        self.potencia_bus.grid(True)

        # Separación entre las gráficas
        plt.subplots_adjust(hspace=0.7, wspace=0.4) 
        plt.show() # Mostrar las gráficas

# Sólo para que funcione
ventana_principal = App()
ventana_principal.mainloop()