from objects.dynamic_objects.character import Character
from config import SPEED
import pygame
import math

class Drone(Character):
    def __init__(self, position, size, sprite=(255, 0, 0), invincible=False, 
                 max_health=30, attackable=True, damage=15, 
                 custom_speed=None, gravity=0, speed_vector=(0, 0), jump_speed=0,
                 custom_max_health=None, custom_damage=None, id=None):

        speed = custom_speed if custom_speed is not None else SPEED - 100
        max_health = custom_max_health if custom_max_health is not None else max_health
        damage = custom_damage if custom_damage is not None else damage
        
        super().__init__(position, size, sprite, invincible, max_health,
                         attackable, damage, speed, gravity, speed_vector, jump_speed)

        self.id = id
        self.health = max_health
        self.tag = "enemy_npc"
        self.current_animation = None
        self.current_frame = 0
        self.animation_timer = 0
        self.marked_for_removal = False
        self.facing_right = True

        self.animation_speeds = {
            self.animation_manager.AnimationType.WALK: 0.5,
        }

        self.add_collider((0, 0), self.size, type='body', active=True)
        self.add_collider((0, 0), self.size, type='hurt_box', active=True)
        self.add_collider((0, 0), self.size, type='attack_box', active=True)

        # Parâmetros de levitação
        self.base_y = position[1]
        self.levitation_amplitude = 20
        self.levitation_speed = 2
        self.levitation_timer = 0

        # Parâmetros de dano
        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 0.5  # segundos de invulnerabilidade e piscada
        self.knockback_strength = 10  # força do empurrão
        self.blink_interval = 0.2  # intervalo entre piscadas
        self.blink_timer = 0

        # 🔹 Carrega animações
        if self.animation_manager:
            self.animation_manager.load_animations_from_json(
                self.size,
                image_path="assets/drone_bot/drone_bot.png",
                json_path="assets/drone_bot/drone_bot.json"
            )

            if not self.animation_manager.animationList:
                print("Erro: Nenhuma animação do drone carregada")
                self.default_image = pygame.Surface(self.size)
                self.default_image.fill((255, 0, 0))
            else:
                self.set_animation(self.animation_manager.AnimationType.WALK)

                # Define imagem padrão como o primeiro frame da animação de andar
                walk_anim = next(
                    (a for a in self.animation_manager.animationList 
                     if a.type == self.animation_manager.AnimationType.WALK),
                    None
                )
                if walk_anim and walk_anim.animation:
                    self.default_image = walk_anim.animation[0].image
                else:
                    self.default_image = pygame.Surface(self.size)
                    self.default_image.fill((255, 0, 0))

        # Define a imagem inicial
        self.image = self.default_image
        self.rect = self.image.get_rect(topleft=position)


    def update(self, delta_time):
        """Movimento flutuante, animação e efeitos de dano."""
        self.levitation_timer += delta_time

        # Knockback (se foi atingido recentemente)
        if self.is_hit:
            self.hit_timer += delta_time
            self.blink_timer += delta_time

            # Piscar visível/invisível
            if self.blink_timer >= self.blink_interval:
                self.blink_timer = 0
                self.visible = not getattr(self, "visible", True)

            # Finaliza o efeito de dano
            if self.hit_timer >= self.hit_duration:
                self.is_hit = False
                self.visible = True
                self.hit_timer = 0
                self.speed_vector.x = 0  # para o knockback

        # Movimento normal
        if not self.is_hit:
            self.speed_vector.x = self.speed if self.facing_right else -self.speed

        # Atualiza posição
        self.position.x += self.speed_vector.x * delta_time
        levitation_offset = math.sin(self.levitation_timer * self.levitation_speed) * self.levitation_amplitude
        self.position.y = self.base_y + levitation_offset

        # Atualiza animação
        self.update_animation(delta_time)

        # Atualiza posição e imagem
        self.sync_position()


    def update_animation(self, delta_time):
        """Atualiza a animação de voo/andar."""
        if not self.animation_manager or not self.current_animation:
            self.image = self.default_image
            return

        self.animation_timer += delta_time
        animation_speed = self.animation_speeds.get(self.current_animation.type, 0.1)

        if self.animation_timer >= animation_speed:
            self.animation_timer -= animation_speed
            self.current_frame = (self.current_frame + 1) % len(self.current_animation.animation)
            self.update_image()


    def set_animation(self, animation_type):
        """Seleciona e inicializa a animação atual."""
        if not self.animation_manager:
            print("Aviso: Nenhum AnimationManager fornecido")
            return

        for animation in self.animation_manager.animationList:
            if animation.type == animation_type:
                if self.current_animation != animation:
                    self.current_animation = animation
                    self.current_frame = 0
                    self.animation_timer = 0
                    self.update_image()
                return
        print(f"Aviso: Animação {animation_type} não encontrada")


    def update_image(self):
        """Atualiza o frame de exibição do drone."""
        if self.current_animation and self.current_animation.animation:
            sprite = self.current_animation.animation[self.current_frame].image
            if not self.facing_right:
                sprite = pygame.transform.flip(sprite, True, False)

            # Aplica o piscar
            if getattr(self, "visible", True):
                self.image = sprite
            else:
                # Cria uma imagem transparente (invisível)
                self.image = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
        else:
            self.image = self.default_image

        self.rect = self.image.get_rect(topleft=(self.position.x, self.position.y))


    def handle_damage(self, enemy_damage, damage_source_position=None):
        """Recebe dano, aplica knockback e pisca."""
        if self.health <= 0 or self.is_hit:
            return

        self.health -= enemy_damage
        print(f"Drone sofreu {enemy_damage} de dano. Vida restante: {self.health}")

        # Aplica knockback (empurrão para longe da fonte de dano)
        direction = 1 if damage_source_position else -1
        self.speed_vector.x = direction * self.knockback_strength

        # Ativa piscar e invulnerabilidade temporária
        self.is_hit = True
        self.visible = True
        self.hit_timer = 0
        self.blink_timer = 0

        # # Efeito sonoro
        # pygame.mixer.Sound("assets/audio/soundEffects/hit_enemy.mp3").play()

        # Verifica morte
        if self.health <= 0:
            pygame.mixer.Sound("assets/audio/soundEffects/enemy_death.mp3").play()
            self.marked_for_removal = True
            self.colliders[2].active = False
