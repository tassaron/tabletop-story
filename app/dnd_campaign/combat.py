from collections import namedtuple
from random import randint
from math import floor


roll_data = namedtuple("roll_data", ["id", "type"])
character_data = namedtuple("character_data", ["id", "dex"])


def dex_modifier(number):
    return floor((number - 10) / 2)


class Combat:
    def __init__(
        self,
        scene_id=0,
        active=False,
        characters=None,
        npcs=None,
        turn_sequence=None,
        turn_index=0,
    ):
        self.scene_id = int(scene_id)
        self._active = active
        self.characters = (
            [] if characters is None else [character_data(*char) for char in characters]
        )
        self.npcs = [] if npcs is None else [character_data(*npc) for npc in npcs]
        self.turn_index = turn_index
        if turn_sequence is None:
            self.turn_sequence = [] if not active else self.create_turn_sequence()
        else:
            self.turn_sequence = [roll_data(*char) for char in turn_sequence]

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, new_value):
        if new_value == True:
            self.create_turn_sequence()
        else:
            self.turn_sequence = []
        self._active = new_value

    def create_turn_sequence(self):
        """
        The turn sequence is a list of roll_data namedtuples
        """
        self.turn_index = 0
        rolls = {
            character_data(each.id, 0): randint(1, 20) + dex_modifier(each.dex)
            for each in self.characters
        }
        rolls.update(
            {
                character_data(each.id, 1): randint(1, 20) + dex_modifier(each.dex)
                for each in self.npcs
            }
        )
        final_order = {}
        for char, roll in rolls.items():
            while roll in final_order:
                roll += 1
            final_order[roll] = char
        sorted_final_order = {
            k: final_order[k] for k in reversed(sorted(final_order.keys()))
        }
        self.turn_sequence = list(sorted_final_order.values())

    def set_characters(self, characters: list):
        """Receives a list of dnd_character.Character objects"""
        self.characters = [
            character_data(char.id, char.dexterity) for char in characters
        ]

    def set_npcs(self, npcs: list):
        """Receives a list of NPC objects"""
        self.npcs = [character_data(npc.id, npc.dexterity) for npc in npcs]

    def as_dict(self):
        d = {
            key
            if not key.startswith("_")
            else None: val
            if key not in ("characters", "npcs", "turn_sequence")
            else [tuple(k) for k in val]
            for key, val in self.__dict__.items()
        }
        del d[None]
        d["active"] = self._active
        return d

    def __str__(self):
        return str(self.as_dict())

    def next(self):
        self.turn_index += 1
        if self.turn_index == len(self.turn_sequence):
            self.turn_index = 0
