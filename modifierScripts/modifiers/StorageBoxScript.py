from modifierScripts.GlobalRegistry import *
from everythingexcepthim import resolve_value
from UnitProfileCode import ProfileData

@register_modifier
class StorageBoxHandler(ModifierHandler):
    name = "storagebox"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        lookup = kwargs["lookup"]
        if kwargs["target"] is not None:
            lookup["target"] = kwargs["target"].name

        for entry in value:
            resolved_name = lookup.get(entry.get("name"), entry.get("name"))
            valuename = lookup.get(entry.get("valuename"), entry.get("valuename"))
            box = kwargs["data"].setdefault("StorageBox", {}).setdefault(resolved_name, {})
            box.setdefault(valuename, 0)

            if valuename == "ClearAllStoragebox":
                box.clear()

                continue

            if entry.get("value") == "Delete":
                box.pop(valuename, None)
                continue

            finalvalue = resolve_value(entry.get("value"), acquired_values)
            print(f"{valuename}: {box[valuename]} (before any alterations)")
            if entry.get("mode", "regular") == "set":
                box[valuename] = finalvalue
            elif entry.get("mode", "regular") == "add":
                box[valuename] += finalvalue
            elif entry.get("mode", "regular") == "lower":
                box[valuename] -= finalvalue
            else:
                box[valuename] += finalvalue

            print(f"{valuename}: {box[valuename]} (after any alterations)")