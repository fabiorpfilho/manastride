class Ui:
    def __init__(self, screen, asset_loader):
        self.screen = screen
        self.asset_loader = asset_loader

    def draw(self, *args, **kwargs):
        raise NotImplementedError("Subclasse DEVE implementar o método draw.")