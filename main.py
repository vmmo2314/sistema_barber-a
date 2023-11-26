import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
import psycopg2
import datetime
from parteAgendar import agendarCita
from inventario import delInventario

total = 0

def funcionpararetornarTotal():
    print(total)
    return total

class AgregarProductosVentana(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Agregar Productos a la Venta")
        self.geometry("400x400")

        self.id_producto_var = tk.StringVar(value="")
        self.cantidad_var = tk.StringVar(value="1")

        tk.Label(self, text="ID del Producto:").pack(pady=5)
        tk.Entry(self, textvariable=self.id_producto_var).pack(pady=5)

        tk.Label(self, text="Cantidad:").pack(pady=5)
        tk.Entry(self, textvariable=self.cantidad_var).pack(pady=5)

        tk.Button(self, text="Agregar", command=self.agregar_producto).pack(pady=10)

        tk.Button(self, text="Finalizar", command=self.actualizar_inventario).pack(pady=10)

        # Etiquetas para mostrar la información
        self.etiqueta_subtotal = tk.Label(self, text="Subtotal: ")
        self.etiqueta_subtotal.pack(pady=5)

        self.etiqueta_productos = tk.Label(self, text="Productos Agregados:")
        self.etiqueta_productos.pack(pady=5)

        self.productos = []  # Lista para almacenar los productos agregados

        # Cambia total a self.total para hacerlo un atributo de la clase
        self.total = 0

        self.subtotal_total = 0  # Agrega esto para inicializar subtotal_total en el constructor


    def agregar_producto(self):
        id_producto = self.id_producto_var.get()
        cantidad = int(self.cantidad_var.get())

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

            # Realizar la consulta para obtener la cantidad y el precio del producto
            cursor.execute("SELECT nombre_producto, cantidad_disponible, precio_unitario FROM inventarioproductos WHERE id_producto = %s;", (id_producto,))
            resultado = cursor.fetchone()

            if resultado:
                nombre_producto, cantidad_inventario, precio_producto = resultado

                # Puedes utilizar la cantidad y el precio en tu lógica
                print(f"Nombre del producto: {nombre_producto}")
                print(f"Cantidad en inventario: {cantidad_inventario}")
                print(f"Precio del producto: {precio_producto}")

                # Calcular el subtotal y agregar el producto a la lista
                subtotal = cantidad * precio_producto
                self.productos.append({"id_producto": id_producto, "nombre": nombre_producto, "cantidad": cantidad, "subtotal": subtotal})

                # Actualizar las etiquetas en la ventana
                self.actualizar_etiquetas()

                # Limpiar los campos después de agregar el producto
                self.id_producto_var.set("")
                self.cantidad_var.set("1")

            else:
                # El producto no fue encontrado en el inventario
                print(f"El producto con ID {id_producto} no se encontró en el inventario.")

        except (Exception, psycopg2.Error) as error:
            # Imprimir un mensaje en caso de error
            print("Error al consultar el inventario:", error)

        finally:
            # Cerrar el cursor y la conexión
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def actualizar_etiquetas(self):
        # Actualizar la etiqueta de subtotal
        self.subtotal_total = sum(producto["subtotal"] for producto in self.productos)
        self.etiqueta_subtotal.config(text=f"Subtotal: {self.subtotal_total}")

        # Actualizar la etiqueta de productos
        productos_texto = "\n".join(f"{producto['nombre']} - Cantidad: {producto['cantidad']}" for producto in self.productos)
        self.etiqueta_productos.config(text=f"Productos Agregados:\n{productos_texto}")

    def get_productos(self):
        # Devuelve la lista de productos
        return self.productos

    def actualizar_inventario(self):
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
            productos = self.get_productos()
            # Actualizar la cantidad disponible para cada producto vendido
            for producto in productos:
                id_producto = producto["id_producto"]
                cantidad_vendida = producto["cantidad"]

                # Obtener la cantidad actual en el inventario
                cursor.execute("SELECT cantidad_disponible FROM inventarioproductos WHERE id_producto = %s;", (id_producto,))
                cantidad_actual = cursor.fetchone()[0]

                # Calcular la nueva cantidad después de la venta
                nueva_cantidad = cantidad_actual - cantidad_vendida

                # Actualizar la cantidad en el inventario de la BD
                cursor.execute("UPDATE inventarioproductos SET cantidad_disponible = %s WHERE id_producto = %s;", (nueva_cantidad, id_producto))

            # Confirmar la transacción
            connection.commit()


        except (Exception, psycopg2.Error) as error:
            # Imprimir un mensaje en caso de error
            print("Error al actualizar el inventario:", error)

        finally:
            # Cerrar el cursor y la conexión
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        # Cerrar la ventana después de actualizar la base de datos
        total = self.subtotal_total
        self.destroy()


class VentanaCobro:
    def __init__(self, idCita, diaActual, idServicio):
        self.id_cita = idCita
        self.dia_actual = diaActual
        self.id_servicio = idServicio
        self.subtotal_final = 0  # Asegúrate de que subtotal_final esté inicializado en el constructor

    def setSubtotalFinal(self, subtotal_final):
        self.subtotal_final = subtotal_final  # Método para establecer el subtotal final

    def realizarCobro(self):
        # Mostrar ventana de confirmación
        confirmacion = messagebox.askquestion("Confirmación",
                                              "¿Desea agregar productos a la venta antes de eliminar la cita?")

        if confirmacion == 'yes':
            # Abrir la ventana para agregar productos
            agregar_productos_ventana = AgregarProductosVentana(None)
            agregar_productos_ventana.wait_window()


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

            # Construir el nombre de la tabla según el día actual
            nombre_tabla = f"citas_{self.dia_actual}"

            # Eliminar la cita en el día actual usando el id_cita
            cursor.execute(f"DELETE FROM {nombre_tabla} WHERE id_cita = %s;", (self.id_cita,))

            # Obtener el precio del servicio según su ID
            cursor.execute("SELECT precio_servicio FROM servicios WHERE id_servicio = %s;", (self.id_servicio,))
            precio_servicio = cursor.fetchone()[0]

            # Calcular el total final sumando el subtotal total y el precio del servicio
            total_final = agregar_productos_ventana.subtotal_total + precio_servicio


            # Confirmar la transacción
            connection.commit()

            # Mostrar mensaje emergente con el total final
            messagebox.showinfo("Cobro", f"Cobra: {total_final}")

            print(f"Cita con ID {self.id_cita} eliminada exitosamente.")

        except (Exception, psycopg2.Error) as error:
            # Imprimir un mensaje en caso de error
            print("Error al eliminar la cita:", error)

        finally:
            # Cerrar el cursor y la conexión
            if cursor:
                cursor.close()
            if connection:
                connection.close()


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
            self.dia_actual = datetime.datetime.now().strftime('%A').lower()

            # Traducir los días de la semana al español
            dias_ingles = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            dias_espanol = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
            self.dia_actual = dias_espanol[dias_ingles.index(self.dia_actual)]

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
            """, (self.dia_actual, self.dia_actual, self.dia_actual, self.dia_actual, self.dia_actual, self.dia_actual))

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

        # Agregar el botón de cobro
        self.style.configure("TButton", relief="flat", font=("Helvetica", 16))
        botonCobro = ttk.Button(self.root, text="Cobrar", command=self.mostrarVentanaCobro)
        botonCobro.place(relx=0.05, rely=0.7, anchor=tk.CENTER)

    def mostrarVentanaAgendar(self):
        agendar_cita = agendarCita()
        agendar_cita.pantallaPrincipal()

    def mostrarVentanaInventario(self):
        myVentana = delInventario()
        myVentana.pantallaPrincipal()

    def mostrarVentanaCobro(self):
        # Obtener la fila seleccionada en la tabla
        seleccion = self.tree.selection()

        if seleccion:
            # Obtener los valores de la fila seleccionada
            values = self.tree.item(seleccion)['values']

            if values:
                # Obtener el nombre del barbero y la hora de la cita
                nombre_barbero = values[0]
                hora_cita = values[2]

                # Buscar el ID de la cita en la base de datos
                id_cita, id_servicio = self.obtenerIdCita(nombre_barbero, hora_cita)

                if id_cita:
                    print("ID de la Cita:", id_cita)
                    ventana_cobro = VentanaCobro(id_cita, self.dia_actual, id_servicio)
                    ventana_cobro.setSubtotalFinal(funcionpararetornarTotal())
                    ventana_cobro.realizarCobro()
                else:
                    print("No se encontró la cita en la base de datos.")
        else:
            print("Selecciona una fila antes de abrir la ventana de cobro.")

    def obtenerIdCita(self, nombre_barbero, hora_cita):

        if nombre_barbero == "Carlos Martínez":
            nombre_barbero = 1

        if nombre_barbero == "Ana González":
            nombre_barbero = 2

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

            # Ejecutar la consulta SQL para obtener el ID de la cita
            consulta = f"SELECT id_cita, id_servicio FROM citas_{self.dia_actual} WHERE id_barbero = %s and hora = %s;"
            cursor.execute(consulta,
                           (nombre_barbero, hora_cita ))

            # Obtener el resultado de la consulta
            resultado = cursor.fetchone()

            # Cerrar el cursor y la conexión
            cursor.close()
            connection.close()

            # Devolver el ID de la cita y el ID del servicio si se encontró, de lo contrario devolver (None, None)
            return resultado if resultado else (None, None)

        except (Exception, psycopg2.Error) as error:
            print("Error al obtener el ID de la cita:", error)
            return None
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