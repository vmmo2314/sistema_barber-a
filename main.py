import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from parteAgendar import agendarCita


class interfaz:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("1280x720")
        self.root.title("Barbería del Alexis :D")

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

    def mainMenu(self):
        # Etiquetas
        Menu_label = tk.Label(self.root, text="Barbería", font=("Helvetica", 15))
        Menu_label.place(relx=0.5, rely=.05, anchor=tk.CENTER)
        self.tablaPrincipal_Citas()
        self.cargarBotonesIzquierdos()
        self.root.mainloop()


        # Posicio
    def tablaPrincipal_Citas(self):
        # Configurar las columnas
        self.tree.heading("Nombre Barbero", text="Nombre Barbero")
        self.tree.heading("Nombre Cliente", text="Nombre Cliente")
        self.tree.heading("Hora", text="Hora")
        self.tree.heading("Servicio", text="Servicio")

        self.tree.place(relx=0.5, rely=0.5, width=1000, height=600, anchor=tk.CENTER)
        self.cargarTabla_citas()

    def cargarTabla_citas(self):
        # Insertar datos en la tabla (ejemplo)
        datos = [("Barbero 1", "Cliente 1", "10:00 AM", "Corte de pelo"),
                 ("Barbero 2", "Cliente 2", "11:30 AM", "Afeitado"),
                 ("Barbero 3", "Cliente 3", "02:15 PM", "Barba")]

        for dato in datos:
            self.tree.insert("", "end", values=dato)

    def cargarBotonesIzquierdos(self):
        self.style.configure("TButton", relief="flat", font=("Helvetica", 16))
        botonAgendar = ttk.Button(self.root, text="Agendar", command=self.mostrarVentanaAgendar)
        botonAgendar.place(relx=0.05, rely=0.3, anchor=tk.CENTER)

        botonInventario = ttk.Button(self.root, text="Inventario", command=lambda: print("Botón presionado"))
        botonInventario.place(relx=0.05, rely=0.5, anchor=tk.CENTER)
        #ejemplo de como poner un boton con imagen
        #botonAgendar = ttk.Button(self.root, image=self.imagenBarber1,command=lambda: print("Botón presionado"))

    def mostrarVentanaAgendar(self):
        agendar_cita = agendarCita()
        agendar_cita.pantallaPrincipal()




myInterfaz = interfaz()
myInterfaz.mainMenu()
