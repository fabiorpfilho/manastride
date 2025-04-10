from game_controller import GameController




# Já em relação à POO, ao se referir a um atributo de uma classe, usar o this para deixar claro que é de uma classe e não uma variavel qualquer
# ou sempre nomear o atributo com m_ (member), ex: m_position


if __name__ == "__main__":
    game = GameController()
    game.run()
#Colocar tipo nos prototipos das funções, em python é possivel forçar isso