import pygame
from utils.hex_math import axial_to_pixel, hex_distance


class MovementSystem:
    """Gestiona movimiento de agentes, rutas y desplazamiento de cámara."""

    def __init__(self, simulador):
        self.simulador = simulador

    def actualizar_movimiento_camara(self):
        """Actualizar movimiento de cámara basado en teclas presionadas."""
        sim = self.simulador
        if not any(sim.teclas_presionadas.values()):
            return

        dx, dy = 0, 0
        if sim.teclas_presionadas[pygame.K_w] or sim.teclas_presionadas[pygame.K_UP]:
            dy -= 1
        if sim.teclas_presionadas[pygame.K_s] or sim.teclas_presionadas[pygame.K_DOWN]:
            dy += 1
        if sim.teclas_presionadas[pygame.K_a] or sim.teclas_presionadas[pygame.K_LEFT]:
            dx -= 1
        if sim.teclas_presionadas[pygame.K_d] or sim.teclas_presionadas[pygame.K_RIGHT]:
            dx += 1

        if dx != 0 or dy != 0:
            sim.camara.mover(dx, dy)
            sim.seguir_jugador = False

    def mover_agente_a(self, agente, destino):
        """Iniciar movimiento a una casilla destino."""
        sim = self.simulador
        inicio = agente.ubicacion

        if inicio == destino:
            print(f"{agente.nombre} ya está en {destino}")
            return False

        if destino not in sim.mapa.hexagonos:
            print(f"Destino {destino} no está en el mapa")
            return False

        sim.ruta_actual = self.calcular_ruta(inicio, destino)

        if not sim.ruta_actual:
            print(f"No se pudo calcular ruta de {inicio} a {destino}")
            return False

        print(f"{agente.nombre} se mueve a {destino} ({len(sim.ruta_actual)} pasos)")
        sim.moviendo_agente = True
        agente.actividad_actual = "moviendose"
        print("Movimiento iniciado. Primer paso en el próximo tick.")
        return True

    def avanzar_paso_movimiento(self):
        """Mover UN paso por tick."""
        sim = self.simulador
        if not sim.ruta_actual or not sim.moviendo_agente:
            return False

        agente = sim.agente_jugador
        if not agente:
            return False

        siguiente = sim.ruta_actual.pop(0)

        if siguiente not in sim.mapa.hexagonos:
            print(f"Error: Paso inválido {siguiente}")
            self.finalizar_movimiento()
            return False

        ubicacion_anterior = agente.ubicacion
        agente.ubicacion = siguiente
        agente.fisiologia.cansancio += 2
        agente.fisiologia.energia = max(0, agente.fisiologia.energia - 1)

        print(f"  {agente.nombre}: {ubicacion_anterior} → {siguiente}")

        if not sim.ruta_actual:
            self.finalizar_movimiento()
            return True

        return False

    def finalizar_movimiento(self):
        """Finalizar movimiento correctamente."""
        sim = self.simulador
        agente = sim.agente_jugador
        if agente:
            destino = agente.ubicacion
            print(f"{agente.nombre} llegó a {destino}")

            hex_destino = sim.mapa.hexagonos.get(destino)
            if hex_destino:
                if destino == (0, 0):
                    print("  (Estás en el área central)")
                elif hex_destino.arboles > 0:
                    print("  (Hay árboles aquí para talar)")
                elif any(count > 0 for count in hex_destino.animales.values()):
                    print("  (Hay animales aquí para cazar)")

        sim.moviendo_agente = False
        sim.ruta_actual = []

        if agente:
            agente.actividad_actual = None

    def calcular_ruta(self, inicio, destino):
        """Calcular ruta en línea recta por interpolación axial."""
        if inicio == destino:
            return []

        q1, r1 = inicio
        q2, r2 = destino

        distancia = self.distancia_hex(inicio, destino)

        if distancia == 1:
            return [destino]

        ruta = []
        for i in range(1, distancia + 1):
            t = i / distancia
            q_float = q1 * (1 - t) + q2 * t
            r_float = r1 * (1 - t) + r2 * t

            hex_redondeado = self.axial_round(q_float, r_float)
            if not ruta or hex_redondeado != ruta[-1]:
                ruta.append(hex_redondeado)

        return ruta

    def dibujar_ruta(self):
        """Dibujar ruta usando cámara."""
        sim = self.simulador
        if not sim.ruta_actual or not sim.agente_jugador:
            return

        puntos = []

        q_actual, r_actual = sim.agente_jugador.ubicacion
        x_mundo, y_mundo = axial_to_pixel(q_actual, r_actual, sim.hex_size, sim.hex_flat)
        x_pant, y_pant = sim.camara.mundo_a_pantalla(x_mundo, y_mundo)
        puntos.append((x_pant, y_pant))

        for q, r in sim.ruta_actual:
            x_mundo, y_mundo = axial_to_pixel(q, r, sim.hex_size, sim.hex_flat)
            x_pant, y_pant = sim.camara.mundo_a_pantalla(x_mundo, y_mundo)
            puntos.append((x_pant, y_pant))

        if len(puntos) >= 2:
            pygame.draw.lines(
                sim.pantalla,
                (255, 255, 0),
                False,
                puntos,
                max(2, int(3 * sim.camara.escala)),
            )

        for punto in puntos[1:]:
            radio = max(3, int(6 * sim.camara.escala))
            pygame.draw.circle(sim.pantalla, (255, 200, 0), (int(punto[0]), int(punto[1])), radio)

    def distancia_hex(self, hex1, hex2):
        return hex_distance(hex1, hex2)

    def axial_round(self, q, r):
        x = q
        z = r
        y = -x - z

        rx = round(x)
        ry = round(y)
        rz = round(z)

        x_diff = abs(rx - x)
        y_diff = abs(ry - y)
        z_diff = abs(rz - z)

        if x_diff > y_diff and x_diff > z_diff:
            rx = -ry - rz
        elif y_diff > z_diff:
            ry = -rx - rz
        else:
            rz = -rx - ry

        return int(rx), int(rz)
