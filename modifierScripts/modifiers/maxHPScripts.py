from modifierScripts.GlobalRegistry import *
from everythingexcepthim import applystatus, resolve_value
from UnitProfileCode import ProfileData

@register_modifier
class MaxHPDamageHandler(ModifierHandler):
    name = "lowermaxhp"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        value = resolve_value(value, acquired_values)
        modifier_target.take_max_HP_damage(value)
        if log is not None:
            if value >= 0:
                log.append(
                    f"{symbol['stagger']} {modifier_target.name} takes {value} Max HP damage from effect. {symbol['stagger']}")
            else:
                log.append(
                    f"{symbol['buff']} {modifier_target.name} heals {abs(value)} Max HP from effect. {symbol['buff']}")
        await applystatus(kwargs["source"], modifier_target, kwargs["dice"], roll_container,
                          kwargs["damage"], kwargs["stagger"], kwargs["source_page"],
                          log=log, pageusetype=kwargs["pageusetype"], data=kwargs["data"], effect=effect)


@register_modifier
class MaxHPIncreaseHandler(ModifierHandler):
    name = "increasemaxhp"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        value = resolve_value(value, acquired_values)
        modifier_target.increase_max_HP(value)
        if log is not None:
            if value <= 0:
                log.append(
                    f"{symbol['stagger']} {modifier_target.name} takes {value} Max HP damage from effect. {symbol['stagger']}")
            else:
                log.append(
                    f"{symbol['buff']} {modifier_target.name} heals {abs(value)} Max HP from effect. {symbol['buff']}")
        await applystatus(kwargs["source"], modifier_target, kwargs["dice"], roll_container,
                          kwargs["damage"], kwargs["stagger"], kwargs["source_page"],
                          log=log, pageusetype=kwargs["pageusetype"], data=kwargs["data"], effect=effect)
