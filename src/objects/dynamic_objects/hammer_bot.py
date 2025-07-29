from objects.dynamic_objects.character import Character
from config import SPEED, GRAVITY
import pygame
from objects.animation_type import AnimationType
from typing import Optional
from objects.animation_manager import AnimationManager
import json

class HammerBot(Character):
    def __init__(self, position, size,
                 sprite=(0, 255, 0), collide_damage=5, invincible=False, health=100, 
                 attackable=True, attack_speed=0, damage=10, speed=0, gravity=0, 
                 speed_vector=(0, 0), jump_speed=0):
        
        super().__init__(position, size, sprite, collide_damage, invincible, health,
                         attackable, attack_speed, damage, speed, gravity, speed_vector, jump_speed)
        
        self.current_animation = None
        self.current_frame = 0
        self.animation_timer = 0
        self.is_attacking = False
        self.attack_cooldown = 0.3
        self.spriteOffset = (0, 0)
        self.animation_speeds = {
            AnimationType.IDLE1: 0.35,
            AnimationType.WALK: 0.1,
            AnimationType.ATTACK1: 0.1,
            AnimationType.DEATH: 0.15,
        }
        self.facing_right = True
        self.add_collider((0, 0), self.size, type='enemy_body', solid=True)
        self.patrol_speed = SPEED - 160
        
        # Edge detection sensors (relative to character position)
        self.left_sensor_offset = (-10, self.size[1] + 5)  # Slightly outside left bottom
        self.right_sensor_offset = (self.size[0] + 10, self.size[1] + 5)  # Slightly outside right bottom
        
        if self.animation_manager:
            self.animation_manager.load_animations_from_json(
                self.size,
                image_path="assets/hammer_bot/PackedSpriteSheet.png",
                json_path="assets/hammer_bot/PackedSpriteSheet.json"
            )
            if not self.animation_manager.animationList:
                print("Erro: Nenhuma animação carregada")
            else:
                self.set_animation(AnimationType.IDLE1)

    def set_animation(self, animation_type: AnimationType):
        if not self.animation_manager:
            print("Aviso: Nenhum AnimationManager fornecido")
            return
        for animation in self.animation_manager.animationList:
            if animation.type == animation_type:
                if self.current_animation != animation:
                    self.current_animation = animation
                    self.current_frame = 0
                    self.animation_timer = 0
                    self.is_attacking = (animation_type == AnimationType.ATTACK1)
                    self.update_image()
                return
        print(f"Aviso: Animação {animation_type} não encontrada")

    def update_image(self):
        if self.current_animation and self.current_animation.animation:
            sprite = self.current_animation.animation[self.current_frame].image
            if not self.facing_right:
                sprite = pygame.transform.flip(sprite, True, False)
            self.image = sprite
            self.rect = self.image.get_rect(topleft=(self.position.x, self.position.y))
        else:
            self.image.fill(self.sprite)

    def check_edge(self, platforms):
        """Check if there's a platform below the edge sensors"""
        sensor_size = (5, 5)  # Small rectangle for edge detection
        
        # Left sensor position
        left_sensor_pos = (self.position.x + self.left_sensor_offset[0], 
                         self.position.y + self.left_sensor_offset[1])
        left_sensor_rect = pygame.Rect(left_sensor_pos, sensor_size)
        
        
        # Right sensor position
        right_sensor_pos = (self.position.x + self.right_sensor_offset[0], 
                          self.position.y + self.right_sensor_offset[1])
        right_sensor_rect = pygame.Rect(right_sensor_pos, sensor_size)
        
        left_has_platform = False
        right_has_platform = False
        
        for platform in platforms:
            if left_sensor_rect.colliderect(platform.rect) and platform.colliders[0].type == "terrain":
                left_has_platform = True
            if right_sensor_rect.colliderect(platform.rect) and platform.colliders[0].type == "terrain":
                right_has_platform = True
                
        return left_has_platform, right_has_platform

    def movement_update(self, delta_time, platforms):
        # Apply gravity
        g = (self.gravity + GRAVITY)
        self.position.y += self.speed_vector.y * delta_time + ((g * (delta_time ** 2)) / 2)
        self.speed_vector.y += g * delta_time

        # Check for platform edges
        left_platform, right_platform = self.check_edge(platforms)
        
        # Set movement direction based on facing
        self.speed_vector.x = self.patrol_speed if self.facing_right else -self.patrol_speed
        
        # Turn around if at edge or hitting a wall
        if (self.facing_right and not right_platform) or (not self.facing_right and not left_platform):
            self.facing_right = not self.facing_right
            self.speed_vector.x = -self.speed_vector.x
        
        # Check for wall collision
        # future_position = (self.position.x + self.speed_vector.x * delta_time, self.position.y)
        # future_rect = pygame.Rect(future_position, self.size)
        
        # for platform in platforms:
        #     if future_rect.colliderect(platform.rect) and platform.colliders[0].type == "terrain":
        #         print((f"future_rect: {future_rect}, platform: {platform.rect}"))
        #         print(f"Collision with platform at {platform.rect.topleft}")
        #         # If hitting a wall, reverse direction
        #         self.facing_right = not self.facing_right
        #         self.speed_vector.x = -self.speed_vector.x
        #         break
        
        # Update position   
        self.position.x += self.speed_vector.x * delta_time

        # Update colliders
        for collider in self.colliders:
            collider.update_position()

        self.update_animation(delta_time)

    def update_animation(self, delta_time):
        if not self.animation_manager or not self.current_animation:
            return

        if self.is_attacking:
            self.animation_timer += delta_time
            animation_speed = self.animation_speeds.get(self.current_animation.type, 0.1)
            if self.animation_timer >= animation_speed:
                self.animation_timer -= animation_speed
                self.current_frame += 1
                if self.current_frame >= len(self.current_animation.animation):
                    self.current_frame = 0
                    self.is_attacking = False
                    self.set_animation(AnimationType.IDLE1)
                self.update_image()
            return
        else:
            if abs(self.speed_vector.x) > 0.1:
                self.set_animation(AnimationType.WALK)
            else:
                self.set_animation(AnimationType.IDLE1)

        self.animation_timer += delta_time
        animation_speed = self.animation_speeds.get(self.current_animation.type, 0.1)
        if self.animation_timer >= animation_speed:
            self.animation_timer -= animation_speed
            if self.current_animation.type == AnimationType.JUMP:
                self.current_frame = min(self.current_frame + 1, len(self.current_animation.animation) - 1)
            else:
                self.current_frame = (self.current_frame + 1) % len(self.current_animation.animation)
            self.update_image()
            
            
    def draw_sensors_debug(self, screen, camera):
        """Draw debug rectangles for edge detection sensors."""
        # Update sensor positions
        sensor_size = (5, 5)
        left_sensor_pos = (self.position.x + self.left_sensor_offset[0], 
                          self.position.y + self.left_sensor_offset[1])
        right_sensor_pos = (self.position.x + self.right_sensor_offset[0], 
                           self.position.y + self.right_sensor_offset[1])
        
        # Create sensor rectangles
        left_sensor_rect = pygame.Rect(left_sensor_pos, sensor_size)
        right_sensor_rect = pygame.Rect(right_sensor_pos, sensor_size)
        
        # Apply camera transformation (offset and zoom)
        left_sensor_screen = camera.apply(left_sensor_rect, False)
        right_sensor_screen = camera.apply(right_sensor_rect, False)
        
        # Draw sensors: red for left, blue for right
        pygame.draw.rect(screen, (255, 0, 0), left_sensor_screen, 0)  # Filled red rectangle
        pygame.draw.rect(screen, (0, 0, 255), right_sensor_screen, 0)  # Filled blue 