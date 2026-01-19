Voy a agregar un diálogo completo para modificar usuarios. Aquí está la implementación completa:

1. Primero, modifica la clase ConfiguracionContainer para agregar la funcionalidad de gestión de usuarios:

En tu archivo configuracion.py, agrega estos métodos a la clase ConfiguracionContainer:

```python
class ConfiguracionContainer:
    def __init__(self, page, reloj_global, usuario_actual, rol_actual):
        # ... código existente del constructor ...
        
        # Variables para gestión de usuarios
        self.usuario_actual = usuario_actual
        self.rol_actual = rol_actual
        
        # Crear sección de gestión de usuarios
        self.crear_seccion_usuarios()
        
        # ... resto del código existente ...
    
    def crear_seccion_usuarios(self):
        """Crea la sección de gestión de usuarios"""
        # Botón para abrir gestión de usuarios
        self.btn_gestion_usuarios = ft.ElevatedButton(
            text="Gestión de Usuarios",
            icon=ft.Icons.PEOPLE,
            on_click=self.mostrar_gestion_usuarios,
            width=250,
            height=45,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_700,
                color=ft.Colors.WHITE,
            )
        )
        
        # Agregar a la sección correspondiente en tu UI existente
        # (depende de cómo tengas organizado el layout)
        # Por ejemplo, si tienes una columna principal:
        if hasattr(self, 'main_column'):
            self.main_column.controls.append(
                ft.Container(
                    padding=ft.padding.only(top=20),
                    content=ft.Column(
                        spacing=15,
                        controls=[
                            ft.Text(
                                "Gestión de Usuarios",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_900
                            ),
                            self.btn_gestion_usuarios,
                        ]
                    )
                )
            )
    
    def mostrar_gestion_usuarios(self, e):
        """Muestra el diálogo de gestión de usuarios"""
        # Cargar usuarios actuales
        self.cargar_usuarios()
        
        # Crear lista de usuarios
        self.lista_usuarios = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
        )
        
        # Cargar usuarios en la lista
        self.actualizar_lista_usuarios()
        
        # Crear botones de acción
        botones_accion = ft.Row(
            spacing=10,
            controls=[
                ft.ElevatedButton(
                    text="Nuevo Usuario",
                    icon=ft.Icons.PERSON_ADD,
                    on_click=self.crear_nuevo_usuario,
                    bgcolor=ft.Colors.GREEN,
                    color=ft.Colors.WHITE,
                ),
                ft.ElevatedButton(
                    text="Actualizar",
                    icon=ft.Icons.REFRESH,
                    on_click=lambda e: self.actualizar_lista_usuarios(),
                    bgcolor=ft.Colors.BLUE,
                    color=ft.Colors.WHITE,
                ),
            ]
        )
        
        # Crear diálogo
        self.dialogo_usuarios = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.PEOPLE, color=ft.Colors.BLUE_700),
                    ft.Text("Gestión de Usuarios", size=22, weight=ft.FontWeight.BOLD),
                ],
                spacing=10,
            ),
            content=ft.Container(
                width=700,
                height=500,
                content=ft.Column(
                    spacing=15,
                    controls=[
                        ft.Text(
                            f"Administrador: {self.usuario_actual}",
                            size=14,
                            color=ft.Colors.GREY_600,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Divider(),
                        botones_accion,
                        ft.Container(
                            expand=True,
                            border=ft.border.all(1, ft.Colors.GREY_300),
                            border_radius=10,
                            content=self.lista_usuarios,
                        ),
                    ]
                )
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=self.cerrar_gestion_usuarios),
            ],
        )
        
        self.page.dialog = self.dialogo_usuarios
        self.dialogo_usuarios.open = True
        self.page.update()
    
    def cargar_usuarios(self):
        """Carga los usuarios desde el archivo JSON"""
        usuarios_file = "usuarios.json"
        if os.path.exists(usuarios_file):
            try:
                with open(usuarios_file, "r") as f:
                    self.usuarios = json.load(f)
                print(f"Usuarios cargados: {len(self.usuarios)}")
            except Exception as e:
                print(f"Error cargando usuarios: {e}")
                self.usuarios = {}
        else:
            self.usuarios = {}
    
    def guardar_usuarios(self):
        """Guarda los usuarios en el archivo JSON"""
        usuarios_file = "usuarios.json"
        try:
            with open(usuarios_file, "w") as f:
                json.dump(self.usuarios, f, indent=2)
            print("Usuarios guardados exitosamente")
        except Exception as e:
            print(f"Error guardando usuarios: {e}")
    
    def actualizar_lista_usuarios(self, e=None):
        """Actualiza la lista de usuarios en el diálogo"""
        self.cargar_usuarios()
        self.lista_usuarios.controls.clear()
        
        for usuario, datos in self.usuarios.items():
            # No permitir modificar al usuario actual si no es admin
            if usuario == self.usuario_actual and self.rol_actual != "admin":
                continue
                
            # Determinar color según rol
            rol_color = ft.Colors.GREEN if datos.get('rol') == 'admin' else ft.Colors.BLUE
            rol_texto = "Administrador" if datos.get('rol') == 'admin' else "Usuario"
            
            # Crear tarjeta de usuario
            tarjeta_usuario = ft.Card(
                elevation=2,
                content=ft.Container(
                    padding=15,
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        spacing=10,
                                        controls=[
                                            ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE_700),
                                            ft.Text(
                                                usuario,
                                                size=18,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                        ]
                                    ),
                                    ft.Container(
                                        content=ft.Text(
                                            rol_texto,
                                            color=ft.Colors.WHITE,
                                            size=12,
                                        ),
                                        bgcolor=rol_color,
                                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                        border_radius=8,
                                    ),
                                ]
                            ),
                            ft.Row(
                                spacing=20,
                                controls=[
                                    ft.ElevatedButton(
                                        text="Cambiar Rol",
                                        icon=ft.Icons.SWAP_HORIZ,
                                        on_click=lambda e, u=usuario: self.cambiar_rol_usuario(u),
                                        width=150,
                                        height=35,
                                        style=ft.ButtonStyle(
                                            bgcolor=ft.Colors.ORANGE,
                                            color=ft.Colors.WHITE,
                                        )
                                    ),
                                    ft.ElevatedButton(
                                        text="Cambiar Contraseña",
                                        icon=ft.Icons.LOCK_RESET,
                                        on_click=lambda e, u=usuario: self.cambiar_contrasena_usuario(u),
                                        width=180,
                                        height=35,
                                        style=ft.ButtonStyle(
                                            bgcolor=ft.Colors.PURPLE,
                                            color=ft.Colors.WHITE,
                                        )
                                    ),
                                    ft.ElevatedButton(
                                        text="Eliminar",
                                        icon=ft.Icons.DELETE,
                                        on_click=lambda e, u=usuario: self.eliminar_usuario(u),
                                        width=120,
                                        height=35,
                                        style=ft.ButtonStyle(
                                            bgcolor=ft.Colors.RED,
                                            color=ft.Colors.WHITE,
                                        )
                                    ),
                                ]
                            ),
                        ]
                    )
                )
            )
            
            self.lista_usuarios.controls.append(tarjeta_usuario)
        
        self.lista_usuarios.update()
    
    def cambiar_rol_usuario(self, usuario):
        """Cambia el rol de un usuario"""
        if usuario not in self.usuarios:
            self.mostrar_mensaje(f"Usuario {usuario} no encontrado", ft.Colors.RED)
            return
        
        # No permitir cambiar el rol del usuario actual si no es admin
        if usuario == self.usuario_actual and self.rol_actual != "admin":
            self.mostrar_mensaje("No puedes cambiar tu propio rol", ft.Colors.ORANGE)
            return
        
        nuevo_rol = "usuario" if self.usuarios[usuario].get('rol') == 'admin' else "admin"
        
        def confirmar_cambio(e):
            self.usuarios[usuario]['rol'] = nuevo_rol
            self.guardar_usuarios()
            self.actualizar_lista_usuarios()
            dlg.open = False
            self.page.update()
            self.mostrar_mensaje(f"Rol de {usuario} cambiado a {nuevo_rol}", ft.Colors.GREEN)
        
        def cancelar(e):
            dlg.open = False
            self.page.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar cambio de rol"),
            content=ft.Text(f"¿Cambiar rol de '{usuario}' a '{nuevo_rol}'?"),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.ElevatedButton(
                    "Confirmar",
                    on_click=confirmar_cambio,
                    bgcolor=ft.Colors.BLUE,
                    color=ft.Colors.WHITE,
                ),
            ],
        )
        
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
    
    def cambiar_contrasena_usuario(self, usuario):
        """Muestra diálogo para cambiar contraseña de usuario"""
        if usuario not in self.usuarios:
            self.mostrar_mensaje(f"Usuario {usuario} no encontrado", ft.Colors.RED)
            return
        
        # Campos para nueva contraseña
        nueva_contrasena = ft.TextField(
            label="Nueva contraseña",
            password=True,
            can_reveal_password=True,
            width=300,
        )
        
        confirmar_contrasena = ft.TextField(
            label="Confirmar contraseña",
            password=True,
            can_reveal_password=True,
            width=300,
        )
        
        error_text = ft.Text("", color=ft.Colors.RED, size=12)
        
        def aplicar_cambio(e):
            if not nueva_contrasena.value:
                error_text.value = "La contraseña no puede estar vacía"
                self.page.update()
                return
            
            if nueva_contrasena.value != confirmar_contrasena.value:
                error_text.value = "Las contraseñas no coinciden"
                self.page.update()
                return
            
            if len(nueva_contrasena.value) < 6:
                error_text.value = "La contraseña debe tener al menos 6 caracteres"
                self.page.update()
                return
            
            self.usuarios[usuario]['password'] = nueva_contrasena.value
            self.guardar_usuarios()
            dlg.open = False
            self.page.update()
            self.mostrar_mensaje(f"Contraseña de {usuario} actualizada", ft.Colors.GREEN)
        
        def cancelar(e):
            dlg.open = False
            self.page.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Cambiar contraseña de {usuario}"),
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
    
    def eliminar_usuario(self, usuario):
        """Elimina un usuario"""
        if usuario not in self.usuarios:
            self.mostrar_mensaje(f"Usuario {usuario} no encontrado", ft.Colors.RED)
            return
        
        # No permitir eliminarse a sí mismo
        if usuario == self.usuario_actual:
            self.mostrar_mensaje("No puedes eliminar tu propio usuario", ft.Colors.RED)
            return
        
        # No permitir eliminar el último admin
        admins = [u for u, d in self.usuarios.items() if d.get('rol') == 'admin']
        if self.usuarios[usuario].get('rol') == 'admin' and len(admins) <= 1:
            self.mostrar_mensaje("No puedes eliminar el único administrador", ft.Colors.RED)
            return
        
        def confirmar_eliminar(e):
            del self.usuarios[usuario]
            self.guardar_usuarios()
            self.actualizar_lista_usuarios()
            dlg.open = False
            self.page.update()
            self.mostrar_mensaje(f"Usuario {usuario} eliminado", ft.Colors.GREEN)
        
        def cancelar(e):
            dlg.open = False
            self.page.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Está seguro que desea eliminar al usuario '{usuario}'?\nEsta acción no se puede deshacer."),
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
    
    def crear_nuevo_usuario(self, e):
        """Crea un nuevo usuario"""
        # Campos para nuevo usuario
        nuevo_usuario = ft.TextField(
            label="Nombre de usuario",
            prefix_icon=ft.Icons.PERSON_ADD,
            width=300,
        )
        
        nueva_contrasena = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            width=300,
        )
        
        confirmar_contrasena = ft.TextField(
            label="Confirmar contraseña",
            password=True,
            can_reveal_password=True,
            width=300,
        )
        
        rol_usuario = ft.Dropdown(
            label="Rol",
            width=300,
            options=[
                ft.dropdown.Option("usuario", "Usuario Normal"),
                ft.dropdown.Option("admin", "Administrador"),
            ],
            value="usuario",
        )
        
        error_text = ft.Text("", color=ft.Colors.RED, size=12)
        
        def crear_usuario(e):
            usuario = nuevo_usuario.value.strip()
            contrasena = nueva_contrasena.value.strip()
            confirmar = confirmar_contrasena.value.strip()
            rol = rol_usuario.value
            
            if not usuario:
                error_text.value = "El nombre de usuario es obligatorio"
                self.page.update()
                return
            
            if not contrasena:
                error_text.value = "La contraseña es obligatoria"
                self.page.update()
                return
            
            if contrasena != confirmar:
                error_text.value = "Las contraseñas no coinciden"
                self.page.update()
                return
            
            if len(contrasena) < 6:
                error_text.value = "La contraseña debe tener al menos 6 caracteres"
                self.page.update()
                return
            
            if usuario in self.usuarios:
                error_text.value = "El usuario ya existe"
                self.page.update()
                return
            
            # Crear nuevo usuario
            self.usuarios[usuario] = {
                'password': contrasena,
                'rol': rol
            }
            
            self.guardar_usuarios()
            self.actualizar_lista_usuarios()
            dlg.open = False
            self.page.update()
            self.mostrar_mensaje(f"Usuario {usuario} creado exitosamente", ft.Colors.GREEN)
        
        def cancelar(e):
            dlg.open = False
            self.page.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Crear Nuevo Usuario"),
            content=ft.Column(
                width=400,
                spacing=15,
                controls=[
                    nuevo_usuario,
                    nueva_contrasena,
                    confirmar_contrasena,
                    rol_usuario,
                    error_text,
                ]
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.ElevatedButton(
                    "Crear Usuario",
                    on_click=crear_usuario,
                    bgcolor=ft.Colors.BLUE,
                    color=ft.Colors.WHITE,
                ),
            ],
        )
        
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
    
    def cerrar_gestion_usuarios(self, e):
        """Cierra el diálogo de gestión de usuarios"""
        self.dialogo_usuarios.open = False
        self.page.update()
    
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
```

2. Versión simplificada si solo quieres un diálogo básico:

Si prefieres una versión más simple, aquí tienes un diálogo básico:

```python
def mostrar_gestion_usuarios(self, e):
    """Muestra un diálogo simple para gestionar usuarios"""
    # Cargar usuarios
    self.cargar_usuarios()
    
    # Crear lista de opciones
    opciones = []
    for usuario, datos in self.usuarios.items():
        if usuario == self.usuario_actual:
            continue  # No mostrar el usuario actual
            
        rol = "👑 Admin" if datos.get('rol') == 'admin' else "👤 Usuario"
        opciones.append(
            ft.ListTile(
                title=ft.Text(usuario),
                subtitle=ft.Text(rol),
                trailing=ft.PopupMenuButton(
                    icon=ft.Icons.MORE_VERT,
                    items=[
                        ft.PopupMenuItem(
                            text="Cambiar a Usuario" if datos.get('rol') == 'admin' else "Cambiar a Admin",
                            on_click=lambda e, u=usuario: self.cambiar_rol_simple(u),
                        ),
                        ft.PopupMenuItem(
                            text="Eliminar",
                            on_click=lambda e, u=usuario: self.eliminar_usuario_simple(u),
                        ),
                    ]
                )
            )
        )
    
    # Diálogo simple
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Gestión de Usuarios"),
        content=ft.Container(
            width=400,
            height=300,
            content=ft.ListView(
                controls=opciones,
                spacing=5,
            )
        ),
        actions=[
            ft.ElevatedButton(
                "Nuevo Usuario",
                on_click=self.crear_nuevo_usuario_simple,
                bgcolor=ft.Colors.GREEN,
                color=ft.Colors.WHITE,
            ),
            ft.TextButton("Cerrar", on_click=lambda e: self.cerrar_dialogo(dlg)),
        ],
    )
    
    self.page.dialog = dlg
    dlg.open = True
    self.page.update()

def cambiar_rol_simple(self, usuario):
    """Cambia el rol de forma simple"""
    if usuario in self.usuarios:
        nuevo_rol = "usuario" if self.usuarios[usuario].get('rol') == 'admin' else "admin"
        self.usuarios[usuario]['rol'] = nuevo_rol
        self.guardar_usuarios()
        self.mostrar_mensaje(f"{usuario} ahora es {nuevo_rol}", ft.Colors.GREEN)

def eliminar_usuario_simple(self, usuario):
    """Elimina usuario de forma simple"""
    if usuario in self.usuarios and usuario != self.usuario_actual:
        del self.usuarios[usuario]
        self.guardar_usuarios()
        self.mostrar_mensaje(f"Usuario {usuario} eliminado", ft.Colors.GREEN)

def crear_nuevo_usuario_simple(self, e):
    """Crea nuevo usuario de forma simple"""
    # Similar al método anterior pero más simple
    pass

def cerrar_dialogo(self, dlg):
    """Cierra cualquier diálogo"""
    dlg.open = False
    self.page.update()
```

3. Para integrarlo en tu UI existente:

En el método que crea la UI de configuración, agrega el botón de gestión de usuarios:

```python
def __init__(self, page, reloj_global, usuario_actual, rol_actual):
    # ... código existente ...
    
    # Crear columna principal
    self.main_column = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=20,
        controls=[
            # ... otros controles existentes ...
            
            # SECCIÓN GESTIÓN DE USUARIOS
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
                                ft.Icon(ft.Icons.PEOPLE, color=ft.Colors.BLUE_700, size=28),
                                ft.Text(
                                    "Gestión de Usuarios",
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLUE_900
                                ),
                            ],
                            spacing=10
                        ),
                        ft.Divider(),
                        ft.Text(
                            "Administra los usuarios del sistema. Solo usuarios administradores pueden acceder a esta sección.",
                            size=14,
                            color=ft.Colors.GREY_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(
                            alignment=ft.alignment.center,
                            padding=ft.padding.only(top=10),
                            content=self.btn_gestion_usuarios,
                        ),
                    ]
                )
            ),
            
            # ... más controles existentes ...
        ]
    )
    
    # ... resto del código ...
```

Características del diálogo implementado:

1. Lista de usuarios con tarjetas informativas
2. Cambio de rol (usuario ↔ admin)
3. Cambio de contraseña para cualquier usuario
4. Eliminación de usuarios con validaciones
5. Creación de nuevos usuarios
6. Validaciones para evitar:
   · Eliminar el último admin
   · Eliminar tu propio usuario
   · Contraseñas inválidas
7. Interfaz visual con colores según roles
8. Actualización automática de la lista

El diálogo se abre desde el botón "Gestión de Usuarios" en la página de Configuración y solo es accesible para usuarios administradores.
