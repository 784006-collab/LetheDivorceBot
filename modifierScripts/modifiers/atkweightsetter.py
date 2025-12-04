from modifierScripts.GlobalRegistry import *
from everythingexcepthim import resolve_value
from UnitProfileCode import ProfileData

@register_modifier
class AtkWeightSetterHandler(ModifierHandler):
    name = "atkweightsetter"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        delta = resolve_value(value, acquired_values)
        if not delta:
            return

        if not pagename:
            return

        print(f"AtkWeightSetterHandler {pagename}")
        print(f"AtkWeightSetterHandler THE STRING IS NOW {str(pagename)}")
        page = kwargs.get("pages")[pagename]
        page["originalattackweight"] = page.get("attackweight", 1)
        page["attackweight"] = delta

        if log := kwargs.get("log"):
            log.append(f"⚡ {modifier_target.name}'s page {pagename} gets set to {delta} attack weight.")