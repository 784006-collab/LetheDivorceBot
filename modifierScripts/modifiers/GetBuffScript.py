from modifierScripts.GlobalRegistry import *
from everythingexcepthim import resolve_value, process_effects
from UnitProfileCode import ProfileData

@register_modifier
class GetBuffHandler(ModifierHandler):
    name = "getbuff"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        if not isinstance(value, dict):
            return


        target = kwargs.get("target") or modifier_target

        print(f"{modifier_target.name}: {value}")

        for buff_name, buff_data in value.items():
            print(f"{modifier_target.name}: has gained/lost the buff {buff_name} ")
            is_nextturn = buff_data.get("nextturn", False)
            is_setting = buff_data.get("set", False)

            # Determine target dict
            buff_dest = getattr(modifier_target, "nextturn", {}) if is_nextturn else getattr(modifier_target, "buffs", {})
            if is_nextturn:
                modifier_target.nextturn = getattr(modifier_target, "nextturn", {})
                buff_dest = modifier_target.nextturn.setdefault("buffs", {})
            else:
                modifier_target.buffs = getattr(modifier_target, "buffs", {})
                buff_dest = modifier_target.buffs

            # Lookup buff template
            realbuff = kwargs["buffs"].get(buff_name, {})

            # Resolve values
            resolved_buff = {k: resolve_value(v, acquired_values) for k, v in buff_data.items() if k != "nextturn"}
            stack = resolved_buff.get("stack", 0)
            print(f"STACK: {stack}")
            count = resolved_buff.get("count", 0)
            print(f"COUNT: {count}")

            storage = kwargs.get("data").setdefault("StorageBox", {}).setdefault(modifier_target.name, {})
            storage[f"{buff_name}_stack_change"] = stack
            storage[f"{buff_name}_count_change"] = count

            # Merge with existing buff
            if buff_name in buff_dest:
                existing = buff_dest[buff_name]
                if "stack" in resolved_buff:
                    existing["stack"] = existing.get("stack", 0) + resolved_buff["stack"]
                    if is_setting:
                        existing["stack"] = resolved_buff["stack"]
                if "count" in resolved_buff:
                    existing["count"] = existing.get("count", 0) + resolved_buff["count"]
                    if is_setting:
                        existing["count"] = resolved_buff["count"]
                if "volatile" in resolved_buff:
                    existing["volatile"] = existing.get("volatile", False) or resolved_buff["volatile"]
            else:
                buff_dest[buff_name] = resolved_buff

                # Set defaults for countable buffs
                if realbuff.get("countable") and resolved_buff.get("count", 0) == 0:
                    buff_dest[buff_name]["count"] = 1
                if resolved_buff.get("stack", 0) == 0:
                    if not is_nextturn and buff_name not in modifier_target.buffs:
                        pass
                    else:
                        buff_dest[buff_name]["stack"] = 1

            # Validate buff (remove if depleted)
            buff = buff_dest.get(buff_name)
            if buff:
                if realbuff.get("countable", False):
                    newcount = buff.get("count")
                    if newcount is None or newcount <= 0:
                        del buff_dest[buff_name]
                        print("deleted our buff inside of count")
                newstack = buff.get("stack")
                if newstack is None or newstack <= 0:
                    if not is_nextturn:
                        del buff_dest[buff_name]
                        print("delete shit inside of stack")

                # Clamp max values
                if realbuff.get("max_stack", 99) < buff.get("stack", 0):
                    buff["stack"] = realbuff.get("max_stack", 99)
                if realbuff.get("countable", False) and realbuff.get("max_count", 99) < buff.get("count", 0):
                    buff["count"] = realbuff.get("max_count", 99)

            # activate the appropriate triggers.
            if stack > 0 or count > 0:
                if kwargs["trigger"] != f"oninflict_{buff_name}":
                    await process_effects(modifier_target, target, kwargs["dice"], f"oninflict_{buff_name}",
                                          roll_container, kwargs["source_page"], kwargs["damage"], kwargs["stagger"],
                                          log, pageusetype=kwargs["pageusetype"], data=kwargs["data"],
                                          interaction=kwargs["interaction"])
                if kwargs["trigger"] != f"ongain_{buff_name}":
                    await process_effects(target, modifier_target, kwargs["dice"], f"ongain_{buff_name}",
                                          roll_container, kwargs["source_page"], kwargs["damage"], kwargs["stagger"],
                                          log, pageusetype=kwargs["pageusetype"], data=kwargs["data"],
                                          interaction=kwargs["interaction"])

            if stack < 0 or count < 0:
                if kwargs["trigger"] != f"onspend_{buff_name}":
                    print(f"so now we trigger onspend_{buff_name} with stack: {stack} and count: {count}")
                    await process_effects(modifier_target, target, kwargs["dice"], f"onspend_{buff_name}",
                                          roll_container, kwargs["source_page"], kwargs["damage"], kwargs["stagger"],
                                          log, pageusetype=kwargs["pageusetype"], data=kwargs["data"],
                                          interaction=kwargs["interaction"])

            # Logging
            if log is not None:
                main = f"{stack} stack" if stack != 0 else ""
                connect = " and " if stack != 0 and count != 0 else ""
                extras = f"{count} count" if count != 0 else ""
                buffemoji = symbol.get(buff_name, symbol.get("buff", "✨"))
                if stack != 0 or count != 0:
                    log.append(
                        f"{buffemoji} {buff_name} applied to {modifier_target.name} with {main}{connect}{extras}{' (next turn)' if is_nextturn else ''}. {buffemoji}")
            else:
                print("we didn't meet the previous conditions for bullshit")