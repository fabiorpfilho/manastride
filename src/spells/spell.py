from typing import List
from spells.rune import Rune
from spells.rune_type import RuneType
from spells.spell_effect_type import SpellEffectType
from config import SPEED
from objects.entity_with_animation import EntityWithAnimation
import pygame


class Spell(EntityWithAnimation):
    def __init__(self, name: str, runes: List[Rune], effect_type: SpellEffectType):
        
        super().__init__(position=(0, 0), size=(0, 0), sprite=(0, 255, 0))
        self.add_collider((0, 0), (self.size.x, self.size.y), type='spell', solid=True)
        self.name = name                             # Nome do feitiço
        self.runes = runes                           # Lista de runas que compõem o feitiço
        self.compiled_effect = None                  # Função resultante da combinação das runas
        self.mana_cost = int                   # Custo total de mana para lançar o feitiço
        self.effect_type = effect_type
        self.projectiles = []            # Projéteis já ativos na tela
        self.pending_projectiles = []    # Projéteis esperando o tempo de spawn
        self.marked_for_removal = False

        # self.compile_spell()

    def validate(self):
        """
        Verifica se a sequência de runas forma um feitiço válido.
        Exemplo de validações:
        - Deve ter ao menos uma runa.
        - Um LOOP deve conter ao menos um COMMAND dentro e ter um numero de repetições válido.
        - Uma CONDITION deve ser seguida por um comando ou bloco
        - MODIFIERS devem seguir e modificar COMMAND válidos
        """
        if not self.runes:
            return False

        for i, rune in enumerate(self.runes):
            if rune.rune_type == RuneType.CONDITION:
                if i + 1 >= len(self.runes) or self.runes[i + 1].rune_type != RuneType.COMMAND:
                    return False
                if not rune.value or "condition" not in rune.value:
                    return False
            elif rune.rune_type == RuneType.LOOP:
                if i + 1 >= len(self.runes) or self.runes[i + 1].rune_type != RuneType.COMMAND:
                    return False
                if not rune.value or "iterations" not in rune.value or rune.value["iterations"] <= 0:
                    return False
            elif rune.rune_type == RuneType.MODIFIER:
                if i == 0 or self.runes[i - 1].rune_type != RuneType.COMMAND:
                    return False

        return True

    def execute(self, direction):
        """
        Executa o feitiço interpretando as runas como uma mini linguagem.
        Exemplo: [Fireball] [Dano=5] => Cria e lança um projétil com 5 de dano.
        """
        if not self.validate():
            self.compiled_effect = lambda pos: print(f"Feitiço inválido: {self.name}")
            return
        
        current_command = None
        modifiers = {}
        loop_count = 1  
        
        self.mana_cost = sum(rune.cost for rune in self.runes)

        for rune in self.runes:
            if rune.rune_type == RuneType.COMMAND:
                current_command = rune.name
                modifiers = {}  # limpa modificadores anteriores

            elif rune.rune_type == RuneType.MODIFIER:
                if current_command:
                    # Espera-se que value seja um dicionário como {"dano": 5}
                    modifiers.update(rune.value)
            elif rune.rune_type == RuneType.LOOP:
                    loop_count = rune.value.get("iterations", 1)

        if self.effect_type == SpellEffectType.PROJECTILE and current_command:
            for i in range(loop_count):
                damage = modifiers.get("damage", 1)
                speed = modifiers.get("speed", 1)
                spawn_time = pygame.time.get_ticks() + (i * 200)
                pending  = {
                    "spawn_time": spawn_time,
                    "speed": speed,
                    "damage": damage,
                    "direction": direction
                }
                self.pending_projectiles.append(pending)
                print(f"🔥 {self.name} launched with damage {damage} and speed {speed}")
            
    def update_projectiles(self, delta_time, player_pos):
        MAX_DISTANCE = 500
        current_time = pygame.time.get_ticks()

        # Spawn projéteis pendentes
        for pending in self.pending_projectiles[:]:
            if current_time >= pending["spawn_time"]:
                projectile = Spell(
                    name=self.name,
                    runes=self.runes,
                    effect_type=self.effect_type
                )
                projectile.position.x = player_pos[0]
                projectile.position.y = player_pos[1]
                projectile.size.update(10, 10)
                projectile.add_collider((0, 0), (10, 10), type='spell', solid=True)

                # Atributos extras para movimento
                projectile.speed = pending["speed"]
                projectile.damage = pending["damage"]
                projectile.start_x = player_pos[0]
                projectile.direction = pending["direction"]

                self.projectiles.append(projectile)
                self.pending_projectiles.remove(pending)

        # Atualizar projéteis ativos
        for proj in self.projectiles[:]:
            if proj.marked_for_removal:
                print(f"Chegou aqui")
                self.projectiles.remove(proj)
                continue  # Pula pra próximo projétil se marcado para remoção
            
            proj.position.x += proj.direction * (proj.speed + SPEED) * delta_time
            distance_traveled = abs(proj.position.x - proj.start_x)
            if distance_traveled > MAX_DISTANCE:
                self.projectiles.remove(proj)

    def draw_projectiles(self, surface):
        for proj in self.projectiles:
            pygame.draw.circle(surface, (255, 0, 0), (proj.position.x, proj.position.y), 5)  
