from objects.dynamic_objects.hammer_bot import HammerBot
from objects.dynamic_objects.player import Player

class EntityManager:
    def __init__(self):
        self.entities = []  # Todos os objetos dinâmicos (Player, HammerBot, Rune, projéteis, escudos)
        self.enemies = []  # Apenas inimigos (ex.: HammerBot)

    def add_entity(self, entity, is_enemy=False):
        """Adiciona uma entidade, opcionalmente marcando como inimigo."""
        if not hasattr(entity, 'update'):
            print(f"Aviso: Tentativa de adicionar entidade sem método 'update': {type(entity)}")
            return
        if entity not in self.entities:
            self.entities.append(entity)
            if is_enemy:
                self.enemies.append(entity)

    def remove_entity(self, entity, score_callback=None):
        """Remove uma entidade e atualiza pontuação se for inimigo."""
        if entity in self.entities:
            self.entities.remove(entity)
            if entity in self.enemies:
                self.enemies.remove(entity)
                if score_callback:
                    score_callback(100)  # Pontuação por inimigo destruído

    def update(self, delta_time, static_objects, score_callback, all_sprites, spell_system):
        """Atualiza todas as entidades e gerencia projéteis/escudos."""
        for entity in self.entities[:]:
            if hasattr(entity, "marked_for_removal") and entity.marked_for_removal:
                self.remove_entity(entity, score_callback)
                if entity in all_sprites:
                    all_sprites.remove(entity)
            else:
                # Passa static_objects apenas para HammerBot
                if isinstance(entity, HammerBot):
                    entity.update(delta_time, static_objects)
                else:
                    entity.update

        # Atualiza spell_system e adiciona projéteis/escudos
        if spell_system:
            player_pos = None
            for entity in self.entities:
                if isinstance(entity, Player):  # Localiza jogador para spell_system
                    player_pos = [entity.position.x + entity.size[0] / 2,
                                  entity.position.y + entity.size[1] / 2]
                    break
            if player_pos:
                spell_system.update(delta_time, player_pos)
                for spell in spell_system.spellbook:
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

    def get_player(self):
        """Retorna o jogador, se presente."""
        for entity in self.entities:
            if isinstance(entity, Player):
                return entity
        return None

    def check_completion(self):
        """Verifica se não há mais inimigos (para níveis como level_2)."""
        return not self.enemies