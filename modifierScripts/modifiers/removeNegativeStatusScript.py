from modifierScripts.GlobalRegistry import *
from everythingexcepthim import resolve_value
from UnitProfileCode import ProfileData
import random

@register_modifier
class RemoveTypeEffects(ModifierHandler):
    name = "removetypeeffects"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        funnyDict = value

        delta = resolve_value(funnyDict["value"], acquired_values)
        typeToPop = funnyDict.get("type")

        buffs = modifier_target.buffs
        buffsStaticData = kwargs["data"]["buffs"]

        print(f"the delta is: {delta}")
        print(f"the typeToPop is: {typeToPop}")
        print(f"BEFORE THE FALL: {buffs}")

        buffsToPass = [
            buff_name
            for buff_name in buffs.keys()
            if buffsStaticData.get(buff_name, {}).get("type") == typeToPop
        ]
        print(f"AFTER THE FALL: {buffsToPass}")

        to_remove = random.sample(buffsToPass, k=min(delta, len(buffsToPass)))

        # Remove them
        for buff_name in to_remove:
            del buffs[buff_name]
            if log is not None:
                buffemoji = symbol.get(buff_name, symbol.get("buff", "✨"))
                log.append(f"⚡ {modifier_target.name} has removed the {typeToPop} status effect {buffemoji} {buff_name} from self")