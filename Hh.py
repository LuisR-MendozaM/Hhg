def _on_nuevo_registro(self, registro):
    """Se ejecuta cuando se agrega un nuevo registro al historial"""
    print(f"UI: Nuevo registro recibido en callback - Fuente: {registro['fuente'] if registro else 'Limpieza'}")
    
    # Actualizar el historial en la configuración si existe
    if hasattr(self, 'config_container'):
        # Verificar si config_container tiene el método para actualizar
        if hasattr(self.config_container, 'actualizar_historial_desde_externo'):
            print(f"UI: Llamando a actualizar_historial_desde_externo en config_container")
            
            # Usar page.run_thread para ejecutar en el hilo de UI
            if self.page:
                def actualizar():
                    try:
                        self.config_container.actualizar_historial_desde_externo(registro)
                        print(f"UI: Historial actualizado en configuración")
                    except Exception as e:
                        print(f"UI: Error actualizando historial: {e}")
                
                # Ejecutar en el hilo principal de Flet
                self.page.run_task(actualizar)
        else:
            print(f"UI: config_container no tiene método actualizar_historial_desde_externo")
    else:
        print(f"UI: No hay config_container definido")
