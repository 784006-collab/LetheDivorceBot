from modifierScripts.GlobalRegistry import *
from everythingexcepthim import process_effects, resolve_value
from UnitProfileCode import ProfileData
import random

@register_modifier
class DiscardPageHandler(ModifierHandler):
    name = "discard"

    async def apply(self, value, modifier_target: ProfileData, acquired_values, effect,
                    log, roll_container, pagename, symbol, **kwargs):
        """
        Discards cards from the hand based on mode and amount.
        `value` should be a dict with "amount" and optional "mode".
        """
        discard_config = value
        if discard_config is None:
            return

        amount = discard_config.get("amount")
        mode = discard_config.get("mode", "random")
        discard_val = resolve_value(amount, acquired_values)
        data = kwargs.get("data")

        actual_hand = modifier_target.hand

        # Gather pages used this turn
        pages_used_this_turn = {
            action["actorpage"]
            for action in data["action"]
            if action["actor"] == modifier_target.name
        }

        # Eligible discard candidates = hand minus used pages
        discard_candidates = {
            page: info for page, info in actual_hand.items()
            if page not in pages_used_this_turn
        }

        if not discard_val:
            # fallback: discard a specific card if amount is a string page
            if isinstance(amount, str) and amount in discard_candidates:
                actual_hand[amount]["amount"] -= 1
                if actual_hand[amount]["amount"] < 1:
                    del actual_hand[amount]
                if log:
                    log.append(f"📜 {modifier_target.name} discards: {amount}")
            return

        discarded_cards = []

        for _ in range(discard_val):
            if not discard_candidates:
                break

            # Choose card to discard
            if mode == "random":
                discarded = random.choice(list(discard_candidates.keys()))
            elif mode in ("lowest", "highest"):
                sorted_hand = sorted(
                    discard_candidates.keys(),
                    key=lambda page: discard_candidates[page]["cost"],
                    reverse=(mode == "highest")
                )
                discarded = sorted_hand[0]
            else:
                discarded = random.choice(list(discard_candidates.keys()))

            cost = discard_candidates[discarded]["cost"]
            actual_hand[discarded]["amount"] -= 1
            if actual_hand[discarded]["amount"] < 1:
                del actual_hand[discarded]

            discarded_cards.append(discarded)

            # Update StorageBox in data
            storage = data.setdefault("StorageBox", {}).setdefault(modifier_target.name, {})
            storage["discardedThisTurn"] = storage.get("discardedThisTurn", 0) + 1
            storage["lastDiscardedCost"] = cost

            # Trigger on_discard effects
            pages = kwargs.get("pages", {})
            target = kwargs.get("target") or modifier_target
            dice = kwargs.get("dice")
            damage = kwargs.get("damage")
            stagger = kwargs.get("stagger")
            pageusetype = kwargs.get("pageusetype")
            interaction = kwargs.get("interaction")
            log_obj = kwargs.get("log", log)

            if discarded in pages and kwargs["trigger"] != "on_discard":
                await process_effects(
                    modifier_target, target, dice, "on_discard",
                    roll_container, pages[discarded], damage, stagger,
                    log_obj, pageusetype=pageusetype,
                    data=data, interaction=interaction
                )

            # Keep discard_candidates in sync (avoid re-discarding same card)
            if discarded not in actual_hand:
                discard_candidates.pop(discarded, None)

        if log is not None and discarded_cards:
            log.append(f"📜 {modifier_target.name} discards: {', '.join(discarded_cards)}")
