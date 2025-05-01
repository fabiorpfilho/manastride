from objects.sprite import Sprite
from objects.animation_type import AnimationType

class Animation:
    def __init__(self, animation = list[Sprite], type: AnimationType ):
        self.animation = animation
        self.type = type
