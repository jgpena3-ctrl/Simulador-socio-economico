from configu.categorias import COLORES_CATEGORIAS


class InterfazSimulador:
    """Encapsula lógica de presentación/UI del simulador."""

    def __init__(self, simulador):
        self.sim = simulador

    def color_para_hex(self, hexagono):
        """Determina color de cada casilla según prioridad visual."""
        if hasattr(hexagono, "color_personalizado") and hexagono.color_personalizado:
            return hexagono.color_personalizado

        if hasattr(hexagono, "categoria") and hexagono.categoria in COLORES_CATEGORIAS:
            return COLORES_CATEGORIAS[hexagono.categoria]

        if hexagono.q == 0 and hexagono.r == 0:
            return (120, 120, 220)

        if abs(hexagono.q) + abs(hexagono.r) + abs(-hexagono.q - hexagono.r) <= 2:
            return (180, 180, 100)

        if hexagono.arboles > 10:
            return (34, 139, 34)
        if hexagono.arboles > 3:
            return (50, 150, 50)

        return (110, 90, 70)

    def dibujar_ui(self):
        """Dibuja paneles informativos y controles."""
        if not self.sim.agente_jugador:
            return

        agente = self.sim.agente_jugador
        pantalla = self.sim.pantalla
        font = self.sim.font

        info_agente = [
            f"Jugador: {agente.nombre}",
            f"Ubicación: {agente.ubicacion}",
            f"Hambre: {agente.fisiologia.combustible:.3f}%",
            f"Energía: {agente.fisiologia.energia:.0f}%",
            f"Cansancio: {agente.fisiologia.cansancio:.0f}%",
            f"Comida: {agente.inventario.get('comida', 0)}",
            f"Agua: {agente.inventario.get('agua', 0)}",
        ]

        y = 10
        for texto in info_agente:
            superficie = font.render(texto, True, (255, 255, 255))
            pantalla.blit(superficie, (10, y))
            y += 25

        estado_camara = self.sim.camara.get_estado()
        info_camara = [
            f"Día {self.sim.dia}, Año {self.sim.anno}",
            f"Hora: {self.sim.hora:02d}:{self.sim.minutos:02d}",
            f"Tick: {self.sim.tick}",
            f"Cámara: {estado_camara['zoom_percent']:.0f}% zoom",
            f"Seguir: {'ON' if self.sim.seguir_jugador else 'OFF'}",
            f"Estado: {'MOVIÉNDOSE' if self.sim.moviendo_agente else 'LISTO'}",
        ]

        y = self.sim.alto - len(info_camara) * 25 - 10
        for texto in info_camara:
            superficie = font.render(texto, True, (200, 200, 255))
            pantalla.blit(superficie, (self.sim.ancho // 2 - 150, y))
            y += 25

        controles = [
            "=== CONTROLES ===",
            "WASD/Flechas: Mover cámara",
            "Rueda mouse: Zoom",
            "Z/X: Zoom in/out",
            "R: Reset zoom",
            "HOME: Centrar jugador",
            "F: Alternar seguir",
            "CLIC IZQ: Menú casilla",
            "CLIC DER: Cancelar",
            "C: Comer",
            "P: Pausa",
            "ESPACIO: Tick manual",
            "ESC: Salir",
        ]

        y = 10
        for texto in controles:
            superficie = font.render(texto, True, (200, 200, 200))
            pantalla.blit(superficie, (self.sim.ancho - 250, y))
            y += 25
