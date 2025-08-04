from spell_system.rune_type import RuneType
from typing import Dict, Optional, Callable
from objects.entity_with_sprite import EntityWithSprite;

class Rune(EntityWithSprite):
    def __init__(self, position, size, name: str, image, rune_type, cost: int, effect: Optional[Callable] = None,):
        super().__init__(position, size, image)
        self.name = name
        self.rune_type = RuneType.MAJOR if rune_type == "major" else RuneType.MINOR
        self.cost = cost
        # Para MINOR (ex: {"slow": 0.5}) ou MAJOR (ex: {})
        self.effect = effect
        
        # self.add_collider((0, 0), (self.size.x, self.size.y), type='rune', active=True)
        
        
        
