from modifierScripts.GlobalRegistry import *
from everythingexcepthim import resolve_value, applystatus, calculate_damage
from UnitProfileCode import ProfileData

@register_modifier
class FlatDamageHandler(ModifierHandler):
    name = "flatdamage"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        if not isinstance(value, dict):
            return

        valid_physical = ["slash", "blunt", "pierce"]

        for dtype, dmg_data in value.items():
            if isinstance(dmg_data, (int, float, str)):
                raw_dmg = resolve_value(dmg_data, acquired_values)
                raw_stagger = resolve_value(dmg_data, acquired_values)
            elif isinstance(dmg_data, dict):
                raw_dmg = resolve_value(dmg_data.get("damage", 0), acquired_values)
                raw_stagger = resolve_value(dmg_data.get("stagger", 0), acquired_values)
            else:
                raise TypeError(f"Unsupported damage data type for {dtype}: {type(dmg_data)}")

            type_parts = dtype.split()

            for part in type_parts:
                part = part.strip()


            if kwargs["source"] is not None:
                enemyOffenseLevel = kwargs["source"].offense_level
            else:
                enemyOffenseLevel = modifier_target.offense_level

            if raw_dmg is not None:
                final_dmg = calculate_damage(raw_dmg, modifier_target, kwargs["dice"], attackerOffenseLevel=enemyOffenseLevel, stagger=False, damageTypeOverwrite=dtype)
                modifier_target.take_hp_damage(final_dmg)
                await applystatus(kwargs["source"], modifier_target, kwargs["dice"], roll_container,
                                  kwargs["damage"], kwargs["stagger"], kwargs["source_page"],
                                  log=log, pageusetype=kwargs["pageusetype"], data=kwargs["data"], effect=effect)
                if log is not None:
                    log.append(f"{symbol['stagger']} {modifier_target.name} "
                               f"takes {final_dmg} {dtype} HP damage (resisted from {raw_dmg}). {symbol['stagger']}")

            if raw_stagger is not None and any(part in valid_physical for part in type_parts):
                final_st_dmg = calculate_damage(raw_stagger, modifier_target, kwargs["dice"], attackerOffenseLevel=enemyOffenseLevel, stagger=True, damageTypeOverwrite=dtype)
                modifier_target.take_st_damage(final_st_dmg)
                await applystatus(kwargs["source"], modifier_target, kwargs["dice"], roll_container,
                                  kwargs["damage"], kwargs["stagger"], kwargs["source_page"],
                                  log=log, pageusetype=kwargs["pageusetype"], data=kwargs["data"], effect=effect)
                if log is not None:
                    log.append(f"{symbol['stagger']} {modifier_target.name} "
                               f"takes {final_st_dmg} {dtype} Stagger damage (resisted from {raw_stagger}). {symbol['stagger']}")