import pygame
from utils.hex_math import axial_to_pixel, get_hex_corners


class WorldRenderer:
    """Se encarga de renderizar mundo, agentes y capas UI."""

    def __init__(self, simulador):
        self.simulador = simulador

    def dibujar(self):
        sim = self.simulador
        sim.pantalla.fill((25, 25, 35))

        for (q, r), hexagono in sim.mapa.hexagonos.items():
            x_mundo, y_mundo = axial_to_pixel(q, r, sim.hex_size, sim.hex_flat)
            x_pant, y_pant = sim.camara.mundo_a_pantalla(x_mundo, y_mundo)

            if sim._esta_en_pantalla(x_pant, y_pant):
                vertices = get_hex_corners(
                    x_pant,
                    y_pant,
                    sim.hex_size * sim.camara.escala,
                    sim.hex_flat,
                )
                color = sim._color_para_hex(hexagono)
                pygame.draw.polygon(sim.pantalla, color, vertices, 0)
                pygame.draw.polygon(sim.pantalla, (0, 0, 0), vertices, 1)

        if sim.moviendo_agente and sim.ruta_actual:
            sim.movement.dibujar_ruta()

        for agente in sim.agentes:
            if agente.ubicacion in sim.mapa.hexagonos:
                q, r = agente.ubicacion
                x_mundo, y_mundo = axial_to_pixel(q, r, sim.hex_size, sim.hex_flat)
                x_pant, y_pant = sim.camara.mundo_a_pantalla(x_mundo, y_mundo)

                color = (0, 200, 255) if agente.controlado_por_jugador else (255, 100, 100)
                radio = max(3, (sim.hex_size * sim.camara.escala) // 3)
                pygame.draw.circle(sim.pantalla, color, (int(x_pant), int(y_pant)), radio)

                if sim.camara.escala > 0.8 and agente.controlado_por_jugador:
                    font = pygame.font.SysFont(None, int(20 * sim.camara.escala))
                    nombre_surf = font.render(agente.nombre, True, (255, 255, 255))
                    sim.pantalla.blit(nombre_surf, (x_pant - 40, y_pant - radio - 20))

        sim._dibujar_ui()
        sim.menu.dibujar(sim.pantalla)
        if sim.menu_inventario.visible:
            sim.menu_inventario.dibujar(sim.pantalla)

        if sim.menu_mercado.visible:
            sim.menu_mercado.dibujar(sim.pantalla)

        pygame.display.flip()
