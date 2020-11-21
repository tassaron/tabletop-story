import pytest
from ast import literal_eval
from tabletop_story.dnd_campaign import Combat, NPC
from dnd_character import Character
from dnd_character.monsters import SRD_monsters


@pytest.fixture
def combat():
    c = Combat()
    chars = [Character() for _ in range(6)]
    for i in range(6):
        chars[i].id = i
    npcs = [NPC.from_template(SRD_monsters["zombie"]) for _ in range(6)]
    for i in range(6):
        npcs[i].id = i
    c.set_npcs(npcs)
    c.set_characters(chars)
    yield c


def test_dnd_campaign_combat_set_characters():
    chars = [Character() for _ in range(6)]
    for i in range(6):
        chars[i].id = i
    c = Combat()
    c.set_characters(chars)
    for i in range(6):
        assert c.characters[i] == (chars[i].id, chars[i].dexterity)


def test_dnd_campaign_combat_set_npcs():
    npcs = [NPC.from_template(SRD_monsters["zombie"]) for _ in range(6)]
    for i in range(6):
        npcs[i].id = i
    c = Combat()
    c.set_npcs(npcs)
    for i in range(6):
        assert c.npcs[i] == (npcs[i].id, npcs[i].dexterity)


def test_dnd_campaign_combat_active_turn_sequence(combat):
    combat.active = True
    assert len(combat.turn_sequence) == 12


def test_dnd_campaign_combat_inactive_turn_sequence(combat):
    combat.active = True
    combat.active = False
    assert len(combat.turn_sequence) == 0


def test_dnd_campaign_literal_eval(combat):
    assert literal_eval(str(combat)) == combat.as_dict()


def test_dnd_campaign_literal_eval_active(combat):
    combat.active = True
    test_dnd_campaign_literal_eval(combat)


def test_dnd_campaign_serialization(combat):
    new_combat = Combat(**literal_eval(str(combat)))
    assert new_combat.as_dict() == combat.as_dict()
    assert new_combat.characters == combat.characters
    assert new_combat.npcs == combat.npcs


def test_dnd_campaign_serialization_active(combat):
    combat.active = True
    test_dnd_campaign_serialization(combat)
