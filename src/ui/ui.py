class Ui:
    def __init__(self, screen):
        self.screen = screen

    def draw(self, *args, **kwargs):
        raise NotImplementedError("Subclasse DEVE implementar o método draw.")