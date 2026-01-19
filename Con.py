import flet as ft
import json
import os
import datetime

class ConfiguracionContainer(ft.Container):
    def __init__(self, page, reloj_global, usuario_actual, rol_actual):
        super().__init__(expand=True)
        self.page = page
        self.reloj_global = reloj_global
        self.usuario_actual = usuario_actual
        self.rol_actual = rol_actual
        
        # Variables de estado
        self.en_pagina = False
        self.pendiente_actualizacion = False
        self.historial_completo = []
        
        # Inicializar UI
        self._initialize_ui()
        
        # Cargar datos iniciales
        self.cargar_historial()
        self.actualizar_tabla_historial()
    
    def _initialize_ui(self):
        """Inicializa todos los componentes de la UI de configuración"""
        # 1. CREAR TABLA DE HISTORIAL
        self.historial_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Hora", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Datos", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Fuente", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            heading_row_color=ft.Colors.BLUE_50,
            heading_row_height=50,
            data_row_color={"hovered": ft.Colors.GREY_100},
            show_checkbox_column=False,
        )
        
        # 2. BOTONES DE ACCIÓN PARA HISTORIAL
        self.btn_refrescar_historial = ft.ElevatedButton(
            text="Refrescar Historial",
            icon=ft.Icons.REFRESH,
            on_click=lambda e: self.cargar_historial(),
            width=200,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_700,
                color=ft.Colors.WHITE,
            )
        )
        
        self.btn_limpiar_historial = ft.ElevatedButton(
            text="Limpiar Historial",
            icon=ft.Icons.DELETE_SWEEP,
            on_click=self.confirmar_limpieza_historial,
            width=200,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.RED,
                color=ft.Colors.WHITE,
            )
        )
        
        # 3. BOTÓN DE GESTIÓN DE USUARIOS (SOLO PARA ADMIN)
        if self.rol_actual == "admin":
            self.btn_gestion_usuarios = ft.ElevatedButton(
                text="Gestión de Usuarios",
                icon=ft.Icons.PEOPLE,
                on_click=self.mostrar_gestion_usuarios,
                width=250,
                height=45,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.PURPLE_700,
                    color=ft.Colors.WHITE,
                )
            )
        else:
            self.btn_gestion_usuarios = ft.Container()  # Contenedor vacío para no admin
        
        # 4. CONTENEDOR DE CONFIGURACIÓN DEL RELOJ
        self.reloj_config_container = self._crear_reloj_config()
        
        # 5. CREAR LAYOUT PRINCIPAL
        self.main_column = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            controls=[
                # SECCIÓN 1: GESTIÓN DE USUARIOS (SOLO ADMIN)
                ft.Container(
                    padding=20,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=15,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=5,
                        color=ft.Colors.GREY_300,
                    ),
                    content=ft.Column(
                        spacing=15,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(
                                        ft.Icons.PEOPLE, 
                                        color=ft.Colors.PURPLE_700 if self.rol_actual == "admin" else ft.Colors.GREY_400, 
                                        size=28
                                    ),
                                    ft.Text(
                                        "Gestión de Usuarios",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.PURPLE_900 if self.rol_actual == "admin" else ft.Colors.GREY_500,
                                    ),
                                ],
                                spacing=10
                            ),
                            ft.Divider(),
                            ft.Text(
                                "Administra los usuarios del sistema. Solo usuarios administradores pueden acceder a esta sección.",
                                size=14,
                                color=ft.Colors.GREY_600 if self.rol_actual == "admin" else ft.Colors.GREY_400,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(
                                alignment=ft.alignment.center,
                                padding=ft.padding.only(top=10),
                                content=self.btn_gestion_usuarios,
                            ),
                        ]
                    ),
                    visible=self.rol_actual == "admin"  # Solo visible para admin
                ),
                
                # SECCIÓN 2: CONFIGURACIÓN DEL RELOJ
                self.reloj_config_container,
                
                # SECCIÓN 3: HISTORIAL DE REGISTROS
                ft.Container(
                    padding=20,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=15,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=5,
                        color=ft.Colors.GREY_300,
                    ),
                    content=ft.Column(
                        spacing=15,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(ft.Icons.HISTORY, color=ft.Colors.BLUE_700, size=28),
                                    ft.Text(
                                        "Historial de Registros",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.BLUE_900
                                    ),
                                ],
                                spacing=10
                            ),
                            ft.Divider(),
                            ft.Text(
                                f"Últimos registros del sistema ({datetime.datetime.now().strftime('%d/%m/%Y')})",
                                size=14,
                                color=ft.Colors.GREY_600,
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=20,
                                controls=[
                                    self.btn_refrescar_historial,
                                    self.btn_limpiar_historial,
                                ]
                            ),
                            ft.Container(
                                height=400,
                                border=ft.border.all(1, ft.Colors.GREY_300),
                                border_radius=10,
                                padding=10,
                                content=ft.Column(
                                    scroll=ft.ScrollMode.AUTO,
                                    controls=[
                                        self.historial_table
                                    ]
                                )
                            ),
                        ]
                    )
                ),
            ]
        )
        
        self.content = self.main_column
    
    def _crear_reloj_config(self):
        """Crea la sección de configuración del reloj"""
        # Lista de horas registradas
        self.lista_horas = ft.ListView(
            spacing=10,
            height=200,
        )
        
        # Campo para agregar nueva hora
        self.nueva_hora_input = ft.TextField(
            label="Nueva hora (HH:MM)",
            hint_text="Ej: 08:00",
            prefix_icon=ft.Icons.ACCESS_TIME,
            width=200,
        )
        
        self.btn_agregar_hora = ft.ElevatedButton(
            text="Agregar Hora",
            icon=ft.Icons.ADD,
            on_click=self.agregar_hora,
            width=200,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN,
                color=ft.Colors.WHITE,
            )
        )
        
        return ft.Container(
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.Colors.GREY_300,
            ),
            content=ft.Column(
                spacing=15,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.ACCESS_TIME, color=ft.Colors.TEAL_700, size=28),
                            ft.Text(
                                "Configuración del Reloj Automático",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.TEAL_900
                            ),
                        ],
                        spacing=10
                    ),
                    ft.Divider(),
                    ft.Text(
                        "Horas programadas para registro automático:",
                        size=14,
                        color=ft.Colors.GREY_600,
                    ),
                    ft.Container(
                        height=200,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=10,
                        padding=10,
                        content=self.lista_horas
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20,
                        controls=[
                            self.nueva_hora_input,
                            self.btn_agregar_hora,
                        ]
                    ),
                ]
            )
        )
    
    # ============================
    # MÉTODOS PARA GESTIÓN DE USUARIOS
    # ============================
    
    def mostrar_gestion_usuarios(self, e):
        """Muestra el diálogo de gestión de usuarios"""
        print("Abriendo gestión de usuarios...")
        
        # Cargar usuarios actuales
        self.cargar_usuarios()
        
        # Crear lista de usuarios
        self.lista_usuarios_ui = ft.ListView(
            expand=True,
            spacing=10,
            padding=10,
        )
        
        # Actualizar lista
        self.actualizar_lista_usuarios_ui()
        
        # Crear diálogo
        self.dialogo_usuarios = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.PEOPLE, color=ft.Colors.PURPLE_700, size=30),
                    ft.Text("Gestión de Usuarios", size=24, weight=ft.FontWeight.BOLD),
                ],
                spacing=15,
            ),
            content=ft.Container(
                width=800,
                height=500,
                content=ft.Column(
                    expand=True,
                    spacing=15,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(
                                    f"Administrador: {self.usuario_actual}",
                                    size=16,
                                    color=ft.Colors.GREEN_700,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    f"Total usuarios: {len(self.usuarios)}",
                                    size=16,
                                    color=ft.Colors.BLUE_700,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ]
                        ),
                        ft.Divider(),
                        
                        # Botones de acción
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=20,
                            controls=[
                                ft.ElevatedButton(
                                    text="➕ Nuevo Usuario",
                                    icon=ft.Icons.PERSON_ADD,
                                    on_click=self.mostrar_dialogo_nuevo_usuario,
                                    width=200,
                                    height=45,
                                    style=ft.ButtonStyle(
                                        bgcolor=ft.Colors.GREEN_700,
                                        color=ft.Colors.WHITE,
                                    )
                                ),
                                ft.ElevatedButton(
                                    text="🔄 Actualizar Lista",
                                    icon=ft.Icons.REFRESH,
                                    on_click=lambda e: self.actualizar_lista_usuarios_ui(),
                                    width=200,
                                    height=45,
                                    style=ft.ButtonStyle(
                                        bgcolor=ft.Colors.BLUE_700,
                                        color=ft.Colors.WHITE,
                                    )
                                ),
                            ]
                        ),
                        
                        # Lista de usuarios
                        ft.Container(
                            expand=True,
                            border=ft.border.all(1, ft.Colors.GREY_300),
                            border_radius=10,
                            padding=5,
                            content=self.lista_usuarios_ui
                        ),
                    ]
                )
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=self.cerrar_gestion_usuarios),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = self.dialogo_usuarios
        self.dialogo_usuarios.open = True
        self.page.update()
    
    def cargar_usuarios(self):
        """Carga los usuarios desde el archivo JSON"""
        usuarios_file = "usuarios.json"
        try:
            if os.path.exists(usuarios_file):
                with open(usuarios_file, "r") as f:
                    self.usuarios = json.load(f)
                print(f"✅ Usuarios cargados: {len(self.usuarios)} usuarios")
            else:
                # Crear archivo con admin por defecto
                self.usuarios = {
                    "admin": {
                        "password": "admin123",
                        "rol": "admin"
                    }
                }
                with open(usuarios_file, "w") as f:
                    json.dump(self.usuarios, f, indent=2)
                print("✅ Archivo de usuarios creado con usuario admin")
        except Exception as e:
            print(f"❌ Error cargando usuarios: {e}")
            self.usuarios = {}
    
    def guardar_usuarios(self):
        """Guarda los usuarios en el archivo JSON"""
        usuarios_file = "usuarios.json"
        try:
            with open(usuarios_file, "w") as f:
                json.dump(self.usuarios, f, indent=2)
            print("✅ Usuarios guardados exitosamente")
            return True
        except Exception as e:
            print(f"❌ Error guardando usuarios: {e}")
            return False
    
    def actualizar_lista_usuarios_ui(self, e=None):
        """Actualiza la lista de usuarios en la interfaz"""
        self.cargar_usuarios()  # Recargar datos
        
        if not hasattr(self, 'lista_usuarios_ui'):
            return
        
        self.lista_usuarios_ui.controls.clear()
        
        for usuario, datos in self.usuarios.items():
            es_admin = datos.get('rol') == 'admin'
            es_usuario_actual = usuario == self.usuario_actual
            
            # Determinar colores según rol y usuario actual
            if es_usuario_actual:
                color_fondo = ft.Colors.GREEN_100
                borde_color = ft.Colors.GREEN_400
                texto_usuario = f"👑 {usuario} (Tú)"
            elif es_admin:
                color_fondo = ft.Colors.PURPLE_50
                borde_color = ft.Colors.PURPLE_300
                texto_usuario = f"👑 {usuario}"
            else:
                color_fondo = ft.Colors.BLUE_50
                borde_color = ft.Colors.BLUE_300
                texto_usuario = f"👤 {usuario}"
            
            # Crear tarjeta de usuario
            tarjeta = ft.Card(
                elevation=3,
                content=ft.Container(
                    padding=15,
                    bgcolor=color_fondo,
                    border=ft.border.all(2, borde_color),
                    border_radius=10,
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            # Fila 1: Información del usuario
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        spacing=10,
                                        controls=[
                                            ft.Icon(
                                                ft.Icons.PERSON,
                                                color=ft.Colors.BLUE_700 if not es_usuario_actual else ft.Colors.GREEN_700,
                                                size=24
                                            ),
                                            ft.Column(
                                                spacing=2,
                                                controls=[
                                                    ft.Text(
                                                        texto_usuario,
                                                        size=18,
                                                        weight=ft.FontWeight.BOLD,
                                                        color=ft.Colors.BLUE_900 if not es_usuario_actual else ft.Colors.GREEN_900,
                                                    ),
                                                    ft.Text(
                                                        f"Rol: {'Administrador' if es_admin else 'Usuario normal'}",
                                                        size=14,
                                                        color=ft.Colors.GREY_600,
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                    ft.Container(
                                        content=ft.Text(
                                            "Administrador" if es_admin else "Usuario",
                                            color=ft.Colors.WHITE,
                                            size=12,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        bgcolor=ft.Colors.PURPLE if es_admin else ft.Colors.BLUE,
                                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                                        border_radius=20,
                                    ),
                                ]
                            ),
                            
                            # Fila 2: Botones de acción
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=10,
                                controls=self._crear_botones_usuario(usuario, datos, es_usuario_actual)
                            ),
                        ]
                    )
                )
            )
            
            self.lista_usuarios_ui.controls.append(tarjeta)
        
        self.lista_usuarios_ui.update()
    
    def _crear_botones_usuario(self, usuario, datos, es_usuario_actual):
        """Crea los botones de acción para cada usuario"""
        botones = []
        
        # Botón Cambiar Rol (excepto para usuario actual)
        if not es_usuario_actual:
            nuevo_rol = "usuario" if datos.get('rol') == 'admin' else "admin"
            texto_boton = "👉 Hacer Usuario" if datos.get('rol') == 'admin' else "👑 Hacer Admin"
            
            botones.append(
                ft.ElevatedButton(
                    text=texto_boton,
                    icon=ft.Icons.SWAP_HORIZ,
                    on_click=lambda e, u=usuario: self.cambiar_rol_usuario(u),
                    width=180,
                    height=35,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.ORANGE_700,
                        color=ft.Colors.WHITE,
                    )
                )
            )
        
        # Botón Cambiar Contraseña (siempre disponible)
        botones.append(
            ft.ElevatedButton(
                text="🔐 Cambiar Contraseña",
                icon=ft.Icons.LOCK_RESET,
                on_click=lambda e, u=usuario: self.mostrar_dialogo_cambiar_contrasena(u),
                width=200,
                height=35,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.PURPLE_700,
                    color=ft.Colors.WHITE,
                )
            )
        )
        
        # Botón Eliminar (excepto para usuario actual y último admin)
        if not es_usuario_actual:
            # Verificar si es el último admin
            admins = [u for u, d in self.usuarios.items() if d.get('rol') == 'admin']
            puede_eliminar = not (datos.get('rol') == 'admin' and len(admins) <= 1)
            
            if puede_eliminar:
                botones.append(
                    ft.ElevatedButton(
                        text="🗑️ Eliminar",
                        icon=ft.Icons.DELETE,
                        on_click=lambda e, u=usuario: self.mostrar_dialogo_eliminar_usuario(u),
                        width=120,
                        height=35,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.RED_700,
                            color=ft.Colors.WHITE,
                        )
                    )
                )
        
        return botones
    
    def mostrar_dialogo_nuevo_usuario(self, e):
        """Muestra diálogo para crear nuevo usuario"""
        # Campos del formulario
        self.nuevo_usuario_nombre = ft.TextField(
            label="Nombre de usuario",
            hint_text="mín. 3 caracteres",
            prefix_icon=ft.Icons.PERSON_ADD,
            width=300,
            autofocus=True,
        )
        
        self.nuevo_usuario_contrasena = ft.TextField(
            label="Contraseña",
            hint_text="mín. 6 caracteres",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK,
            width=300,
        )
        
        self.nuevo_usuario_confirmar = ft.TextField(
            label="Confirmar contraseña",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK,
            width=300,
        )
        
        self.nuevo_usuario_rol = ft.Dropdown(
            label="Rol del usuario",
            width=300,
            options=[
                ft.dropdown.Option("usuario", "Usuario Normal"),
                ft.dropdown.Option("admin", "Administrador"),
            ],
            value="usuario",
            hint_text="Seleccione un rol",
        )
        
        self.error_text_nuevo = ft.Text("", color=ft.Colors.RED, size=12)
        
        def crear_usuario(e):
            usuario = self.nuevo_usuario_nombre.value.strip()
            contrasena = self.nuevo_usuario_contrasena.value.strip()
            confirmar = self.nuevo_usuario_confirmar.value.strip()
            rol = self.nuevo_usuario_rol.value
            
            # Validaciones
            if not usuario or len(usuario) < 3:
                self.error_text_nuevo.value = "El nombre debe tener al menos 3 caracteres"
                self.page.update()
                return
            
            if not contrasena or len(contrasena) < 6:
                self.error_text_nuevo.value = "La contraseña debe tener al menos 6 caracteres"
                self.page.update()
                return
            
            if contrasena != confirmar:
                self.error_text_nuevo.value = "Las contraseñas no coinciden"
                self.page.update()
                return
            
            if usuario in self.usuarios:
                self.error_text_nuevo.value = "El usuario ya existe"
                self.page.update()
                return
            
            # Crear nuevo usuario
            self.usuarios[usuario] = {
                'password': contrasena,
                'rol': rol
            }
            
            if self.guardar_usuarios():
                self.actualizar_lista_usuarios_ui()
                dlg.open = False
                self.page.update()
                self.mostrar_mensaje(f"✅ Usuario '{usuario}' creado exitosamente", ft.Colors.GREEN)
            else:
                self.error_text_nuevo.value = "Error al guardar el usuario"
                self.page.update()
        
        def cancelar(e):
            dlg.open = False
            self.page.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("➕ Crear Nuevo Usuario"),
            content=ft.Column(
                width=400,
                spacing=15,
                controls=[
                    self.nuevo_usuario_nombre,
                    self.nuevo_usuario_contrasena,
                    self.nuevo_usuario_confirmar,
                    self.nuevo_usuario_rol,
                    self.error_text_nuevo,
                ]
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.ElevatedButton(
                    "Crear Usuario",
                    on_click=crear_usuario,
                    bgcolor=ft.Colors.GREEN,
                    color=ft.Colors.WHITE,
                ),
            ],
        )
        
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
    
    def cambiar_rol_usuario(self, usuario):
        """Cambia el rol de un usuario"""
        if usuario not in self.usuarios:
            self.mostrar_mensaje(f"❌ Usuario '{usuario}' no encontrado", ft.Colors.RED)
            return
        
        nuevo_rol = "usuario" if self.usuarios[usuario].get('rol') == 'admin' else "admin"
        texto_rol = "Usuario Normal" if nuevo_rol == "usuario" else "Administrador"
        
        def confirmar_cambio(e):
            self.usuarios[usuario]['rol'] = nuevo_rol
            if self.guardar_usuarios():
                self.actualizar_lista_usuarios_ui()
                dlg.open = False
                self.page.update()
                self.mostrar_mensaje(f"✅ Rol de '{usuario}' cambiado a {texto_rol}", ft.Colors.GREEN)
            else:
                self.mostrar_mensaje("❌ Error al guardar cambios", ft.Colors.RED)
        
        def cancelar(e):
            dlg.open = False
            self.page.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("🔄 Cambiar Rol de Usuario"),
            content=ft.Text(
                f"¿Cambiar rol de '{usuario}' a '{texto_rol}'?\n\n"
                f"Actual: {'Administrador' if self.usuarios[usuario].get('rol') == 'admin' else 'Usuario Normal'}\n"
                f"Nuevo: {texto_rol}"
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.ElevatedButton(
                    "Confirmar Cambio",
                    on_click=confirmar_cambio,
                    bgcolor=ft.Colors.ORANGE,
                    color=ft.Colors.WHITE,
                ),
            ],
        )
        
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
    
    def mostrar_dialogo_cambiar_contrasena(self, usuario):
        """Muestra diálogo para cambiar contraseña de usuario"""
        if usuario not in self.usuarios:
            self.mostrar_mensaje(f"❌ Usuario '{usuario}' no encontrado", ft.Colors.RED)
            return
        
        # Campos del formulario
        nueva_contrasena = ft.TextField(
            label="Nueva contraseña",
            hint_text="mín. 6 caracteres",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_RESET,
            width=300,
            autofocus=True,
        )
        
        confirmar_contrasena = ft.TextField(
            label="Confirmar contraseña",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK,
            width=300,
        )
        
        error_text = ft.Text("", color=ft.Colors.RED, size=12)
        
        def aplicar_cambio(e):
            contrasena = nueva_contrasena.value.strip()
            confirmar = confirmar_contrasena.value.strip()
            
            if not contrasena or len(contrasena) < 6:
                error_text.value = "La contraseña debe tener al menos 6 caracteres"
                self.page.update()
                return
            
            if contrasena != confirmar:
                error_text.value = "Las contraseñas no coinciden"
                self.page.update()
                return
            
            self.usuarios[usuario]['password'] = contrasena
            
            if self.guardar_usuarios():
                dlg.open = False
                self.page.update()
                self.mostrar_mensaje(f"✅ Contraseña de '{usuario}' actualizada", ft.Colors.GREEN)
            else:
                error_text.value = "Error al guardar la contraseña"
                self.page.update()
        
        def cancelar(e):
            dlg.open = False
            self.page.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"🔐 Cambiar Contraseña de {usuario}"),
            content=ft.Column(
                width=400,
                spacing=15,
                controls=[
                    nueva_contrasena,
                    confirmar_contrasena,
                    error_text,
                ]
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.ElevatedButton(
                    "Aplicar Cambio",
                    on_click=aplicar_cambio,
                    bgcolor=ft.Colors.GREEN,
                    color=ft.Colors.WHITE,
                ),
            ],
        )
        
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
    
    def mostrar_dialogo_eliminar_usuario(self, usuario):
        """Muestra diálogo para eliminar usuario"""
        if usuario not in self.usuarios:
            self.mostrar_mensaje(f"❌ Usuario '{usuario}' no encontrado", ft.Colors.RED)
            return
        
        # Verificar si es el último admin
        admins = [u for u, d in self.usuarios.items() if d.get('rol') == 'admin']
        if self.usuarios[usuario].get('rol') == 'admin' and len(admins) <= 1:
            self.mostrar_mensaje("❌ No puedes eliminar el único administrador", ft.Colors.RED)
            return
        
        def confirmar_eliminar(e):
            del self.usuarios[usuario]
            if self.guardar_usuarios():
                self.actualizar_lista_usuarios_ui()
                dlg.open = False
                self.page.update()
                self.mostrar_mensaje(f"✅ Usuario '{usuario}' eliminado", ft.Colors.GREEN)
            else:
                self.mostrar_mensaje("❌ Error al eliminar usuario", ft.Colors.RED)
        
        def cancelar(e):
            dlg.open = False
            self.page.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("🗑️ Eliminar Usuario"),
            content=ft.Text(
                f"¿Está seguro que desea eliminar al usuario '{usuario}'?\n\n"
                f"Rol: {'Administrador' if self.usuarios[usuario].get('rol') == 'admin' else 'Usuario Normal'}\n\n"
                f"⚠️ Esta acción no se puede deshacer."
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.ElevatedButton(
                    "Eliminar",
                    on_click=confirmar_eliminar,
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE,
                ),
            ],
        )
        
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
    
    def cerrar_gestion_usuarios(self, e):
        """Cierra el diálogo de gestión de usuarios"""
        if hasattr(self, 'dialogo_usuarios'):
            self.dialogo_usuarios.open = False
            self.page.update()
    
    # ============================
    # MÉTODOS PARA GESTIÓN DE HISTORIAL
    # ============================
    
    def actualizar_historial_desde_externo(self, registro=None):
        """Actualiza el historial cuando se recibe una notificación externa"""
        print(f"📥 Configuración: Recibida actualización de historial")
        
        if self.en_pagina:
            # Si estamos en la página, actualizar inmediatamente
            self.cargar_historial()
            self.actualizar_tabla_historial()
            print(f"✅ Historial actualizado en tiempo real")
        else:
            # Marcar que hay actualización pendiente
            self.pendiente_actualizacion = True
    
    def entrar_a_pagina(self):
        """Se llama cuando el usuario entra a la página de configuración"""
        self.en_pagina = True
        
        # Si hay actualizaciones pendientes, cargar historial
        if self.pendiente_actualizacion:
            self.cargar_historial()
            self.actualizar_tabla_historial()
            self.pendiente_actualizacion = False
        
        print(f"🔧 Configuración: Entrando a página")
    
    def salir_de_pagina(self):
        """Se llama cuando el usuario sale de la página de configuración"""
        self.en_pagina = False
        print(f"🔧 Configuración: Saliendo de página")
    
    def cargar_historial(self):
        """Carga el historial desde el archivo JSON"""
        try:
            if os.path.exists(self.reloj_global.archivo_historial):
                with open(self.reloj_global.archivo_historial, "r") as file:
                    self.historial_completo = json.load(file)
                
                # Ordenar por fecha y hora más recientes primero
                self.historial_completo.sort(
                    key=lambda x: datetime.datetime.strptime(
                        f"{x['fecha']} {x['hora']}", "%d/%m/%y %H:%M"
                    ), 
                    reverse=True
                )
                
                print(f"📊 Historial cargado: {len(self.historial_completo)} registros")
                
                # Actualizar la tabla
                self.actualizar_tabla_historial()
                
                return True
            else:
                self.historial_completo = []
                print("📊 No existe archivo de historial")
                return False
                
        except Exception as e:
            print(f"❌ Error cargando historial: {e}")
            self.historial_completo = []
            return False
    
    def actualizar_tabla_historial(self):
        """Actualiza la tabla de historial con los datos cargados"""
        if not hasattr(self, 'historial_table'):
            return
        
        # Limpiar filas existentes
        self.historial_table.rows.clear()
        
        # Agregar filas con los datos
        for registro in self.historial_completo[:50]:  # Mostrar solo los últimos 50
            datos = registro['datos']
            datos_str = f"🌡️ {datos.get('temperatura', 'N/A')}°C | "
            datos_str += f"💧 {datos.get('humedad', 'N/A')}% | "
            datos_str += f"📊 {datos.get('presion1', 'N/A')}/{datos.get('presion2', 'N/A')}/{datos.get('presion3', 'N/A')}Pa"
            
            # Determinar color según tipo
            if registro['tipo'] == 'registro_manual':
                tipo_color = ft.Colors.GREEN_700
                tipo_icono = "👆"
            elif registro['tipo'] == 'registro_automatico':
                tipo_color = ft.Colors.BLUE_700
                tipo_icono = "⏰"
            else:
                tipo_color = ft.Colors.GREY_700
                tipo_icono = "📝"
            
            self.historial_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(registro['fecha'])),
                        ft.DataCell(ft.Text(registro['hora'])),
                        ft.DataCell(ft.Text(datos_str)),
                        ft.DataCell(
                            ft.Text(f"{tipo_icono} {registro['tipo']}", color=tipo_color)
                        ),
                        ft.DataCell(ft.Text(registro['fuente'])),
                    ]
                )
            )
        
        self.historial_table.update()
    
    def confirmar_limpieza_historial(self, e):
        """Confirma la limpieza del historial"""
        def limpiar(e):
            self.reloj_global.limpiar_historial()
            self.cargar_historial()
            dlg.open = False
            self.page.update()
            self.mostrar_mensaje("✅ Historial limpiado completamente", ft.Colors.GREEN)
        
        def cancelar(e):
            dlg.open = False
            self.page.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("⚠️ Confirmar Limpieza"),
            content=ft.Text(
                "¿Está seguro que desea eliminar TODOS los registros del historial?\n\n"
                "Se eliminarán todos los registros guardados.\n"
                "Esta acción no se puede deshacer."
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.ElevatedButton(
                    "Limpiar Todo", 
                    on_click=limpiar,
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE
                ),
            ],
        )
        
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
    
    # ============================
    # MÉTODOS PARA CONFIGURACIÓN DEL RELOJ
    # ============================
    
    def agregar_hora(self, e):
        """Agrega una nueva hora al reloj automático"""
        hora_texto = self.nueva_hora_input.value.strip()
        
        try:
            hora_time = datetime.datetime.strptime(hora_texto, "%H:%M").time()
            
            if self.reloj_global.agregar_hora(hora_time):
                self.mostrar_mensaje(f"✅ Hora {hora_time.strftime('%I:%M %p')} agregada", ft.Colors.GREEN)
                self.nueva_hora_input.value = ""
                self.actualizar_lista_horas()
            else:
                self.mostrar_mensaje("⚠️ Esta hora ya está registrada", ft.Colors.ORANGE)
                
        except ValueError:
            self.mostrar_mensaje("❌ Formato inválido. Use HH:MM (ej: 08:30)", ft.Colors.RED)
        
        self.page.update()
    
    def actualizar_lista_horas(self):
        """Actualiza la lista de horas programadas"""
        if not hasattr(self, 'lista_horas'):
            return
        
        self.lista_horas.controls.clear()
        
        for hora in sorted(self.reloj_global.horas_registradas):
            hora_str = hora.strftime("%I:%M %p")
            
            tarjeta_hora = ft.Card(
                elevation=2,
                content=ft.Container(
                    padding=10,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.Icon(ft.Icons.ACCESS_TIME, color=ft.Colors.BLUE_700),
                                    ft.Text(hora_str, size=16, weight=ft.FontWeight.BOLD),
                                ]
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.RED,
                                tooltip="Eliminar hora",
                                on_click=lambda e, h=hora: self.eliminar_hora(h),
                            )
                        ]
                    )
                )
            )
            
            self.lista_horas.controls.append(tarjeta_hora)
        
        self.lista_horas.update()
    
    def eliminar_hora(self, hora):
        """Elimina una hora del reloj automático"""
        if self.reloj_global.eliminar_hora(hora):
            self.mostrar_mensaje(f"✅ Hora {hora.strftime('%I:%M %p')} eliminada", ft.Colors.GREEN)
            self.actualizar_lista_horas()
        else:
            self.mostrar_mensaje("❌ Error al eliminar la hora", ft.Colors.RED)
    
    # ============================
    # MÉTODOS UTILITARIOS
    # ============================
    
    def mostrar_mensaje(self, mensaje, color):
        """Muestra un mensaje de notificación"""
        snackbar = ft.SnackBar(
            content=ft.Text(mensaje, color=ft.Colors.WHITE),
            bgcolor=color,
            duration=2000,
        )
        self.page.snack_bar = snackbar
        snackbar.open = True
        self.page.update()
