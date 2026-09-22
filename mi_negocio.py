from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
import json
import os
import urllib.parse

# Color de fondo oscuro profesional
Window.clearcolor = (0.1, 0.1, 0.1, 1)

# Inventario de tu negocio (Nombre : Stock Ideal deseado)
inventario_granmanjar = {
    "Servilletas": 2, "B. Salsera": 3, "Vasos 7oz": 2,
    "Palillo 20cm": 2, "Portaperros": 1, "Palillo Hamb.": 3,
    "B. Alum 5.5": 2, "Tenedores": 1, "Cuchillo": 1,
    "Papel Alum.": 1, "Parafinado": 2, "Paparapido": 2,
    "Bolsa 2kg": 2, "Bolsa 5kg": 2, "Bolsa 25kg": 1,
    "Salsa Roja": 1, "Mostaza": 1, "BBQ": 1, 
    "Icopor C1": 10, "Icopor K1": 10, "Icopor T1": 10, 
    "Icopor J1": 45, "Icopor J2": 45, "Icopor JL1": 45, 
    "Onoto": 2, "Pimienta": 2, "Canela": 2, "Sal": 1,
    "Bolsa 7x11": 3, "Jamón": 6, "Delichi": 3, "Tocineta": 2,
    "Pan Shawarma": 2, "Salchicha": 1, "Q. Costeño": 2, 
    "Mozzarella": 1, "Lechuga": 2, "Tomate": 9,
    "Cebolla Cab.": 9, "Cebolla Junca": 1, "Chorizo": 60,
    "Lomo": 10, "Carne Hamb.": 45, "Carne Desmech.": 6,
    "Pechuga": 4, "Maíz": 2, "Papa Francesa": 2,
    "Carne Res": 2, "Piña Prep.": 4, "Grillet": 3,
    "Panela (lb)": 2, "Piña Tomatico": 2, "Piña p/Prep": 2,
    "Pan Perro": 30, "Pan Hamb.": 40, "Aceite 20L": 2,
}

ARCHIVO_DATOS = "inventario_guardado.json"

class InventarioApp(App):
    def build(self):
        self.cajas_texto = {}
        self.datos_guardados = self.cargar_datos_locales()
        
        # Contenedor principal
        root = BoxLayout(orientation='vertical', padding=8, spacing=8)
        
        # Título principal
        titulo = Label(text="🛒 INVENTARIO GRAN MANJAR", font_size=42, bold=True, size_hint_y=None, height=65, color=(0.2, 0.7, 1, 1))
        root.add_widget(titulo)
        
        # ENCABEZADOS
        encabezados = GridLayout(cols=3, size_hint_y=None, height=50, spacing=5)
        encabezados.add_widget(Label(text="PRODUCTO", bold=True, font_size=32, color=(1, 1, 0, 1), size_hint_x=0.48))
        encabezados.add_widget(Label(text="¿HAY?", bold=True, font_size=32, color=(1, 1, 0, 1), size_hint_x=0.26))
        encabezados.add_widget(Label(text="FALTA", bold=True, font_size=32, color=(1, 0.5, 0, 1), size_hint_x=0.26))
        root.add_widget(encabezados)
        
        # Zona deslizable
        scroll = ScrollView(size_hint=(1, 1))
        grid = GridLayout(cols=3, spacing=5, size_hint_y=None, padding=5)
        grid.bind(minimum_height=grid.setter('height'))
        
        for producto, cantidad_ideal in inventario_granmanjar.items():
            
            # Columna 1: Nombre y stock ideal
            lbl_nombre = Label(text=f"{producto}\n(Ideal: {cantidad_ideal})", size_hint_y=None, height=110, size_hint_x=0.48, halign="left", valign="middle", font_size=36)
            lbl_nombre.bind(size=lbl_nombre.setter('text_size'))
            
            # Recuperar valor guardado previamente si existe
            valor_previo = str(self.datos_guardados.get(producto, ""))
            
            # Columna 2: Cuadro para escribir
            txt_hay = TextInput(text=valor_previo, input_filter='int', multiline=False, size_hint_y=None, height=85, font_size=40, halign="center", hint_text="0", size_hint_x=0.26)
            self.cajas_texto[producto] = txt_hay
            
            # Calcular faltante inicial según lo guardado
            try:
                val_ini = int(valor_previo) if valor_previo != "" else 0
            except:
                val_ini = 0
            falta_ini = cantidad_ideal - val_ini
            
            color_inicial = (1, 0.3, 0.3, 1) if falta_ini > 0 else (0.3, 1, 0.3, 1)
            texto_inicial = str(falta_ini) if falta_ini > 0 else "0"

            # Columna 3: Resultado numérico dinámico
            lbl_falta = Label(text=texto_inicial, size_hint_y=None, height=85, size_hint_x=0.26, font_size=42, bold=True, color=color_inicial)
            
            def crear_calculador(prod, ideal, lbl_resultado, app_instance):
                def calcular(instancia, valor):
                    try:
                        actual = int(valor) if valor != "" else 0
                    except:
                        actual = 0
                    
                    # Guardar automáticamente
                    app_instance.datos_guardados[prod] = actual
                    app_instance.guardar_datos_locales()

                    faltante = ideal - actual
                    if faltante > 0:
                        lbl_resultado.text = str(faltante)
                        lbl_resultado.color = (1, 0.3, 0.3, 1) # Rojo alerta
                    else:
                        lbl_resultado.text = "0"
                        lbl_resultado.color = (0.3, 1, 0.3, 1) # Verde OK
                return calcular
                
            txt_hay.bind(text=crear_calculador(producto, cantidad_ideal, lbl_falta, self))
            
            grid.add_widget(lbl_nombre)
            grid.add_widget(txt_hay)
            grid.add_widget(lbl_falta)
            
        scroll.add_widget(grid)
        root.add_widget(scroll)
        
        # Panel de Botones de Acción
        panel_botones = BoxLayout(orientation='horizontal', size_hint_y=None, height=70, spacing=8)
        
        btn_resumen = Button(text="📝 VER LISTA", background_color=(0, 0.5, 0.8, 1), bold=True, font_size=28)
        btn_resumen.bind(on_press=self.mostrar_resumen)
        
        btn_whatsapp = Button(text="💬 WHATSAPP", background_color=(0.1, 0.7, 0.3, 1), bold=True, font_size=28)
        btn_whatsapp.bind(on_press=self.enviar_whatsapp)

        btn_limpiar = Button(text="🗑️ LIMPIAR", background_color=(0.8, 0.2, 0.2, 1), bold=True, font_size=28)
        btn_limpiar.bind(on_press=self.limpiar_inventario)

        panel_botones.add_widget(btn_resumen)
        panel_botones.add_widget(btn_whatsapp)
        panel_botones.add_widget(btn_limpiar)
        root.add_widget(panel_botones)
        
        # Cuadro de resultados abajo
        self.resultado_txt = TextInput(text="Aquí saldrá la lista para comprar...", readonly=True, size_hint_y=None, height=140, font_size=26)
        root.add_widget(self.resultado_txt)
        
        return root

    def cargar_datos_locales(self):
        if os.path.exists(ARCHIVO_DATOS):
            try:
                with open(ARCHIVO_DATOS, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def guardar_datos_locales(self):
        try:
            with open(ARCHIVO_DATOS, "w") as f:
                json.dump(self.datos_guardados, f)
        except:
            pass
        
    def mostrar_resumen(self, instance):
        texto_resultado = "--- LISTA DE COMPRAS ---\n"
        faltan_cosas = False
        
        for producto, txt_input in self.cajas_texto.items():
            valor = txt_input.text
            cantidad_actual = int(valor) if valor != "" else 0
            cantidad_ideal = inventario_granmanjar[producto]
            
            if cantidad_actual < cantidad_ideal:
                comprar = cantidad_ideal - cantidad_actual
                texto_resultado += f"• {comprar} x {producto}\n"
                faltan_cosas = True
                
        if not faltan_cosas:
            texto_resultado = "¡Inventario completo! No falta nada."
            
        self.resultado_txt.text = texto_resultado

    def enviar_whatsapp(self, instance):
        self.mostrar_resumen(None)
        texto_a_enviar = self.resultado_txt.text
        texto_codificado = urllib.parse.quote(texto_a_enviar)
        import webbrowser
        webbrowser.open(f"https://api.whatsapp.com/send?text={texto_codificado}")

    def limpiar_inventario(self, instance):
        for producto, txt_input in self.cajas_texto.items():
            txt_input.text = ""
        if os.path.exists(ARCHIVO_DATOS):
            os.remove(ARCHIVO_DATOS)
        self.datos_guardados = {}
        self.resultado_txt.text = "Inventario borrado y reiniciado."

if __name__ == '__main__':
    InventarioApp().run()
