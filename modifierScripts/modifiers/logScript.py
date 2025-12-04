from modifierScripts.GlobalRegistry import *
from everythingexcepthim import resolve_value
from UnitProfileCode import ProfileData

@register_modifier
class LogHandler(ModifierHandler):
    name = "log"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        for entry in value:
            log.append(entry["text"])
            if "value" in entry:
                newValue = resolve_value(entry["value"],acquired_values)
                log.append(f"{newValue}")