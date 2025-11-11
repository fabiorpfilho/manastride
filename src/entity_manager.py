# entity_manager.py
from objects.dynamic_objects.hammer_bot import HammerBot
from objects.dynamic_objects.player import Player
from objects.dynamic_objects.rune import Rune
from objects.dynamic_objects.drone import Drone
from object_factory import ObjectFactory
import random
import logging
from pygame.math import Vector2
from typing import Optional, Dict, Any


class EntityManager:
    # --------------------------------------------------------------
    #  SINGLETON
    # --------------------------------------------------------------
    _instance: Optional["EntityManager"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # --------------------------------------------------------------
    #  __init__ (executado apenas uma vez)
    # --------------------------------------------------------------
    def __init__(self, minor_rune_drop_state: Optional[Dict[str, Any]] = None):
        # Evita reinicializar se já foi chamado
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

        self.entities = []
        self.enemies = []

        # Efeitos de runas menores
        self.minor_rune_effects = [
            {"power": 5}, {"cost": -10}, {"cooldown": -2},
            {"power": 15, "cost": 10}, {"cooldown": 10, "cost": -8},
            {"power": 10, "cooldown": 8}, {"power": -5, "cooldown": -5},
            {"cost": -5, "cooldown": -5, "power": -8}
        ]
        self.available_effects = self.minor_rune_effects.copy()
        self.used_effects = []

        # Mapa de atualização por tipo
        self.update_map = {
            Player: self._update_player,
            HammerBot: self._update_hammer_bot,
            Rune: self._update_rune,
            Drone: self._update_drone
        }

        # Estado de drop de runa menor
        default_state = {"first_drop": True, "streak": 0, "base_chance": 0.2, "increment": 0.1}
        self.minor_rune_drop_state = minor_rune_drop_state if minor_rune_drop_state is not None else default_state

    # --------------------------------------------------------------
    #  MÉTODOS PÚBLICOS
    # --------------------------------------------------------------
    def add_entity(self, entity, is_enemy=False):
        if not hasattr(entity, 'update'):
            return
        if entity not in self.entities:
            self.entities.append(entity)
            if is_enemy:
                self.enemies.append(entity)

    def remove_entity(self, entity, score_callback=None, all_sprites=None, dead_callback=None, current_dead_ids=None):
        if entity not in self.entities:
            return

        self.entities.remove(entity)
        if entity in self.enemies:
            self.enemies.remove(entity)
            print(f"Removendo inimigo: {type(entity).__name__} com ID: {getattr(entity, 'id', 'N/A')}")

            if current_dead_ids is not None and (not hasattr(entity, 'id') or entity.id not in current_dead_ids):
                if self._should_drop_minor_rune():
                    self._generate_minor_rune(entity, all_sprites)

            if score_callback:
                score_callback(100)
            if dead_callback and hasattr(entity, 'id'):
                dead_callback(entity.id)

        if not isinstance(entity, (HammerBot, Drone)):
            if all_sprites and entity in all_sprites:
                all_sprites.remove(entity)

    def _should_drop_minor_rune(self) -> bool:
        state = self.minor_rune_drop_state
        if state["first_drop"]:
            state["first_drop"] = False
            self.logger.info("Primeiro inimigo derrotado - dropando runa menor")
            return True
        else:
            chance = min(1.0, state["base_chance"] + state["increment"] * state["streak"])
            self.logger.info(f"Chance de drop: {chance*100:.1f}% (streak: {state['streak']})")
            if random.random() < chance:
                state["streak"] = 0
                self.logger.info("Runa menor dropada - streak resetado")
                return True
            else:
                state["streak"] += 1
                self.logger.info(f"Nenhuma runa dropada - streak aumentado para {state['streak']}")
                return False

    def _generate_minor_rune(self, entity, all_sprites):
        if not self.available_effects:
            self.available_effects = self.used_effects.copy()
            self.used_effects = []

        effect = random.choice(self.available_effects)
        self.available_effects.remove(effect)
        self.used_effects.append(effect)

        minor_rune = ObjectFactory.create_object({
            'position': (entity.position.x + (entity.size[0] / 2), entity.position.y),
            'size': (11, 15),
            'name': 'Runa menor',
            'type': 'rune',
            'rune_type': 'minor',
            'effect': effect
        })
        if minor_rune:
            self.add_entity(minor_rune)
            if all_sprites and minor_rune not in all_sprites:
                all_sprites.append(minor_rune)
            self.logger.info(f"Runa menor gerada com efeito: {effect}")

    def update(self, delta_time, static_objects, score_callback, all_sprites, dead_callback=None, current_dead_ids=None):
        for entity in self.entities[:]:
            if hasattr(entity, "marked_for_removal") and entity.marked_for_removal:
                self.remove_entity(entity, score_callback, all_sprites, dead_callback, current_dead_ids)
            else:
                update_func = self.update_map.get(type(entity))
                if update_func:
                    update_func(entity, delta_time, static_objects, all_sprites)

        for static in static_objects:
            if hasattr(static, "marked_for_removal") and static.marked_for_removal:
                static_objects.remove(static)
                if static in all_sprites:
                    all_sprites.remove(static)

        player = self.get_player()
        if player:
            player_pos = [player.position.x + player.size[0] / 2, player.position.y + player.size[1] / 2]
            player.spell_system.update(delta_time, player_pos)

            for spell in player.spell_system.spellbook:
                if not spell:
                    continue
                if hasattr(spell, "projectiles"):
                    for proj in spell.projectiles:
                        if proj not in self.entities:
                            self.add_entity(proj)
                            if proj not in all_sprites:
                                all_sprites.append(proj)
                if hasattr(spell, "shields"):
                    for shield in spell.shields:
                        if spell.major_rune and spell.major_rune.name == "fan":
                            if shield not in static_objects:
                                static_objects.append(shield)
                                if shield not in all_sprites:
                                    all_sprites.append(shield)
                        elif shield not in self.entities:
                            self.add_entity(shield)
                            if shield not in all_sprites:
                                all_sprites.append(shield)

    def _update_player(self, entity, delta_time, static_objects, all_sprites):
        entity.update(delta_time)

    def _update_hammer_bot(self, entity, delta_time, static_objects, all_sprites):
        entity.update(delta_time, static_objects)

    def _update_rune(self, entity, delta_time, static_objects, all_sprites):
        entity.update(delta_time)

    def _update_drone(self, entity, delta_time, static_objects, all_sprites):
        entity.update(delta_time)

    def get_player(self):
        for entity in self.entities:
            if isinstance(entity, Player):
                return entity
        return None

    def check_completion(self):
        return not self.enemies

    def update_player_position(self, player, position):
        player.position = Vector2(position)
        player.sync_position()
        print(f"Player reposicionado em: {player.position}")
        return player

    # --------------------------------------------------------------
    #  MÉTODO DE FÁBRICA (opcional, para clareza)
    # --------------------------------------------------------------
    @classmethod
    def get_instance(cls, minor_rune_drop_state: Optional[Dict[str, Any]] = None) -> "EntityManager":
        """Retorna a instância única, inicializando com estado se necessário."""
        if cls._instance is None:
            cls(minor_rune_drop_state)  # chama __init__
        return cls._instance