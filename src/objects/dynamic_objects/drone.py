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
        self.is_dying = False
        self.facing_right = False

        # NOVO: Controle de morte com queda
        self.death_falling = False
        self.death_grounded = False
        self.death_bounce_frame = False

        self.animation_speeds = {
            self.animation_manager.AnimationType.WALK: 0.5,
            self.animation_manager.AnimationType.HURT: 0.1,
            self.animation_manager.AnimationType.DEATH: 0.15,
        }

        self.add_collider((0, 0), self.size, type='body', active=True)
        self.add_collider((0, 0), self.size, type='hurt_box', active=True)
        self.add_collider((0, 0), self.size, type='attack_box', active=True)
        player_check_size = (self.size[0] + 125, self.size[1] + 100)
        player_check_offset = (-62, -50)  # -100 // 2
        self.add_collider(player_check_offset, player_check_size, type='player_check', active=True)
        self.player_detected = False
        self.player_target = None
        self.detection_cooldown = 0.2  # evita piscar detecção rapidamente
        self.detection_timer = 0


        # Parâmetros de levitação
        self.base_y = position[1]
        self.levitation_amplitude = 20
        self.levitation_speed = 2
        self.levitation_timer = 0

        # Parâmetros de dano
        self.is_hurt = False

        # Carrega animações
        if self.animation_manager:
            self.animation_manager.load_animations_from_json(
                self.size,
                image_path="assets/drone_bot/DroneBotSpriteSheet.png",
                json_path="assets/drone_bot/DroneBotSpriteSheet.json"
            )

            if not self.animation_manager.animationList:
                print("Erro: Nenhuma animação do drone carregada")
                self.default_image = pygame.Surface(self.size)
                self.default_image.fill((255, 0, 0))
            else:
                self.set_animation(self.animation_manager.AnimationType.WALK)

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
        else:
            self.default_image = pygame.Surface(self.size)
            self.default_image.fill((255, 0, 0))

        # Define a imagem inicial
        self.image = self.default_image
        self.rect = self.image.get_rect(topleft=position)


    def update(self, delta_time):
        """Movimento flutuante, perseguição e efeitos de dano."""
        self.levitation_timer += delta_time

        # --- Gerenciamento de detecção ---
        if self.player_detected:
            if self.player_target is None:
                self.player_detected = False
            else:
                self.detection_timer = 0
        else:
            self.detection_timer += delta_time
            if self.detection_timer >= self.detection_cooldown:
                self.player_target = None

        # --- Movimento ---
        if not self.is_hurt and not self.is_dying:
            if self.player_detected and self.player_target:
                # Persegue o jogador nos eixos X e Y
                dx = self.player_target.position.x - self.position.x
                dy = self.player_target.position.y - self.position.y

                self.facing_right = dx > 0

                # Normaliza a direção (para não se mover mais rápido em diagonal)
                distance = math.hypot(dx, dy)
                if distance != 0:
                    dir_x = dx / distance
                    dir_y = dy / distance
                else:
                    dir_x = dir_y = 0

                chase_speed = self.speed * 1.2
                self.speed_vector.x = dir_x * chase_speed
                self.speed_vector.y = dir_y * chase_speed

            else:
                # Patrulha normal (flutuando horizontalmente)
                self.speed_vector.x = self.speed if self.facing_right else -self.speed
                # Mantém o padrão de levitação suave no Y
                levitation_offset = math.sin(self.levitation_timer * self.levitation_speed) * self.levitation_amplitude
                self.position.y = self.base_y + levitation_offset
                self.speed_vector.y = 0

        # --- Atualiza posição ---
        if self.is_dying and self.death_falling:
            self.speed_vector.y += self.gravity * delta_time
            self.position.y += self.speed_vector.y * delta_time
            self.position.x += self.speed_vector.x * delta_time
        elif not self.is_dying:
            self.position.x += self.speed_vector.x * delta_time
            if self.player_detected and self.player_target:
                # Persegue verticalmente enquanto detecta o player
                self.position.y += self.speed_vector.y * delta_time + math.sin(self.levitation_timer * 4) * 0.5
            else:
                # Movimento flutuante já aplicado acima
                pass

        # --- Atualiza animação ---
        self.update_animation(delta_time)

        # --- Atualiza posição e imagem ---
        self.sync_position()

    def update_animation(self, delta_time):
        if not self.animation_manager or not self.current_animation:
            return

        if self.is_dying:
            self.animation_timer += delta_time
            animation_speed = self.animation_speeds.get(self.animation_manager.AnimationType.DEATH, 0.15)
            death_anim = self.current_animation
            total_frames = len(death_anim.animation) if death_anim.animation else 0

            if total_frames < 6:
                self.update_image()
                return

            if self.animation_timer >= animation_speed:
                self.animation_timer -= animation_speed

                # FASE 1: Anima até o frame 4
                if self.current_frame < 4:
                    self.current_frame += 1

                # FASE 2: Alterna entre 3 e 4 enquanto cai
                elif self.current_frame == 4 and self.death_falling:
                    self.death_bounce_frame = not self.death_bounce_frame
                    self.current_frame = 3 if self.death_bounce_frame else 4

                # FASE 3: Ao tocar o chão, vai para frame 5
                elif self.death_grounded and self.current_frame < 5:
                    self.current_frame = 5

                # FASE 4: Mantém no frame 5 e conta para remoção
                elif self.current_frame >= 5:
                    self.current_frame = 5
                    self.marked_for_removal = True

                self.update_image()

            return  # pula o resto da lógica de animação

        if self.is_hurt:
            self.animation_timer += delta_time
            animation_speed = self.animation_speeds.get(self.animation_manager.AnimationType.HURT, 0.1)
            if self.animation_timer >= animation_speed:
                self.animation_timer -= animation_speed
                self.current_frame += 1
                if self.current_frame >= len(self.current_animation.animation):
                    self.current_frame = 0
                    self.is_hurt = False
                    self.colliders[2].active = True  # Re-enable attack_box
                    self.colliders[0].active = True  # Re-enable body
                    self.set_animation(self.animation_manager.AnimationType.IDLE1)
                self.update_image()
            return

        if abs(self.speed_vector.x) > 0.1:
            self.set_animation(self.animation_manager.AnimationType.WALK)
        else:
            self.set_animation(self.animation_manager.AnimationType.IDLE1)

        self.animation_timer += delta_time
        animation_speed = self.animation_speeds.get(self.current_animation.type, 0.1)
        if self.animation_timer >= animation_speed:
            self.animation_timer -= animation_speed
            if self.current_animation.type == self.animation_manager.AnimationType.JUMP:
                self.current_frame = min(self.current_frame + 1, len(self.current_animation.animation) - 1)
            else:
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

            if getattr(self, "visible", True):
                self.image = sprite
            else:
                self.image = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
        else:
            self.image = self.default_image

        self.rect = self.image.get_rect(topleft=(self.position.x, self.position.y))


    def handle_damage(self, enemy_damage, damage_source_position=None):
        """Recebe dano, aplica knockback e pisca."""
        if self.health <= 0 or self.is_hurt:
            return

        self.health -= enemy_damage
        print(f"Drone sofreu {enemy_damage} de dano. Vida restante: {self.health}")

        if self.health <= 0:
            pygame.mixer.Sound("assets/audio/soundEffects/enemy_death.mp3").play()
            self.set_animation(self.animation_manager.AnimationType.DEATH)
            self.is_dying = True
            self.death_falling = True
            self.death_grounded = False
            self.death_bounce_frame = False
            self.marked_for_removal = False

            # Desativa colisores de ataque e corpo (mas mantém body para colisão com chão)
            self.colliders[2].active = False  # attack_box

            # Ativa gravidade apenas na morte
            self.gravity = 800  # ajuste conforme necessário
            self.speed_vector.y = -100  # leve impulso inicial para cima

            # Opcional: knockback horizontal
            direction = 1 if damage_source_position and damage_source_position[0] < self.position.x else -1
            self.speed_vector.x = direction * 100

        else:
            self.set_animation(self.animation_manager.AnimationType.HURT)
            self.is_hurt = True
            self.colliders[2].active = False
            self.is_attacking = False
            knockback_strength = 150
            direction = 1 if damage_source_position and damage_source_position[0] < self.position.x else -1
            self.speed_vector.x = direction * knockback_strength
            self.speed_vector.y = -150