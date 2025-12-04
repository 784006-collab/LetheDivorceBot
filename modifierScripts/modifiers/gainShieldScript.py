from modifierScripts.GlobalRegistry import *
from everythingexcepthim import process_effects, resolve_value
from UnitProfileCode import ProfileData
import random

@register_modifier
class GainShieldHandler(ModifierHandler):
    name = "gainshield"

    async def apply(self, value, modifier_target: ProfileData, acquired_values, effect,
                    log, roll_container, pagename, symbol, **kwargs):
        discard_config = value
        if discard_config is None:
            return

        min = discard_config.get("min")
        max = discard_config.get("max")

        min_val = resolve_value(min, acquired_values)
        max_val = resolve_value(max, acquired_values)
        final_val = random.randint(min_val, max_val)

        modifier_target.gain_shield(final_val)

        if log is not None:
            log.append(f"📜 {modifier_target.name} gains {final_val} Shield")
