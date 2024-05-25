class DungeonGenerator:
    def __init__(self, dungeon_map: list[str] = None):
        self.__dungeon = dungeon_map if dungeon_map else ['St', ' ', 'E', 'E', ' ', 'E', 'Ex']
        self.game_data = self.__load_game_data()
        self.dungeon_map = self.__create_dungeon()
        self.player = self.__create_player()

