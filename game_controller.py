from typing import Callable

from data_classes import Direction
from entities import Player, Enemy
from event_system import event_system, EventType, Events
from dungeon_generator import DungeonGenerator, Room


class ActionsStorage:
    def __init__(self, player):
        self.player = player
        self.enemy = None
        self.item = None

    def __get_item(self):
        getattr(self.player, 'get_item')(self.item)
        self.item.is_lifted = True
        item = getattr(self.player, 'inventory')[-1]
        print(f'Вы обнаружили {getattr(item, "name")}.\n{getattr(item, "description")}')

    @property
    def actions(self):
        auto_battler = AutoBattler(self.player, self.enemy)
        return {
            "Пойти дальше": lambda: self.player.move(Direction.RIGHT),
            "Вернутся назад": lambda: self.player.move(Direction.LEFT),
            "Атаковать": lambda: auto_battler.fight(),
            "Выйти из подземелья": lambda: event_system.add(Events.game_over_event()),
            "Поднять предмет": lambda: self.__get_item()
        }


class AutoBattler:
    def __init__(self, player: Player, enemy: Enemy):
        self.player = player
        self.enemy = enemy

    def fight(self):
        print('Состояние здоровья у вас:')
        self.player.hp_bar.draw()
        print('Состояние здоровья у противника:')
        self.enemy.hp_bar.draw()
        print('Вы решительно бросаетесь на противника. Завязался бой:')
        while True:
            if not self.player.is_dead:
                print(f'Вы наносите удар!')
                previous_hp = self.enemy.data.hp
                self.player.attack(self.enemy)
                current_hp = self.enemy.data.hp
                if previous_hp == current_hp:
                    print(f'{self.enemy.data.name} смог увернулся от вашего удара.')
                elif current_hp < previous_hp:
                    print(f'Удар пришелся точно в цель! Вы нанесли "{previous_hp - current_hp}" урона цели "{self.enemy.data.name}".')
                print('Состояние здоровья у противника:')
                self.enemy.hp_bar.draw()
                if not self.enemy.is_dead:
                    print(f'{self.enemy.data.name} наносит ответный удар. Берегитесь!')
                    previous_hp = self.player.data.hp
                    self.enemy.attack(self.player)
                    current_hp = self.player.data.hp
                    if previous_hp == current_hp:
                        print('Удар был внезапным, но вы смогли увернулся. Оружие пролетело в сантиметре от вашего лица.')
                    elif current_hp < previous_hp:
                        print(
                            f'На этот раз вы не смогли увернутся... Противник нанес вам "{previous_hp - current_hp}" урона.')
                    print('Состояние здоровья у вас:')
                    self.player.hp_bar.draw()
                else:
                    print(f'\nВы одержали победу над {self.enemy.data.name}! {self.enemy.data.death_description}\n')
                    break
            else:
                print(f'\nВы храбро сражались, но {self.enemy.data.name} оказался сильнее. {self.player.data.death_description}\n')
                event_system.add(Events.game_over_event())
                break


class DungeonManager:
    def __init__(self):
        self.event_system = event_system
        self.creator = DungeonGenerator()
        self.actions_storage = ActionsStorage(self.creator.player)

    def play(self):
        print(f'Добро пожаловать в подземелье, приключенец!\n')
        print(f'Вас зовут: {self.creator.player.data.name}\n'
              f'{self.creator.player.data.description}\n'
              f'В этот поход вы надели самое лучшее, что у вас было:\n'
              f'Ваша броня: {self.creator.player.data.armor.description}.\n'
              f'Ваше оружие: {self.creator.player.data.weapon.description}.\n'
              f'У вас "{self.creator.player.data.hp}" здоровья. Вы чувствуете себя прекрасно!\n')
        self.creator.player.hp_bar.draw()
        while True:
            msg, answer_mapper = self.__lore_maker()
            answer = self.__input_handler(msg)
            try:
                answer_mapper[answer]()
            except KeyError:
                print('Выбирать можно только из доступных действий. Никаких пасхалок тут нет. Попробуйте выбрать действие еще раз.')
            if event := self.event_system.get_event():
                if event.name == EventType.GAME_OVER:
                    print(f'\n{event.name.value}')
                    break

    def __lore_maker(self) -> tuple[str, dict[int, Callable]]:
        current_room: Room = self.creator.dungeon_map[self.creator.player.position.x]
        answer_mapper = dict()
        msg = '\n================================================\n'
        msg += f'Перед вами: {current_room.description}.\n'
        if current_room.enemy:
            if not current_room.enemy.is_dead:
                self.actions_storage.enemy = current_room.enemy
                msg += f'Сквозь тусклый свет, вы замечаете, что в центре комнаты находится: {current_room.enemy.data.description}.\n'
                msg += f'Одет он в: {current_room.enemy.data.armor.description}\n'
                msg += f'В руках у него находится: {current_room.enemy.data.weapon.description}.\n'
                msg += f'Вы можете:\n\t1. Вернутся назад\n\t2. Атаковать\nВаши действия: '
                answer_mapper.update(
                    {
                        1: self.actions_storage.actions['Вернутся назад'],
                        2: self.actions_storage.actions['Атаковать']
                    }
                )
            else:
                msg += f'{current_room.enemy.data.death_description}\n'
                msg += f'Вы можете:\n\t1. Вернутся назад\n\t2. Пойти дальше\nВаши действия: '
                answer_mapper.update(
                    {
                        1: self.actions_storage.actions['Вернутся назад'],
                        2: self.actions_storage.actions['Пойти дальше']
                    }
                )
        elif getattr(current_room, 'item', None) and not getattr(current_room, 'item').is_lifted:
            self.actions_storage.item = current_room.item
            msg += f'В сумраке комнаты вы замечаете любопытный силуэт, это нечто неодушевленное - артефакт давно забытой эпохи.'
            msg += f'Вы можете:\n\t1. Вернутся назад\n\t2. Пойти дальше\n\t3. Поднять предмет\nВаши действия: '
            answer_mapper.update(
                {
                    1: self.actions_storage.actions['Вернутся назад'],
                    2: self.actions_storage.actions['Пойти дальше'],
                    3: self.actions_storage.actions['Поднять предмет']
                }
            )
        else:
            if current_room.is_start:
                msg += f'Вы можете:\n\t1. Пойти дальше\nВаши действия: '
                answer_mapper.update({1: self.actions_storage.actions['Пойти дальше']})
            elif not current_room.is_end and not current_room.is_start:
                msg += f'Вы можете:\n\t1. Вернутся назад\n\t2. Пойти дальше\nВаши действия: '
                answer_mapper.update(
                    {
                        1: self.actions_storage.actions['Вернутся назад'],
                        2: self.actions_storage.actions['Пойти дальше']
                    }
                )
            elif current_room.is_end:
                msg += f'Вы можете:\n\t1. Выйти из подземелья\n\t2. Вернутся назад\nВаши действия: '
                answer_mapper.update(
                    {
                        1: self.actions_storage.actions['Выйти из подземелья'],
                        2: self.actions_storage.actions['Вернутся назад']
                    }
                )
        return msg, answer_mapper

    @staticmethod
    def __input_handler(msg: str):
        try:
            return int(input(msg))
        except ValueError:
            print('Нужно ввести номер действия, например: 1 для действия "1. Пойти дальше".')
            return -1


if __name__ == '__main__':
    dm = DungeonManager()
    dm.play()