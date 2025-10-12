from objects.dynamic_objects.hammer_bot import HammerBot
from objects.dynamic_objects.player import Player
from objects.dynamic_objects.rune import Rune
import random
import logging

class EntityManager:
    def __init__(self, spell_system, object_factory, minor_rune_drop_state=None):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)
        self.entities = []
        self.enemies = []
        self.spell_system = spell_system
        self.object_factory = object_factory
        self.minor_rune_effects = [
            {"power": 5}, {"cost": -10}, {"cooldown": -2},
            {"power": 15, "cost": 10}, {"cooldown": 10, "cost": -8},
            {"power": 10, "cooldown": 8}, {"power": -5, "cooldown": -5},
            {"cost": -5, "cooldown": -5, "power": -8}
        ]
        self.available_effects = self.minor_rune_effects.copy()
        self.used_effects = []
        self.update_map = {
            Player: self._update_player,
            HammerBot: self._update_hammer_bot,
            Rune: self._update_rune
        }
        # Initialize minor_rune_drop_state, use provided state or default
        self.minor_rune_drop_state = minor_rune_drop_state if minor_rune_drop_state is not None else {
            "first_drop": True,
            "streak": 0,
            "base_chance": 0.2,
            "increment": 0.1
        }

    def add_entity(self, entity, is_enemy=False):
        """Adiciona uma entidade, opcionalmente marcando como inimigo."""
        if not hasattr(entity, 'update'):
            return
        if entity not in self.entities:
            self.entities.append(entity)
            if is_enemy:
                self.enemies.append(entity)

    def remove_entity(self, entity, score_callback=None, all_sprites=None, dead_callback=None, current_dead_ids=None):
        """Remove uma entidade e atualiza pontuação se for inimigo."""
        if entity in self.entities:
            self.entities.remove(entity)
            if entity in self.enemies:
                print(f"Removendo inimigo: {type(entity).__name__} com ID: {getattr(entity, 'id', 'N/A')}")
                self.enemies.remove(entity)
                if current_dead_ids is not None and (not hasattr(entity, 'id') or entity.id not in current_dead_ids):
                    # Novo: Verificar se deve dropar com base na lógica randomizada
                    if self._should_drop_minor_rune():
                        self._generate_minor_rune(entity, all_sprites)
                if score_callback:
                    score_callback(100)
                if dead_callback and hasattr(entity, 'id'):
                    dead_callback(entity.id)
                # Verifica se o inimigo já está na lista temporária de mortos
                print(f"Current dead IDs before rune generation: {current_dead_ids}")

            else:
                if all_sprites and entity in all_sprites:
                    all_sprites.remove(entity)

    def _should_drop_minor_rune(self):
        """Decide se deve dropar uma runa menor com base no estado interno."""
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
        """Gera uma runa menor com um efeito aleatório."""
        if not self.available_effects:
            self.available_effects = self.used_effects.copy()
            self.used_effects = []
        effect = random.choice(self.available_effects)
        self.available_effects.remove(effect)
        self.used_effects.append(effect)
        minor_rune = self.object_factory.create_object({
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
        """Atualiza todas as entidades e gerencia projéteis/escudos."""
        for entity in self.entities[:]:
            if hasattr(entity, "marked_for_removal") and entity.marked_for_removal:
                self.remove_entity(entity, score_callback, all_sprites, dead_callback, current_dead_ids)
            else:
                update_func = self.update_map.get(type(entity))
                if update_func:
                    update_func(entity, delta_time, static_objects, all_sprites)

        # Atualiza spell_system e adiciona projéteis/escudos
        player = self.get_player()
        player_pos = [player.position.x + player.size[0] / 2, player.position.y + player.size[1] / 2] if player else None
        if player_pos:
            self.spell_system.update(delta_time, player_pos)
            for spell in self.spell_system.spellbook:
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
        """Atualiza o jogador."""
        entity.update(delta_time)

    def _update_hammer_bot(self, entity, delta_time, static_objects, all_sprites):
        """Atualiza o HammerBot."""
        entity.update(delta_time, static_objects)

    def _update_rune(self, entity, delta_time, static_objects, all_sprites):
        """Atualiza a runa."""
        entity.update(delta_time)

    def get_player(self):
        """Retorna o jogador, se presente."""
        for entity in self.entities:
            if isinstance(entity, Player):
                return entity
        return None

    def check_completion(self):
        """Verifica se não há mais inimigos."""
        return not self.enemies