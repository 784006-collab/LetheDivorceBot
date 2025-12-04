from modifierScripts.GlobalRegistry import *
from everythingexcepthim import resolve_value
from UnitProfileCode import ProfileData

@register_modifier
class SpeedDiceHandler(ModifierHandler):
    name = "speeddice"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        delta = resolve_value(value, acquired_values)
        modifier_target.attack_slot = delta
        modifier_target.attackslotchange = delta

        if log := kwargs.get("log"):
            log.append(f"⚡ {modifier_target.name} gets set to {delta} attack slot (speed dice)")