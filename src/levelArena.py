from level import Level
import random  # Para spawns randômicos
from objects.dynamic_objects.hammer_bot import HammerBot
from pygame.math import Vector2

class LevelArena(Level):
    def __init__(self, screen, level_name, player_spawn=None):
        super().__init__(screen, level_name, player_spawn)
        # Atributos específicos da arena (responsabilidade única: gerenciar waves)
        self.waves = []  # Lista de waves: cada wave é uma dict com 'enemies_count', 'health_multiplier', etc.
        self.current_wave = 0
        self.arena_active = False  # Estado: True quando arena inicia (hordas começam)
        self.wave_cooldown = 0  # Tempo entre waves (em segundos)
        self.max_waves = 3  # Exemplo: 3 waves progressivas
        self.setup_waves()  # Configura waves iniciais

    def setup_waves(self):
        """Configura waves progressivas. Pode ser ajustado para balanceamento (análise crítica)."""
        self.waves = [
            {'count': 3, 'health_multiplier': 1.0, 'speed_multiplier': 1.0},  # Wave 1: Básica
            {'count': 5, 'health_multiplier': 1.2, 'speed_multiplier': 1.1},  # Wave 2: Mais inimigos, mais fortes
            {'count': 7, 'health_multiplier': 1.5, 'speed_multiplier': 1.2},  # Wave 3: Desafio final
        ]

    def load_map(self, level_name, player_spawn=None):
        super().load_map(level_name, player_spawn)
        # Lógica específica: Fechar entradas (ex.: tornar portas inativas ou adicionar barreiras)
        for obj in self.static_objects:
            if isinstance(obj, Door):
                obj.active = False  # Exemplo: Desativa trigger de portas (assumindo que Door tem 'active')
                print(f"Porta fechada na arena: {obj.name}")
        self.arena_active = True  # Inicia a arena ao carregar o mapa
        self.spawn_wave()  # Spawna a primeira wave imediatamente

    def update(self, delta_time):
        super().update(delta_time)
        if not self.arena_active:
            return

        # Gerencia waves: Se wave atual completa (sem inimigos), inicia cooldown para próxima
        if not self.enemies:  # Todos inimigos mortos
            if self.current_wave < self.max_waves:
                self.wave_cooldown += delta_time
                if self.wave_cooldown >= 5.0:  # 5 segundos entre waves
                    self.current_wave += 1
                    self.wave_cooldown = 0
                    self.spawn_wave()
            else:
                # Todas waves completas: Vitória!
                self.is_completed = True
                print("Arena completada! Todas waves eliminadas.")
                # Aqui: Adicione recompensas, ex.: self.player.spell_system.add_rune(nova_runa)
                # Ou transite para próximo level via self.load_map("next_level")

    def spawn_wave(self):
        """Spawna inimigos da wave atual em posições randômicas (dentro dos limites do mapa)."""
        if self.current_wave >= len(self.waves):
            return
        wave = self.waves[self.current_wave]
        print(f"Iniciando Wave {self.current_wave + 1}: {wave['count']} inimigos")
        for _ in range(wave['count']):
            # Posição randômica: Ajuste para evitar spawn no player ou fora do mapa
            spawn_x = random.uniform(100, self.map_width * self.tile_width - 100)
            spawn_y = random.uniform(100, self.map_height * self.tile_height - 100)
            position = Vector2(spawn_x, spawn_y)
            size = (22, 31)  # Tamanho padrão do HammerBot
            enemy = HammerBot(position, size)
            # Aplica multiplicadores para progressão (melhoria contínua: facilita balanceamento)
            enemy.max_health *= wave['health_multiplier']
            enemy.health = enemy.max_health
            enemy.speed *= wave['speed_multiplier']
            self.enemies.append(enemy)
            self.dynamic_objects.append(enemy)
            self.all_sprites.append(enemy)

    def reset(self):
        super().reset()
        # Reset específico da arena
        self.current_wave = 0
        self.wave_cooldown = 0
        self.arena_active = False
        self.setup_waves()  # Reinicia waves para nova tentativa