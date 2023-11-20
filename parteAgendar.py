import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import psycopg2
import datetime

class EntryWithPlaceholder(tk.Entry):
    def __init__(self, master=None, placeholder="", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = "grey"
        self.default_fg_color = self["fg"]
        self.bind("<FocusIn>", self.on_entry_focus_in)
        self.bind("<FocusOut>", self.on_entry_focus_out)
        self.insert(0, self.placeholder)
        self.on_entry_focus_out(None)

    def on_entry_focus_in(self, event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self["fg"] = self.default_fg_color

    def on_entry_focus_out(self, event):
        if not self.get():
            self.insert(0, self.placeholder)
            self["fg"] = self.placeholder_color

class agendarCita:
    def __init__(self):
        self.root = tk.Toplevel()
        self.root.geometry("1280x720")
        self.root.title("Agendar cita")

        #Variable para saber el barbero seleccionado para la cita
        self.selectBarbero1 = tk.StringVar()
        self.selectBarbero2 = tk.StringVar()

        self.selectBarbero1.set("barbero 1")
        self.selectBarbero2.set("barbero 2")

        self.barberoSeleccionado = ""

        #booleanos saber día de la semana presionado
        self.dia1 = False
        self.dia2 = False
        self.dia3 = False
        self.dia4 = False
        self.dia5 = False
        self.dia6 = False

        # Agregar opciones de servicio predefinidas
        self.servicios = ["Corte de pelo", "Afeitado", "Coloración", "Manicura", "Tratamiento facial"]
        self.horarios = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"]

        # Configuración de la conexión a la base de datos
        self.connection = psycopg2.connect(
            user="postgres",
            password="usuario",
            host="localhost",
            port="5432",
            database="barberia_sistema"
        )
        self.cursor = self.connection.cursor()

        # Variable para almacenar el servicio seleccionado
        self.servicio_seleccionado = tk.StringVar()
        self.servicio_seleccionado.set(self.servicios[0])

        self.horario_seleccionado = tk.StringVar()
        self.horario_seleccionado.set(self.horarios[0])

        self.treeAgenda = ttk.Treeview(self.root, columns=("Hora", "Cliente"), show="headings")

        # Establecer el tema del estilo
        self.style = ttk.Style()
        self.style.theme_use("xpnative")
        self.style.configure("TButton", relief="flat", font=("Helvetica", 16))
        # Estilo para el encabezado
        self.style.configure("Treeview.Heading", font=("Helvetica", 18, "bold"))

        self.style.configure("BotonListo.TButton", font=("Helvetica", 25), width=10, background="green")


        # Estilo para las filas
        self.style.configure("Treeview", font=("Helvetica", 12), rowheight=55, background="#f5f5f5")
        self.style.map("Treeview", background=[("selected", "#347083")])

    def pantallaPrincipal(self):
        self.treeAgenda.heading("Hora", text="Hora")
        self.treeAgenda.heading("Cliente", text="Cliente")

        self.Advertencia = tk.Label(self.root, text= "Selecciona un barbero antes que todo...", font=("Helvetica", 12))
        self.Advertencia.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

        self.treeAgenda.place(relx=0.5, rely=0.5, width=1000, height=400, anchor=tk.CENTER)
        self.cargarCitas()
        self.botonesPorDia()
        self.cargarBotonesIzquierdos()
        self.ingresarDatosCliente()

    def insertarCita(self, nombre_cliente, servicio, hora, id_barbero, nombre_tabla):
        self.connection = psycopg2.connect(
            user="postgres",
            password="usuario",
            host="localhost",
            port="5432",
            database="barberia_sistema"
        )
        self.cursor = self.connection.cursor()

        # Obtener el id_servicio de la tabla de servicios
        select_query = "SELECT id_servicio FROM servicios WHERE nombre_servicio = %s;"
        self.cursor.execute(select_query, (servicio,))
        result = self.cursor.fetchone()

        if self.dia1:
            dia = "martes"
        elif self.dia2:
            dia = "miércoles"
        elif self.dia3:
            dia = "jueves"
        elif self.dia4:
            dia = "viernes"
        elif self.dia5:
            dia = "sábado"
        elif self.dia6:
            dia = "domingo"

        if result is not None:
            id_servicio = result[0]

            # Insertar datos en la tabla citas
            insert_query = f"INSERT INTO {nombre_tabla} (nombre_cliente, dia, id_servicio, hora, id_barbero) VALUES (%s, %s, %s, %s, %s);"
            self.cursor.execute(insert_query, (nombre_cliente, dia, id_servicio, hora, id_barbero))

            # Hacer commit para guardar los cambios
            self.connection.commit()

            messagebox.showinfo("Éxito", "Cita agendada exitosamente.")
        else:
            messagebox.showerror("Error", "Servicio no encontrado en la base de datos.")
        self.cursor.close()
        self.connection.close()

    def cargarCitas(self):
        if self.dia1:
            self.mostrarAgenda("citas_martes")
        elif self.dia2:
            self.mostrarAgenda("citas_miercoles")
        elif self.dia3:
            self.mostrarAgenda("citas_jueves")
        elif self.dia4:
            self.mostrarAgenda("citas_viernes")
        elif self.dia5:
            self.mostrarAgenda("citas_sabado")
        elif self.dia6:
            self.mostrarAgenda("citas_domingo")
        else:
            self.AdvertenciaDia = tk.Label(self.root, text="Selecciona un día de la semana",
                                           font=("Helvetica", 15))
            self.AdvertenciaDia.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            return

    def mostrarAgenda(self, nombre_tabla):
        if hasattr(self, "AdvertenciaDia"):
            self.AdvertenciaDia.destroy()
        self.AdvertenciaDia = tk.Label(self.root, text=f"Mostrando agenda del {nombre_tabla}",
                                       font=("Helvetica", 15))
        self.AdvertenciaDia.place(relx=0.5, rely=0.20, anchor=tk.CENTER)

        # Realizar consulta SQL para obtener datos de la tabla específica y filtrar por barbero
        consulta = f"SELECT hora, nombre_cliente FROM {nombre_tabla} WHERE id_barbero = %s;"
        self.cursor.execute(consulta, (1 if self.barberoSeleccionado == "barbero 1" else 2,))
        resultados = self.cursor.fetchall()

        # Verificar si hay resultados antes de procesarlos
        if not resultados:
            messagebox.showinfo("Info", "No hay citas programadas para este día.")
            return

        # Configurar horarios con datos de la consulta
        horarios = []
        for resultado in resultados:
            horarios.extend([resultado[0], resultado[1]])

        if self.treeAgenda:
            self.treeAgenda.destroy()

        self.treeAgenda = ttk.Treeview(self.root, columns=("Hora", "Cliente"), show="headings")
        self.treeAgenda.heading("Hora", text="Hora")
        self.treeAgenda.heading("Cliente", text="Cliente")
        self.treeAgenda.place(relx=0.5, rely=0.5, width=1000, height=400, anchor=tk.CENTER)

        # Insertar datos en el Treeview
        for i in range(0, len(horarios), 2):
            self.treeAgenda.insert("", "end", values=(horarios[i], horarios[i + 1]))


    def botonesPorDia(self):
        self.style.configure("TButton", relief="flat", font=("Helvetica", 17))
        self.diaMartesBoton = ttk.Button(self.root, text="M", command=self.presionarDia1,style="TButton", width=8)
        self.diaMartesBoton.place(relx=0.29, rely=0.80, anchor=tk.CENTER)

        self.diaMiercolesBoton = ttk.Button(self.root, text="Mie", command=self.presionarDia2, style="TButton", width=8)
        self.diaMiercolesBoton.place(relx=0.39, rely=0.80, anchor=tk.CENTER)

        self.diaJuevesBoton = ttk.Button(self.root, text="J", command=self.presionarDia3, style="TButton", width=8)
        self.diaJuevesBoton.place(relx=0.49, rely=0.80, anchor=tk.CENTER)

        self.diaViernesBoton = ttk.Button(self.root, text="V", command=self.presionarDia4,style="TButton", width=8)
        self.diaViernesBoton.place(relx=0.59, rely=0.80, anchor=tk.CENTER)

        self.diaSabadoBoton = ttk.Button(self.root, text="S", command=self.presionarDia5,style="TButton", width=8)
        self.diaSabadoBoton.place(relx=0.69, rely=0.80, anchor=tk.CENTER)

        self.diaDomingoBoton = ttk.Button(self.root, text="D", command=self.presionarDia6,style="TButton", width=8)
        self.diaDomingoBoton.place(relx=0.79, rely=0.80, anchor=tk.CENTER)

    def presionarDia1(self):
        self.dia1 = True
        self.dia2 = False
        self.dia3 = False
        self.dia4 = False
        self.dia5 = False
        self.dia6 = False
        self.cargarCitas()
    def presionarDia2(self):
        self.dia1 = False
        self.dia2 = True
        self.dia3 = False
        self.dia4 = False
        self.dia5 = False
        self.dia6 = False
        self.cargarCitas()

    def presionarDia3(self):
        self.dia1 = False
        self.dia2 = False
        self.dia3 = True
        self.dia4 = False
        self.dia5 = False
        self.dia6 = False
        self.cargarCitas()

    def presionarDia4(self):
        self.dia1 = False
        self.dia2 = False
        self.dia3 = False
        self.dia4 = True
        self.dia5 = False
        self.dia6 = False

        self.cargarCitas()

    def presionarDia5(self):
        self.dia1 = False
        self.dia2 = False
        self.dia3 = False
        self.dia4 = False
        self.dia5 = True
        self.dia6 = False
        self.cargarCitas()

    def presionarDia6(self):
        self.dia1 = False
        self.dia2 = False
        self.dia3 = False
        self.dia4 = False
        self.dia5 = False
        self.dia6 = True
        self.cargarCitas()

    def cargarBotonesIzquierdos(self):
        self.botonBarber1 = ttk.Button(self.root, text="barbero 1", command=self.barbero1Selected, style="TButton",
                                       textvariable=self.selectBarbero1)
        self.botonBarber1.place(relx=0.05, rely=0.3, anchor=tk.CENTER)

        self.botonBarber2 = ttk.Button(self.root, text="barbero 2", command=self.barbero2Selected, style="TButton",
                                       textvariable=self.selectBarbero2)
        self.botonBarber2.place(relx=0.05, rely=0.6, anchor=tk.CENTER)

    def barbero1Selected(self):
        self.Advertencia.destroy()
        self.barberoSeleccionado = "barbero 1"
        self.selectBarbero1.set("barbero 1")
        self.selectBarbero2.set("Seleccionar")


    def barbero2Selected(self):
        self.Advertencia.destroy()
        self.barberoSeleccionado = "barbero 2"
        self.selectBarbero2.set("barbero 2")
        self.selectBarbero1.set("Seleccionar")

    def ingresarDatosCliente(self):
        self.placeholder_Nombre = EntryWithPlaceholder(self.root, placeholder="Nombre del cliente", width=30, font=("Helvetica", 18))
        self.placeholder_Nombre.place(relx=0.2, rely=0.9, anchor=tk.CENTER)
        self.servicio_combobox = ttk.Combobox(self.root, textvariable=self.servicio_seleccionado, width=15,font=("Helvetica", 18), values=self.servicios)
        self.servicio_combobox.place(relx=0.45, rely=0.9, anchor=tk.CENTER)

        self.horario = ttk.Combobox(self.root, textvariable=self.horario_seleccionado, width=15,font=("Helvetica", 18), values=self.horarios)
        self.horario.place(relx=0.65, rely=0.9, anchor=tk.CENTER)

        self.botonListo = ttk.Button(self.root, text="Listo", command=self.mandarDatosAlServer, style="BotonListo.TButton")
        self.botonListo.place(relx=0.9, rely=0.9, anchor=tk.CENTER)

    def mandarDatosAlServer(self):
        nombre_cliente = str(self.placeholder_Nombre.get())
        servicio = str(self.servicio_seleccionado.get())
        hora = str(self.horario_seleccionado.get())

        # Obtener el id_barbero según el nombre seleccionado
        id_barbero = 1 if self.barberoSeleccionado == "barbero 1" else 2

        # Determinar qué día está seleccionado y llamar a la función insertarCita con el nombre de la tabla correspondiente
        if self.dia1:
            self.insertarCita(nombre_cliente, servicio, hora, id_barbero, "citas_martes")
        elif self.dia2:
            self.insertarCita(nombre_cliente, servicio, hora, id_barbero, "citas_miercoles")
        elif self.dia3:
            self.insertarCita(nombre_cliente, servicio, hora, id_barbero, "citas_jueves")
        elif self.dia4:
            self.insertarCita(nombre_cliente, servicio, hora, id_barbero, "citas_viernes")
        elif self.dia5:
            self.insertarCita(nombre_cliente, servicio, hora, id_barbero, "citas_sabado")
        elif self.dia6:
            self.insertarCita(nombre_cliente, servicio, hora, id_barbero, "citas_domingo")

        self.root.destroy()
