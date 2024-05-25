class Colors:
    color_green = "\033[92m"
    color_red = "\033[91m"
    color_default = "\033[0m"


class HealthBar:
    remaining_health_symbol = "█"
    lost_health_symbol = "_"
    bars = 20

    def __init__(self, entity: 'Entity', color: str):
        self.entity = entity
        self.max_health = entity.data.health
        self.color = color

    def draw(self):
        remaining_health_bars = round(self.entity.data.hp / self.max_health * self.bars)
        lost_health_bars = self.bars - remaining_health_bars
        print(f'{self.entity.data.name}. Здоровье: {self.entity.data.hp if self.entity.data.hp >= 0 else 0}/{self.entity.data.health}')
        print(f'|{self.color}{remaining_health_bars * self.remaining_health_symbol}'
              f'{lost_health_bars * self.lost_health_symbol}{Colors.color_default}|')
