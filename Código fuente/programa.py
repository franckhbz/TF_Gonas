import tkinter as tk
from tkinter import ttk
import pandas as pd
from tkinter import *
from tkinter.ttk import *
import pandas as pd
import csv
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
import webbrowser
import urllib.parse

def examine_cocktails(graph, ingredients):
    possible_cocktails = []
    min_cantidad = float('inf')
    min_coctel = None
    for vertex in graph.keys():
        cocktail_ingredients = graph[vertex]
        if all(ingredient in ingredients and ingredients[ingredient][0] >= quantity for ingredient, quantity in cocktail_ingredients.items()):
            possible_cocktails.append(vertex)
        else:
            falta = sum(max(0, quantity - ingredients.get(ingredient, (0,))[0]) for ingredient, quantity in cocktail_ingredients.items())
            falta += sum(1 for ingredient in cocktail_ingredients if ingredient not in ingredients) * 1000
            if falta < min_cantidad:
                min_cantidad = falta
                min_coctel = vertex
    min_cantidad //= 1000
    return possible_cocktails, min_coctel, min_cantidad

def bfs(graph, cocktails):
    cola = deque(cocktails)
    min_cantidad = float('inf')
    min_coctel = None
    while cola:
        coctel = cola.popleft()
        if coctel in graph:
            cantidad = sum(graph[coctel].values()) + len(graph[coctel]) * 1000
            if cantidad < min_cantidad:
                min_cantidad = cantidad
                min_coctel = coctel
    min_cantidad //= 1000
    return min_coctel, min_cantidad
class AutocompleteEntry(ttk.Entry):
    def __init__(self, autocomplete_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.autocomplete_list = autocomplete_list
        self.var = self["textvariable"]
        if self.var == '':
            self.var = self["textvariable"] = tk.StringVar()

        self.var.trace('w', self.changed)
        self.bind("<Right>", self.selection)
        self.bind("<Return>", self.selection)
        self.bind("<Up>", self.move_up)
        self.bind("<Down>", self.move_down)
        self.lb_up = False

    def changed(self, name, index, mode):  
        if self.var.get() == '':
            if self.lb_up:
                self.lb.destroy()
                self.lb_up = False
        else:
            words = self.comparison()
            if words:            
                if not self.lb_up:
                    self.lb = tk.Listbox(width=50) 
                    self.lb.bind("<Double-Button-1>", self.selection)
                    self.lb.bind("<Right>", self.selection)
                    self.lb.place(x=self.winfo_x(), y=self.winfo_y()+self.winfo_height())
                    self.lb_up = True
                    
                self.lb.delete(0, 'end')
                for w in words:
                    self.lb.insert('end', w)
            else:
                if self.lb_up:
                    self.lb.destroy()
                    self.lb_up = False
        
    def selection(self, event):
        if self.lb_up:
            self.var.set(self.lb.get(tk.ACTIVE))
            self.lb.destroy()
            self.lb_up = False
            self.icursor(tk.END)
            self.event_generate("<<AutocompleteSelection>>")

    def move_up(self, event):
        if self.lb_up:
            if self.lb.curselection() == ():
                index = '0'
            else:
                index = self.lb.curselection()[0]
            if index != '0':
                self.lb.selection_clear(first=index)
                index = str(int(index)-1)                
                self.lb.selection_set(first=index)
                self.lb.activate(index) 

    def move_down(self, event):
        if self.lb_up:
            if self.lb.curselection() == ():
                index = '0'
            else:
                index = self.lb.curselection()[0]
            if index != tk.END:
                self.lb.selection_clear(first=index)
                index = str(int(index)+1)                
                self.lb.selection_set(first=index)
                self.lb.activate(index) 

    def comparison(self):
        user_input = self.var.get().lower() 
        return [w for w in self.autocomplete_list if user_input in w.lower()]


def v_menu(ingredient_list,measurement_dict):
   
    previa = tk.Tk()
    previa.title("Menu")
 
    ttk.Label(previa, text="Selecciona una opción").pack()
    ttk.Button(previa, text="Añadir Ingrediente", command=lambda: [previa.destroy(), v_aingrediente(ingredient_list,measurement_dict)]).pack()
    ttk.Button(previa, text="Mis ingredientes", command=lambda: [previa.destroy(), v_mis_ingredientes()]).pack()
    ttk.Button(previa, text="¿Que puedo preparar?", command=lambda: [previa.destroy(), v_que_puedo_preparar()]).pack()
    ttk.Button(previa, text="Evitar ingredientes", command=lambda: [previa.destroy(), v_evitar_ingredientes()]).pack()
    ancho_pantalla = previa.winfo_screenwidth()
    alto_pantalla = previa.winfo_screenheight()
    ancho_ventana = 300
    alto_ventana = 200

    x = (ancho_pantalla - ancho_ventana) // 2
    y = (alto_pantalla - alto_ventana) // 2

    previa.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")
    previa.mainloop()
def v_aingrediente(ingredient_list,measurement_dict):
    root = tk.Tk()
    root.title("Añadir Ingrediente")
    ttk.Label(root, text="Ingresa el nombre del ingrediente y su cantidad").place(x=110,y=7)
    unidades_text = tk.StringVar()
    unidades_entry = tk.Label(root, textvariable=unidades_text)
    unidades_entry.place(x=110,y=85)

    def select_ingredient(event=None):
        selected_ingredient = entry.get()

        if selected_ingredient in measurement_dict:
            unidades_text.set(measurement_dict[selected_ingredient])
        else:
            unidades_text.set("units")

    entry = AutocompleteEntry(ingredient_list, root, width=50)
    entry.place(x=20,y=30)
    entry.bind("<<AutocompleteSelection>>", select_ingredient)
    
    cantidad_entry = tk.Entry(root, width=10)
    cantidad_entry.place(x=40,y=85) 
    
    def añadir_ingrediente():
        selected_ingredient = entry.get()
        cantidad = cantidad_entry.get()
        unidad = unidades_text.get()
        try:
            cantidad = float(cantidad)
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            tk.messagebox.showerror("Error", "La cantidad debe ser un número mayor a 0")
            return

        if selected_ingredient and unidad:
            ingredientes[selected_ingredient] = (cantidad, unidad)
            
            entry.delete(0, 'end')
            cantidad_entry.delete(0, 'end')
            unidades_text.set("")
    boton=ttk.Button(text='Añadir', command=añadir_ingrediente).place(x=140, y=82)
    boton=ttk.Button(text="Mis ingredientes", command=lambda: [root.destroy(), v_mis_ingredientes()]).place(x=200, y=210)
    boton=ttk.Button(text='Volver al Menu', command=lambda: [root.destroy(), v_menu(ingredient_list,measurement_dict)]).place(x=200, y=240)
    
    ancho_pantalla = root.winfo_screenwidth()
    alto_pantalla = root.winfo_screenheight()
    ancho_ventana = 500
    alto_ventana = 300

    x = (ancho_pantalla - ancho_ventana) // 2
    y = (alto_pantalla - alto_ventana) // 2

    root.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")
    root.mainloop()
def v_mis_ingredientes():
    root = tk.Tk()
    root.title("Mis ingredientes")

    listbox = tk.Listbox(root,width=50)
    listbox.pack()

    for ingrediente, (cantidad, unidad) in ingredientes.items():
        listbox.insert('end', f"{ingrediente},{cantidad}{unidad}")
    
    def eliminar_ingrediente():
        selected_ingredient = listbox.get(listbox.curselection())
        if selected_ingredient:
            
            selected_ingredient = selected_ingredient.split(',')[0]
            listbox.delete(listbox.curselection())
            del ingredientes[selected_ingredient]

    ttk.Button(root, text='Eliminar', command=eliminar_ingrediente).pack()
    ttk.Button(root, text='Añadir Ingrediente', command=lambda: [root.destroy(), v_aingrediente(ingredient_list,measurement_dict)]).pack()
    ttk.Button(root, text='Volver al Menu', command=lambda: [root.destroy(), v_menu(ingredient_list,measurement_dict)]).pack()
   
    ancho_pantalla = root.winfo_screenwidth()
    alto_pantalla = root.winfo_screenheight()
    ancho_ventana = 500
    alto_ventana = 300

    x = (ancho_pantalla - ancho_ventana) // 2
    y = (alto_pantalla - alto_ventana) // 2

    root.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")
    root.mainloop()
def v_que_puedo_preparar():
    root = tk.Tk()
    root.title("¿Que puedo preparar?")
    listbox = tk.Listbox(root,width=50)
    listbox.pack()
    cocktails = []  
    cocktails, min_coctel, min_cantidad = examine_cocktails(graph, ingredientes)
    for cocktail in cocktails:
        listbox.insert('end', f"{cocktail}")

   
    def ver_receta():
        selected_index = listbox.curselection()  
        if selected_index:  
            selected_cocktail = cocktails[selected_index[0]] 
            v_recetas(selected_cocktail) 

    # Función para manejar el evento de click en "Gráfico Técnico"
    def mostrar_grafico():
        selected_index = listbox.curselection() 
        if selected_index:  
            selected_cocktail = cocktails[selected_index[0]]  
            graficotecnico(selected_cocktail)  

    ttk.Button(root, text='Ver Receta', command=lambda: [root.destroy(),ver_receta]).pack()  
    ttk.Button(root, text='Mostrar Gráfico Técnico', command=mostrar_grafico).pack()  
    ttk.Button(root, text='Coctel más eficiente', command=lambda: [root.destroy(), v_eficiente(cocktails,min_coctel, min_cantidad)]).pack()  
    ttk.Button(root, text='Volver al Menu', command=lambda: [root.destroy(), v_menu(ingredient_list,measurement_dict)]).pack()

    # Centrar la ventana en la pantalla
    ancho_pantalla = root.winfo_screenwidth()
    alto_pantalla = root.winfo_screenheight()
    ancho_ventana = 500
    alto_ventana = 300

    x = (ancho_pantalla - ancho_ventana) // 2
    y = (alto_pantalla - alto_ventana) // 2

    root.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")
    root.mainloop()

def v_evitar_ingredientes():
    root = tk.Tk()
    root.title("Evitar Ingrediente")
    entry = AutocompleteEntry(ingredient_list, root, width=50)
    entry.place(x=20,y=20)

    def eliminar_ingrediente_y_cocteles(ingrediente):
        
        cocteles_para_eliminar = []
        for coctel in graph:
            if ingrediente in graph[coctel]:
                cocteles_para_eliminar.append(coctel)

        # Eliminar los cócteles de la lista del grafo
        for coctel in cocteles_para_eliminar:
            del graph[coctel]
    def evitar_ingrediente():
        selected_ingredient = entry.get()

        if selected_ingredient:
            eliminar_ingrediente_y_cocteles(selected_ingredient)
            # Limpiar los campos de entrada
            entry.delete(0, 'end')

    boton=ttk.Button(text='Evitar', command=evitar_ingrediente).place(x=140, y=72)
    boton=ttk.Button(text='Volver al Menu', command=lambda: [root.destroy(), v_menu(ingredient_list, measurement_dict)]).place(x=200, y=240)
    # Centrar la ventana en la pantalla
    ancho_pantalla = root.winfo_screenwidth()
    alto_pantalla = root.winfo_screenheight()
    ancho_ventana = 500
    alto_ventana = 300

    x = (ancho_pantalla - ancho_ventana) // 2
    y = (alto_pantalla - alto_ventana) // 2

    root.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")
    root.mainloop()
def v_recetas(coctel):
    root = tk.Tk()
    root.title("Recetas")

    with open('Dataset\Recetafinal.csv', 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Ignoramos la primera fila (cabecera)
        for row in csv_reader:
            if row[0] == coctel:  # Solo mostramos la receta para el coctel seleccionado
                ttk.Label(root, text=row[0], font=("Helvetica", 16), wraplength=450).pack()  # Nombre del coctel
                ttk.Label(root, text=row[1], font=("Helvetica", 12), wraplength=450).pack()  # Ingredientes
                ttk.Label(root, text=row[2], font=("Helvetica", 12), wraplength=450).pack()  # Instrucciones
                break

    # Crear el enlace
    coctel_encoded = urllib.parse.quote(coctel)
    enlace = "https://mrbostondrinks.com/recipes/search?q=" + coctel_encoded
    ttk.Button(root, text="Ver receta en línea", command=lambda: webbrowser.open(enlace)).pack()

    ttk.Button(root, text="Regresar", command=lambda: [root.destroy(), v_que_puedo_preparar()]).pack()
    ttk.Button(root, text='Volver al Menu', command=lambda: [root.destroy(), v_menu(ingredient_list,measurement_dict)]).pack()

    # Centrar la ventana en la pantalla
    ancho_pantalla = root.winfo_screenwidth()
    alto_pantalla = root.winfo_screenheight()
    ancho_ventana = 500
    alto_ventana = 600
    x = (ancho_pantalla - ancho_ventana) // 2
    y = (alto_pantalla - alto_ventana) // 2

    root.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

    root.mainloop()

def graficotecnico(coctel):
    
    G = nx.DiGraph()
    for ingredient, quantity in graph[coctel].items():
        G.add_edge(coctel, ingredient, weight=quantity)
    fig = plt.figure(figsize=(6, 6))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1500, edge_cmap=plt.cm.Blues, font_size=12)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.show()
def v_eficiente(cocktails,min_coctel, min_cantidad):
    root = tk.Tk()
    root.title("Coctel más eficiente")

    listbox = tk.Listbox(root,width=50)
    listbox.pack()
    c_texto="Cantidad total de ingredientes"
    if  cocktails:
        coctel, cantidad = bfs(graph,cocktails)
    else:
        c_texto="Cantidad de ingredientes adicionales"
        coctel, cantidad=min_coctel, min_cantidad
    listbox.insert('end', f"{coctel}")
    tk.Label(root, text=f"{c_texto}: {cantidad}").pack()
    def ver_receta():
        selected_index = listbox.curselection() 
        if selected_index:  #
            selected_cocktail = listbox.get(selected_index)  
            v_recetas(selected_cocktail)  

    def mostrar_grafico():
        selected_index = listbox.curselection() 
        if selected_index:  
            selected_cocktail = listbox.get(selected_index)  
            graficotecnico(selected_cocktail)  

    ttk.Button(root, text='Ver Receta', command=ver_receta).pack()  
    ttk.Button(root, text='Mostrar Gráfico Técnico', command=mostrar_grafico).pack()  
    ttk.Button(root, text='Volver al Menu', command=lambda: [root.destroy(), v_menu(ingredient_list,measurement_dict)]).pack()

    ancho_pantalla = root.winfo_screenwidth()
    alto_pantalla = root.winfo_screenheight()
    ancho_ventana = 500
    alto_ventana = 300
    x = (ancho_pantalla - ancho_ventana) // 2
    y = (alto_pantalla - alto_ventana) // 2

    root.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")
    root.mainloop()



dingredientes = pd.read_csv('Dataset\Ingredientesyunidades.csv')
df = pd.read_csv('Dataset\Aristasgrafo.csv')

graph = {row['name']: {row2['ingredient']: row2['measurement'] for _, row2 in df[df['name'] == row['name']].iterrows()} for _, row in df.iterrows()}
#ingredientes del usuario
ingredientes = {}
# Obtener la lista de ingredientes
ingredient_list = dingredientes['ingredient'].tolist()
# Crear un diccionario para mapear ingredientes a unidades de medida
measurement_dict = dingredientes.set_index('ingredient')['unit'].to_dict()
v_menu(ingredient_list,measurement_dict)




