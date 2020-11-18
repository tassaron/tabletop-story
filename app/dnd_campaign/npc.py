class NPC:
    @classmethod
    def from_template(cls, template: dict):
        """
        Creates a new NPC object using a dict from SRD_monsters as the template
        """
        return cls(
            name=template["name"],
            armour_class=template["armor_class"],
            passive_perception=template["senses"]["passive_perception"],
            proficiencies=[
                f'{proficiency["proficiency"]["name"]} {proficiency["value"]}'
                for proficiency in template["proficiencies"]
            ],
            hit_points=template["hit_points"],
            experience=template["xp"],
            actions=[
                f'{action["name"]} {action["desc"]}' for action in template["actions"]
            ],
            abilities=[
                f'{abil["name"]} {abil["desc"]}'
                for abil in template["special_abilities"]
            ],
            constitution=template["constitution"],
            strength=template["strength"],
            dexterity=template["dexterity"],
            wisdom=template["wisdom"],
            intelligence=template["intelligence"],
            charisma=template["charisma"],
            description="",
        )

    def __init__(
        self,
        name: str,
        armour_class: int,
        passive_perception: int,
        proficiencies: list,
        hit_points: int,
        experience: int,
        actions: list,
        abilities: list,
        constitution: int,
        strength: int,
        dexterity: int,
        wisdom: int,
        intelligence: int,
        charisma: int,
        description: str,
    ):
        self.name = name
        self.armour_class = armour_class
        self.passive_perception = passive_perception
        self.proficiencies = proficiencies
        self.hit_points = hit_points
        self.experience = experience
        self.actions = actions
        self.abilities = abilities
        self.constitution = constitution
        self.strength = strength
        self.dexterity = dexterity
        self.wisdom = wisdom
        self.intelligence = intelligence
        self.charisma = charisma
        self.description = description

    def as_dict(self):
        return {
            key if not key.startswith("_") else None: val
            for key, val in self.__dict__.items()
        }
