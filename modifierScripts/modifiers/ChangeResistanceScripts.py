from modifierScripts.GlobalRegistry import *
from everythingexcepthim import resolve_value
from UnitProfileCode import ProfileData

@register_modifier
class OverWriteResistanceHandler(ModifierHandler):
    name = "overwriteresistance"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        if not isinstance(value, dict):
            return

        physical_resistances = {"slash", "pierce", "blunt"}
        sin_resistances = {"Wrath", "Lust", "Sloth", "Gluttony", "Gloom", "Envy", "Pride", "White", "Black", "none" }

        for res, res_value in value.items():
            resolved_value = resolve_value(res_value, acquired_values)

            if res in physical_resistances:
                modifier_target.resistances[res] = resolved_value
                dict_name = "resistances"
            else:
                modifier_target.sin_resistances[res] = resolved_value
                dict_name = "sin_resistances"

            if log := kwargs.get("log"):
                log.append(f"🛡 {modifier_target.name} sets {dict_name} '{res}' to {resolved_value}")

@register_modifier
class IncreaseResistancesHandler(ModifierHandler):
    name = "increaseresistance"

    async def apply(self, value, modifier_target: ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        if not isinstance(value, dict):
            return

        resistanceBlock = value
        effectSource = resistanceBlock.get("source", "")
        isLower = resistanceBlock.get("lowerResistance", False)

        physical_resistances = {"slash", "pierce", "blunt"}
        sin_resistances = {"Wrath", "Lust", "Sloth", "Gluttony", "Gloom", "Envy", "Pride", "White", "Black", "none" }

        for res, res_value in resistanceBlock.items():
            if res not in sin_resistances and res not in physical_resistances:
                print(f"{res} is not in sin_resistances or physical_resistances.")
                print(res not in sin_resistances and res not in physical_resistances)
                continue

            resolved_value = resolve_value(res_value, acquired_values) / 10
            if isLower:
                resolved_value = -abs(resolved_value)
            if res in physical_resistances:
                modifier_target._phys_resistance_modifiers[res][effectSource] = resolved_value
                modifier_target.calcResistancePhysical(res)
                dict_name = "resistances"
            else:
                modifier_target._sin_resistance_modifiers[res][effectSource] = resolved_value
                modifier_target.calcResistanceSin(res)
                dict_name = "sin_resistances"

            if log is not None:
                log.append(f"🛡 {modifier_target.name} sets {dict_name} '{res}' to {getattr(modifier_target, dict_name)[res]}")