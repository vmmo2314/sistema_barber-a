import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import psycopg2
import datetime
from parteAgendar import agendarCita
from inventario import delInventario

class interfaz:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("1280x720")
        self.root.title("Barbería del Alexis :D")
        self.cargarTodo()


    def cargarTodo(self):
        # Crear un objeto Treeview
        self.tree = ttk.Treeview(self.root, columns=("Nombre Barbero", "Nombre Cliente", "Hora", "Servicio"),
                                 show="headings")

        # Establecer el tema del estilo
        self.style = ttk.Style()
        self.style.theme_use("xpnative")  # Puedes cambiar "clam" a otros temas como "default", "alt", "classic", etc.

        # Estilo para el encabezado
        self.style.configure("Treeview.Heading", font=("Helvetica", 18, "bold"))

        # Estilo para las filas alternas
        self.style.configure("Treeview", font=("Helvetica", 12), rowheight=35, background="#f5f5f5")
        self.style.map("Treeview", background=[("selected", "#347083")])

        ##Conexion a la base de datos
        self.records = []

        try:
            # Parámetros de conexión
            self.connection = psycopg2.connect(
                user="postgres",
                password="usuario",
                host="localhost",
                port="5432",
                database="barberia_sistema"
            )
            # Crear un cursor para ejecutar consultas
            self.cursor = self.connection.cursor()

            # Obtener el día
            dia_actual = datetime.datetime.now().strftime('%A').lower()

            # Traducir los días de la semana al español
            dias_ingles = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            dias_espanol = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
            dia_actual = dias_espanol[dias_ingles.index(dia_actual)]

            # Ejecutar la consulta SQL con la condición WHERE
            self.cursor.execute("""
                SELECT id_cita, nombre_cliente, hora, id_barbero, id_servicio, dia FROM citas_martes WHERE dia = %s
                UNION ALL
                SELECT id_cita, nombre_cliente, hora, id_barbero, id_servicio, dia FROM citas_miercoles WHERE dia = %s
                UNION ALL
                SELECT id_cita, nombre_cliente, hora, id_barbero, id_servicio, dia FROM citas_jueves WHERE dia = %s
                UNION ALL
                SELECT id_cita, nombre_cliente, hora, id_barbero, id_servicio, dia FROM citas_viernes WHERE dia = %s
                UNION ALL
                SELECT id_cita, nombre_cliente, hora, id_barbero, id_servicio, dia FROM citas_sabado WHERE dia = %s
                UNION ALL
                SELECT id_cita, nombre_cliente, hora, id_barbero, id_servicio, dia FROM citas_domingo WHERE dia = %s
            """, (dia_actual, dia_actual, dia_actual, dia_actual, dia_actual, dia_actual))

            # Obtener los registros
            self.records = self.cursor.fetchall()

        except (Exception, psycopg2.Error) as error:
            print("Error al conectar a la base de datos:", error)

        finally:
            # Cerrar el cursor y la conexión si están definidos
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()

        self.tablaPrincipal_Citas()

    def mainMenu(self):
        # Etiquetas
        Menu_label = tk.Label(self.root, text="Barbería", font=("Helvetica", 15))
        Menu_label.place(relx=0.5, rely=.05, anchor=tk.CENTER)
        self.tablaPrincipal_Citas()
        self.cargarBotonesIzquierdos()
        self.botonReload()
        self.root.mainloop()


    def botonReload(self):
        self.style.configure("TButton", relief="flat", font=("Helvetica", 16))
        botonRecargar = ttk.Button(self.root, text="Recargar", command=self.cargarTodo)
        botonRecargar.place(relx=0.95, rely=0.3, anchor=tk.CENTER)
    def tablaPrincipal_Citas(self):
        # Configurar las columnas
        self.tree.heading("Nombre Barbero", text="Nombre Barbero")
        self.tree.heading("Nombre Cliente", text="Nombre Cliente")
        self.tree.heading("Hora", text="Hora")
        self.tree.heading("Servicio", text="Servicio")

        self.tree.place(relx=0.5, rely=0.5, width=1000, height=600, anchor=tk.CENTER)
        self.cargarTabla_citas_hoy()

    def cargarTabla_citas_hoy(self):
        # Limpiar la tabla actual
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Obtener el día actual en español (lunes, martes, miércoles, etc.)
        dia_actual = datetime.datetime.now().strftime('%A').lower()

        # Traducir los días de la semana al español
        dias_ingles = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        dias_espanol = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        dia_actual = dias_espanol[dias_ingles.index(dia_actual)]

        # Insertar datos en la tabla
        for dato in self.records:
            # Supongamos que el índice 2 es la posición del campo hora en la tupla
            hora_cita = dato[2]

            # Obtener información detallada para id_barbero y id_servicio
            id_barbero = dato[3]
            id_servicio = dato[4]

            # Realizar consulta adicional para obtener el nombre del barbero
            nombre_barbero = self.obtenerNombreBarbero(id_barbero)

            # Realizar consulta adicional para obtener el nombre del servicio
            nombre_servicio = self.obtenerNombreServicio(id_servicio)

            # Insertar los datos en la tabla
            self.tree.insert("", "end", values=(nombre_barbero, dato[1], dato[2], nombre_servicio))


    def cargarBotonesIzquierdos(self):
        self.style.configure("TButton", relief="flat", font=("Helvetica", 16))
        botonAgendar = ttk.Button(self.root, text="Agendar", command=self.mostrarVentanaAgendar)
        botonAgendar.place(relx=0.05, rely=0.3, anchor=tk.CENTER)

        botonInventario = ttk.Button(self.root, text="Inventario", command=self.mostrarVentanaInventario)
        botonInventario.place(relx=0.05, rely=0.5, anchor=tk.CENTER)

    def mostrarVentanaAgendar(self):
        agendar_cita = agendarCita()
        agendar_cita.pantallaPrincipal()

    def mostrarVentanaInventario(self):
        myVentana = delInventario()
        myVentana.pantallaPrincipal()

    def obtenerNombreBarbero(self, id_barbero):
        try:
            # Conectar a la base de datos
            connection = psycopg2.connect(
                user="postgres",
                password="usuario",
                host="localhost",
                port="5432",
                database="barberia_sistema"
            )
            cursor = connection.cursor()

            # Ejecutar la consulta SQL para obtener el nombre del barbero
            cursor.execute("SELECT nombre_barbero FROM barberos WHERE id_barbero = %s;", (id_barbero,))

            # Obtener el resultado de la consulta
            resultado = cursor.fetchone()

            # Cerrar el cursor y la conexión
            cursor.close()
            connection.close()

            # Devolver el nombre del barbero si se encontró, de lo contrario devolver None
            return resultado[0] if resultado else None

        except (Exception, psycopg2.Error) as error:
            print("Error al obtener el nombre del barbero:", error)
            return None

    def obtenerNombreServicio(self, id_servicio):
        try:
            # Conectar a la base de datos
            connection = psycopg2.connect(
                user="postgres",
                password="usuario",
                host="localhost",
                port="5432",
                database="barberia_sistema"
            )
            cursor = connection.cursor()

            # Ejecutar la consulta SQL para obtener el nombre del servicio
            cursor.execute("SELECT nombre_servicio FROM servicios WHERE id_servicio = %s;", (id_servicio,))

            # Obtener el resultado de la consulta
            resultado = cursor.fetchone()

            # Cerrar el cursor y la conexión
            cursor.close()
            connection.close()

            # Devolver el nombre del servicio si se encontró, de lo contrario devolver None
            return resultado[0] if resultado else None

        except (Exception, psycopg2.Error) as error:
            print("Error al obtener el nombre del servicio:", error)
            return None

myInterfaz = interfaz()
myInterfaz.mainMenu()