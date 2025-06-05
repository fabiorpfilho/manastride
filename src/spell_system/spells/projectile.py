from spell_system.spell import Spell
from spell_system.rune import Rune
from typing import List, Optional
import pygame 
from config import SPEED
import math

class Projectile(Spell):
    def __init__(self, major_rune: Optional[Rune] = None, minor_runes: List[Rune] = None):
        super().__init__(
            name="Projectile",
            base_attributes={"damage": 10, "speed": 300, "mana_cost": 20},
            major_rune=major_rune,
            minor_runes=minor_runes,
            position=(0, 0), 
            size=(0, 0), 
            sprite=(0, 255, 0)
        )
        self.add_collider((0, 0), (self.size.x, self.size.y),
                          type='projectile', solid=True)
        self.projectiles = []            # Projéteis já ativos na tela
        self.pending_projectiles = []    # Projéteis esperando o tempo de spawn
        self.marked_for_removal = False

    def execute(self, direction: float):
        if not self.validate():
            print(f"Feitiço inválido: {self.name}")
            return

        # Efeitos das runas menores
        effects = {k: v for k, v in self.attributes.items() if k in [
            "slow", "burn"]}
        minor_rune_names = [rune.name for rune in self.minor_runes]

        if self.major_rune:
            # Executa comportamento baseado no nome da runa maior
            if self.major_rune.name == "Fan":
                # Leque de 5 projéteis
                # 40° de espalhamento
                base_angle = 0.5 if direction == 1 else  math.pi - 0.5
                angles = [base_angle + (i * 0.1) - 0.2 for i in range(5)]
                # print(f"Angulos {angles}!")
                for i, angle in enumerate(angles):
                    projectile = {
                        "direction": angle,
                        "speed": self.attributes["speed"],
                        "damage": self.attributes["damage"] * 0.6,
                        "effects": effects,
                        "major_rune": "Fan",
                        "minor_runes": minor_rune_names
                    }
                    self.pending_projectiles.append(projectile)
                # print(f"🌬️ {self.name} dispara leque de projéteis!")
            elif self.major_rune.name == "Multiple":
                for i in range(3):
                    spawn_time = pygame.time.get_ticks() + (i * 200)
                    projectile = {
                        "spawn_time": spawn_time,
                        "direction": direction,
                        "speed": self.attributes["speed"],
                        "damage": self.attributes["damage"],
                        "effects": effects,
                        "major_rune": "Multiple",
                        "minor_runes": minor_rune_names
                    }
                    self.pending_projectiles.append(projectile)
            elif self.major_rune.name == "Homing":
                # Projétil perseguidor
                projectile = {
                    "direction": direction,
                    "speed": self.attributes["speed"],
                    "damage": self.attributes["damage"],
                    "effects": effects,
                    "homing": True,
                    "major_rune": "Homing",
                    "minor_runes": minor_rune_names
                }
                self.projectiles.append(projectile)
                # print(f"🎯 {self.name} dispara projétil perseguidor!")
        else:
            # Comportamento padrão
            projectile = {
                "direction": direction,
                "speed": self.attributes["speed"],
                "damage": self.attributes["damage"],
                "effects": effects,
                "major_rune": "Default",
                "minor_runes": minor_rune_names
            }
            self.projectiles.append(projectile)
            # print(f"🏹 {self.name} disparado!")
            # if "slow" in effects:
            #     print("🧊 Projétil com efeito de gelo!")
            # if "burn" in effects:
            #     print("🔥 Projétil com efeito de fogo!")

    def update(self, delta_time: float, player_pos: tuple):
        MAX_DISTANCE = 500
        current_time = pygame.time.get_ticks()
        
        def spawn_projectile_from_pending(pending):
            projectile = Projectile(
                major_rune=self.major_rune,
                minor_runes=self.minor_runes
            )
            projectile.position.x = player_pos[0]
            projectile.position.y = player_pos[1]
            projectile.size.update(10, 10)
            projectile.add_collider(
                (0, 0), (10, 10), type='projectile', solid=True)

            projectile.speed = pending["speed"]
            projectile.damage = pending["damage"]
            projectile.start_x = player_pos[0]
            projectile.start_y = player_pos[1]
            projectile.direction = pending["direction"]
            projectile.major_rune_name = pending["major_rune"]
            projectile.minor_rune_names = pending["minor_runes"]
            projectile.effects = pending["effects"]
            if "homing" in pending:
                projectile.homing = pending["homing"]

            self.projectiles.append(projectile)
            self.pending_projectiles.remove(pending)

        # Spawn projéteis pendentes
        for pending in self.pending_projectiles[:]:
            if pending.get("spawn_time") is not None:
                if current_time >= pending["spawn_time"]:
                    spawn_projectile_from_pending(pending)
            else:
                spawn_projectile_from_pending(pending)
            
            
        # Atualizar projéteis ativos
        for proj in self.projectiles[:]:
            if proj.marked_for_removal:
                self.projectiles.remove(proj)
                continue
            
            if proj.major_rune_name == "Fan":
                dx = math.cos(proj.direction)
                dy = -math.sin(proj.direction)
                proj.position.x += dx * (proj.speed + SPEED) * delta_time
                proj.position.y += dy * (proj.speed + SPEED) * delta_time
                distance_traveled = math.hypot(
                    proj.position.x - proj.start_x, proj.position.y - proj.start_y)
            else:

                # Movimento linear original para outros tipos
                proj.position.x += proj.direction * (proj.speed + SPEED) * delta_time
                distance_traveled = abs(proj.position.x - proj.start_x)
            
            
            if distance_traveled > MAX_DISTANCE:
                proj.marked_for_removal = True
            # if "slow" in proj.effects:
            #     print(f"🧊 Inimigo atingido por {proj.name} desacelerado!")
            # if "burn" in proj.effects:
            #     print(f"🔥 In System: imigo atingido por {proj.name} queimando!")

    def draw(self, surface, camera):
        for proj in self.projectiles:
            screen_pos = camera.apply(pygame.Rect(proj.position.x, proj.position.y, 0, 0)).center
            # Define a cor com base nas runas menores
            color = (255, 0, 0)  # Padrão: vermelho
            minor_runes = getattr(proj, "minor_rune_names", [])
            if "Ice" in minor_runes:
                color = (0, 200, 255)  # Ice: azul
            elif "Fire" in minor_runes:
                color = (255, 100, 0)  # Fire: laranja

            # Define o visual com base na runa maior
            major_rune = getattr(proj, "major_rune_name", "Default")
            if major_rune == "Fan":
                # Círculo menor para múltiplos projéteis
                pygame.draw.circle(surface, color, screen_pos, 3)
            elif major_rune == "Multiple":
                # Círculo intermediário para múltiplos disparos
                pygame.draw.circle(surface, color, screen_pos, 4)
            elif major_rune == "Homing":
                # Triângulo para perseguição
                points = [
                    (screen_pos[0], screen_pos[1] - 5),
                    (screen_pos[0] - 5, screen_pos[1] + 5),
                    (screen_pos[0] + 5, screen_pos[1] + 5)
                ]
                pygame.draw.polygon(surface, color, points)
            else:  # Default
                pygame.draw.circle(surface, color, screen_pos, 5)
