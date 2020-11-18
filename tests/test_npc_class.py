from tabletop_story.dnd_campaign import NPC
from dnd_character.monsters import SRD_monsters


def test_create_NPC_from_template():
    npc = NPC.from_template(SRD_monsters["zombie"])
    assert npc.name == "Zombie"
