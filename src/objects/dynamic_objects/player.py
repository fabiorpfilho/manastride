from objects.dynamic_objects.character import Character
from config import SPEED, JUMP_SPEED, GRAVITY
import pygame
from typing import Optional
from objects.animation_manager import AnimationManager

class Player(Character):
    def __init__(self, position, size, 
                 sprite=(0, 255, 0),invincible=False, max_health=100, 
                 attackable=True, damage=10, speed= SPEED, gravity=0, 
                 speed_vector=(0, 0), jump_speed=0):
        
        super().__init__(position, size, sprite, invincible, max_health,
                         attackable,damage, speed, gravity, speed_vector, jump_speed)
        self.tag = "player"
        self.current_animation = None
        self.current_frame = 0
        self.animation_timer = 0


        self.attack_sfx = {
            self.animation_manager.AnimationType.ATTACK1: pygame.mixer.Sound("assets/audio/soundEffects/sword/Sword Attack 1.ogg"),
            self.animation_manager.AnimationType.ATTACK2: pygame.mixer.Sound("assets/audio/soundEffects/sword/Sword Attack 2.ogg"),
            self.animation_manager.AnimationType.ATTACK3: pygame.mixer.Sound("assets/audio/soundEffects/sword/Sword Attack 3.ogg"),
        }
        self.attack_hit_sfx = {
            self.animation_manager.AnimationType.ATTACK1: pygame.mixer.Sound("assets/audio/soundEffects/sword/Sword Impact Hit 1.ogg"),
            self.animation_manager.AnimationType.ATTACK2: pygame.mixer.Sound("assets/audio/soundEffects/sword/Sword Impact Hit 2.ogg"),
            self.animation_manager.AnimationType.ATTACK3: pygame.mixer.Sound("assets/audio/soundEffects/sword/Sword Impact Hit 3.ogg"),
        }

        # self.attack_hit_sfx = {
        #     self.animation_manager.AnimationType.ATTACK1: pygame.mixer.Sound("assets/audio/soundEffects/sword/Sword Parry 1.ogg"),
        #     self.animation_manager.AnimationType.ATTACK2: pygame.mixer.Sound("assets/audio/soundEffects/sword/Sword Parry 2.ogg"),
        #     self.animation_manager.AnimationType.ATTACK3: pygame.mixer.Sound("assets/audio/soundEffects/sword/Sword Parry 3.ogg"),
        # }
        self.health = max_health
        
        self.is_attacking = False
        self.last_attack = None
        self.attack_combo_timer = 20
        self.attack_combo_timeout = 3.2
        self.attack_cooldown = 0.6  # Cooldown entre ataques
        self.attack_cooldown_timer = 0  # Temporizador do cooldown de ataque

        self.invincibility_duration = 2.0  # segundos de invencibilidade após tomar dano
        self.invincibility_timer = 0
        self.flicker_timer = 0
        self.flicker_interval = 0.1  # tempo entre piscadas
        self.visible = True  # controla a visibilidade do sprite
        
        self.max_mana = 100
        self.mana = self.max_mana
        self.mana_regen_rate = 5  # Mana por segundo (base)
        self.mana_regen_boost_rate = 10  # Mana por segundo durante o boost
        self.mana_boost_duration = 3.0  # Duração do boost em segundos
        self.mana_boost_timer = 0  # Temporizador do boost
        
        
        self.is_casting = False
        self.spell_cooldown = 0.5
        self.spell_cooldown_timer = 0
        self.dash_timer  = 0
        self.facing_right = True
        self.shield_health = 0
    
        self.already_hit_targets = set()

        

        self.animation_speeds = {
            self.animation_manager.AnimationType.IDLE1: 0.35,
            self.animation_manager.AnimationType.WALK: 0.1,
            self.animation_manager.AnimationType.JUMP: 0.1,
            self.animation_manager.AnimationType.FALLING: 0.1,
            self.animation_manager.AnimationType.CASTING: 0.1,
            self.animation_manager.AnimationType.ATTACK1: 0.08,
            self.animation_manager.AnimationType.ATTACK2: 0.08,
            self.animation_manager.AnimationType.ATTACK3: 0.08
        }

        self.add_collider((0, 0), self.size, type='body', active=True)
        self.add_collider((0, 0), self.size, type='hurt_box', active=True)
        self.add_collider((20, 0), (15, 30), type='attack_box', active=False)

        if self.animation_manager:
            self.animation_manager.load_animations_from_json(
                self.size,
                image_path="assets/player/adventurer-v1.5-Sheet1.png",
                json_path="assets/player/adventurer-v1.5-Sheet1.json",
            )   
            if not self.animation_manager.animationList:
                print("Erro: Nenhuma animação carregada")
            self.set_animation(self.animation_manager.AnimationType.IDLE1)

    def update(self, delta_time):
        keys = pygame.key.get_pressed()
        self.update_timers(delta_time)
        self.handle_movement(keys, delta_time)
        self.handle_attack(keys)
        self.handle_spell_casting(keys)
        self.apply_gravity(delta_time)
        self.update_animation(delta_time)
        self.sync_position()
        
    def update_timers(self, delta_time):

        if hasattr(self, "dash_timer") and self.dash_timer > 0:
            self.dash_timer -= delta_time
            if self.dash_timer <= 0:
                self.dash_timer = 0
                # Para o impulso do dash
                self.speed_vector.x = 0
                
        if self.spell_cooldown_timer > 0:
            self.spell_cooldown_timer -= delta_time
        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= delta_time
            
        if self.attack_combo_timer > 0:
            self.attack_combo_timer -= delta_time
            if self.attack_combo_timer <= 0:
                self.last_attack = None
                    
        if self.invincibility_timer > 0:
            self.invincibility_timer -= delta_time
            self.flicker_timer -= delta_time
            if self.flicker_timer <= 0:
                self.flicker_timer = self.flicker_interval
                self.visible = not self.visible 
        else:
            self.visible = True
            
        # Regeneração de mana
        regen_rate = self.mana_regen_boost_rate if self.mana_boost_timer > 0 else self.mana_regen_rate
        self.mana += regen_rate * delta_time
        if self.mana > self.max_mana:
            self.mana = self.max_mana

        # Atualiza o temporizador de boost de mana
        if self.mana_boost_timer > 0:
            self.mana_boost_timer -= delta_time

    def handle_movement(self, keys, delta_time):
        # Ignorar entradas de movimento durante o dash
        if self.dash_timer <= 0:
            if keys[pygame.K_LEFT]:
                self.speed_vector.x = -self.speed
                self.facing_right = False
            elif keys[pygame.K_RIGHT]:
                self.speed_vector.x = self.speed
                self.facing_right = True
            else:
                self.speed_vector.x *= 0.8
                if abs(self.speed_vector.x) < 0.1:
                    self.speed_vector.x = 0

        self.position.x += self.speed_vector.x * delta_time

        if keys[pygame.K_SPACE] and self.on_ground:
            self.speed_vector.y = -(self.jump_speed + JUMP_SPEED)
            self.on_ground = False

    def handle_attack(self, keys):
        if keys[pygame.K_z] and not self.is_casting and self.attack_cooldown_timer <= 0:
            
            if self.last_attack is None or self.last_attack == self.animation_manager.AnimationType.ATTACK3:
                self.set_animation(self.animation_manager.AnimationType.ATTACK1)
                
            elif self.last_attack == self.animation_manager.AnimationType.ATTACK1 and self.attack_combo_timer > 0:
                self.set_animation(self.animation_manager.AnimationType.ATTACK2)
                
            elif self.last_attack == self.animation_manager.AnimationType.ATTACK2 and self.attack_combo_timer > 0:
                self.set_animation(self.animation_manager.AnimationType.ATTACK3)
                
            elif self.last_attack == self.animation_manager.AnimationType.ATTACK3 and self.attack_combo_timer > 0:
                self.set_animation(self.animation_manager.AnimationType.ATTACK1)
                
            self.attack_cooldown_timer = self.attack_cooldown

    def handle_spell_casting(self, keys):
        key_to_index = {
            pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3,
        }
        for key, index in key_to_index.items():
            if keys[key] and self.spell_cooldown_timer <= 0:
                if hasattr(self, 'spell_system'):
                    spell_index = index - 1
                    spell = self.spell_system.spellbook[spell_index]
                    if self.mana >= spell.mana_cost:
                        direction = 1 if self.facing_right else -1
                        mana_cost = self.spell_system.cast_spell(index, direction , self)
                        self.mana -= mana_cost
                        self.spell_cooldown_timer = self.spell_cooldown
                        self.set_animation(self.animation_manager.AnimationType.CASTING)
                    else:
                        print("Mana insuficiente para lançar o feitiço.")
                        self.spell_cooldown_timer = self.spell_cooldown

    def apply_gravity(self, delta_time):
        # Não aplicar gravidade durante o dash
        if self.dash_timer <= 0:
            g = (self.gravity + GRAVITY)
            self.position.y += self.speed_vector.y * delta_time + ((g * (delta_time ** 2)) / 2)
            self.speed_vector.y += g * delta_time

    def update_animation(self, delta_time):
        if not self.animation_manager or not self.current_animation:
            return

        if self.is_casting or self.is_attacking:
            self.animation_timer += delta_time
            animation_speed = self.animation_speeds.get(self.current_animation.type, 0.1)
            if self.animation_timer >= animation_speed:
                self.animation_timer -= animation_speed
                self.current_frame += 1
                if self.current_frame >= len(self.current_animation.animation):
                    self.current_frame = 0
                    self.is_casting = False
                    print("Animação concluída")
                    self.is_attacking = False
                    self.colliders[2].active = self.is_attacking  # Desativa o ataque após a animação
                    self.set_animation(self.animation_manager.AnimationType.IDLE1)
                else:
                    # Define os frames de ataque onde a attack_box deve estar ativa
                    attack_frames = {
                        self.animation_manager.AnimationType.ATTACK1: [2],  # Frame ativo para ATTACK1
                        self.animation_manager.AnimationType.ATTACK2: [1],  # Frame ativo para ATTACK2
                        self.animation_manager.AnimationType.ATTACK3: [2]   # Frame ativo para ATTACK3
                    }
                    # Ativa a attack_box apenas nos frames especificados para a animação atual
                    self.colliders[2].active = (
                        self.is_attacking and 
                        self.current_animation.type in attack_frames and 
                        self.current_frame >= attack_frames[self.current_animation.type][0]
)
                self.update_image()
            return

        if not self.on_ground:
            if self.speed_vector.y < 0:
                self.set_animation(self.animation_manager.AnimationType.JUMP)
            else:
                self.set_animation(self.animation_manager.AnimationType.FALLING)
        else:
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
        self.image.set_alpha(255 if self.visible else 0)
            
    def set_animation(self, animation_type):
        if not self.animation_manager:
            print("Aviso: Nenhum AnimationManager fornecido")
            return
        for animation in self.animation_manager.animationList:
            if animation.type == animation_type:
                if self.current_animation != animation:
                    self.current_animation = animation
                    self.current_frame = 0
                    self.animation_timer = 0
                    if animation_type == self.animation_manager.AnimationType.CASTING:
                        self.is_casting = True
                        self.is_attacking = False
                    elif animation_type in (self.animation_manager.AnimationType.ATTACK1, 
                                            self.animation_manager.AnimationType.ATTACK2, 
                                            self.animation_manager.AnimationType.ATTACK3):
                        self.is_attacking = True
                        self.is_casting = False
                        self.last_attack = animation_type
                        
                        self.attack_combo_timer = self.attack_combo_timeout
                        self.already_hit_targets.clear()
                        # Tocar som de ataque correspondente
                    if animation_type in self.attack_sfx:
                        self.attack_sfx[animation_type].play()

                    else:
                        self.is_casting = False
                        self.is_attacking = False
                    self.update_image()
                break
        else:
            print(f"Aviso: Animação {animation_type} não encontrada")

    def update_image(self):
        if self.current_animation and self.current_animation.animation:
            sprite = self.current_animation.animation[self.current_frame].image
            if not self.facing_right:
                sprite = pygame.transform.flip(sprite, True, False)

            # Salve o anchor (midbottom atual) antes de mudar a imagem
            anchor = self.rect.midbottom

            # Atualize a imagem
            self.image = sprite

            # Crie um novo rect para a nova imagem
            new_rect = self.image.get_rect()

            # Posicione o novo rect para que o midbottom coincida com o anchor, ajustando pelo offset_y
            new_rect.midbottom = (anchor[0], anchor[1] )

            # Atualize o rect do sprite
            self.rect = new_rect

            # Atualize a posição do sprite
            self.position.x = self.rect.x
            self.position.y = self.rect.y
        else:
            print("Aviso: Nenhuma animação disponível, usando sprite padrão")
            self.image.fill(self.sprite)


    def handle_damage(self, enemy_damage, damage_source_position: None):
        if self.invincibility_timer > 0:
            return  # já está invencível
        

        
        self.invincibility_timer = self.invincibility_duration
        self.flicker_timer = self.flicker_interval
        self.visible = False
        
        if self.shield_health > 0:
            self.shield_health -= enemy_damage
            print(f"Escudo absorveu dano! Vida do escudo: {self.shield_health}")
            if self.shield_health <= 0:
                print("Escudo destruído!")
            return
        
        
        # Knockback leve
        knockback_strength = 300  # ajuste conforme necessário
        direction = 1 if damage_source_position else -1
        self.speed_vector.x = direction * knockback_strength
        self.speed_vector.y = -100  # empurrado levemente para cima também

        self.health -= enemy_damage
        print(f"Sofreu dano! Vida restante: {self.health}")



    def handle_hit(self):
        if self.last_attack and self.last_attack in self.attack_hit_sfx:
            self.attack_hit_sfx[self.last_attack].play()
        self.mana_boost_timer = self.mana_boost_duration  # Ativa o boost de regeneração de mana
            
    def handle_pickup(self, rune):
        self.spell_system.add_rune(rune)


