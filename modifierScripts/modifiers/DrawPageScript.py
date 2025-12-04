from modifierScripts.GlobalRegistry import *
from everythingexcepthim import resolve_value
from UnitProfileCode import ProfileData
import random

@register_modifier
class DrawSpecificPageHandler(ModifierHandler):
    name = "drawspecific"

    async def apply(
        self, value, modifier_target: ProfileData, acquired_values,
        effect, log, roll_container, pagename, symbol, **kwargs
    ):
        page_to_draw = value
        page = kwargs.get("data", {})["pages"][page_to_draw]
        if page_to_draw in modifier_target.hand:
            modifier_target.hand[page_to_draw]["amount"] += 1
        else:
            modifier_target.hand[page_to_draw] = {
                "cost": page["light_cost"],
                "amount": 1,
            }
            if log is not None:
                log.append(f"📜 {modifier_target.name} draws: {page_to_draw}")
            return

@register_modifier
class DrawPageHandler(ModifierHandler):
    name = "draw"

    async def apply(
        self, value, modifier_target: ProfileData, acquired_values,
        effect, log, roll_container, pagename, symbol, **kwargs
    ):

        # otherwise treat it as a number (resolved)
        draw_val = resolve_value(value, acquired_values)

        if not draw_val:
            return

        # --- your random-draw logic unchanged ---
        deck = modifier_target.deck
        hand = modifier_target.hand
        drawn_cards = []
        deck_counts = {page: data["amount"] for page, data in deck.items()}

        if isinstance(draw_val, float):
            draw_val = int(draw_val)

        for _ in range(draw_val):
            hand_counts = {page: data["amount"] for page, data in hand.items()}
            eligible_pages = [
                page for page, max_count in deck_counts.items()
                if hand_counts.get(page, 0) < max_count
            ]
            eligible_pages = [p for p in eligible_pages if p not in modifier_target.used]

            total_deck_count = sum(data["amount"] for data in deck.values())
            if total_deck_count < 9:
                eligible_pages.extend(["Nothing"] * (9 - total_deck_count))

            if not eligible_pages:
                break

            drawn = random.choice(eligible_pages)
            if drawn == "Nothing":
                drawn_cards.append(drawn)
                continue

            if drawn in hand:
                hand[drawn]["amount"] += 1
            else:
                hand[drawn] = {"cost": deck[drawn]["cost"], "amount": 1}
            drawn_cards.append(drawn)

        if log is not None and drawn_cards:
            log.append(f"📜 {modifier_target.name} draws: {', '.join(drawn_cards)}")