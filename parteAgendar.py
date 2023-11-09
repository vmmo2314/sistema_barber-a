import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

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

        self.treeAgenda = ttk.Treeview(self.root, columns=("Hora", "Servicio"), show="headings")
        self.treeAgenda.bind("<ButtonRelease-1>", self.actualizarDatosEntrada)

        # Establecer el tema del estilo
        self.style = ttk.Style()
        self.style.theme_use("xpnative")  # Puedes cambiar "clam" a otros temas como "default", "alt", "classic", etc.
        self.style.configure("TButton", relief="flat", font=("Helvetica", 16))
        # Estilo para el encabezado
        self.style.configure("Treeview.Heading", font=("Helvetica", 18, "bold"))

        self.style.configure("BotonListo.TButton", font=("Helvetica", 25), width=10, background="green")


        # Estilo para las filas
        self.style.configure("Treeview", font=("Helvetica", 12), rowheight=55, background="#f5f5f5")
        self.style.map("Treeview", background=[("selected", "#347083")])

        #cargar de imagen para boton
        self.imagenBarber1 = tk.PhotoImage(file="A:\\python\\actividades\\sistema_barberia\\Imagenes\\barbero1.png")
        self.imagenBarber1 = self.imagenBarber1.subsample(2, 2)  # Reduce a la mitad tanto la anchura como la altura

    def pantallaPrincipal(self):
        self.treeAgenda.heading("Hora", text="Hora")
        self.treeAgenda.heading("Servicio", text="Servicio")

        self.Advertencia = tk.Label(self.root, text= "Selecciona un barbero antes que todo...", font=("Helvetica", 12))
        self.Advertencia.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

        self.treeAgenda.place(relx=0.5, rely=0.5, width=1000, height=400, anchor=tk.CENTER)
        self.cargarCitas()
        self.cargarBotonesIzquierdos()
        self.ingresarDatosCliente()

    def cargarCitas(self):
        # Horarios disponibles
        horarios = [
            "11:00 AM", "",  # Espacio vacío para agendar cita
            "12:00 PM", "",  # Espacio vacío para agendar cita
            "01:00 PM", "",  # Espacio vacío para agendar cita
            "04:00 PM", "",  # Espacio vacío para agendar cita
            "05:00 PM", "",  # Espacio vacío para agendar cita
            "06:00 PM", "",  # Espacio vacío para agendar cita
            "07:00 PM", "",  # Espacio vacío para agendar cita
            "08:00 PM", ""  # Espacio vacío para agendar cita
        ]

        # Insertar datos en el Treeview
        for i in range(0, len(horarios), 2):
            self.treeAgenda.insert("", "end", values=(horarios[i], horarios[i + 1]))
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
        self.placeholder_Servicio = EntryWithPlaceholder(self.root, placeholder="Servicio", width=30, font=("Helvetica", 18))
        self.placeholder_Servicio.place(relx=0.55, rely=0.9, anchor=tk.CENTER)

        self.botonListo = ttk.Button(self.root, text="Listo", command=self.mandarDatosAlServer, style="BotonListo.TButton")
        self.botonListo.place(relx=0.9, rely=0.9, anchor=tk.CENTER)

    def mandarDatosAlServer(self):
        print("Los datos a mandar al server son:")
        print("barbero:", self.barberoSeleccionado)
        print("Nombre:", str(self.placeholder_Nombre.get()))
        print("Servicio:", str(self.placeholder_Servicio.get()))
        print("Hora:", str(self.treeAgenda.item(self.item, "values")[0]))


    def actualizarDatosEntrada(self, event):
        # Obtener la fila seleccionada del Treeview
        self.item = self.treeAgenda.selection()[0]

        # Obtener el servicio del cuadro de entrada
        servicio = self.placeholder_Servicio.get()

        # Verificar si se ha ingresado el servicio en el cuadro de entrada
        if servicio:
            # Actualizar la columna de "Servicio" en la fila seleccionada del Treeview
            self.treeAgenda.item(self.item, values=(self.treeAgenda.item(self.item, "values")[0], servicio))
        else:
            messagebox.showerror("Error", "Por favor, ingrese el servicio en el cuadro de entrada.")