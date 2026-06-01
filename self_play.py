# Self-play loop — runs B_U and B_S to generate one dialogue outline
# Implements Section 2.2 of Shah et al. 2018: outline generation via self-play
#
# F1(T) → O = {oi}                     [Equation 3]
# oi = [(t1...tn), (a1...an)]           [Equation 4]
#
# Each dialogue runs until:
#   - B_U emits good_bye, OR
#   - MAX_TURNS is reached (safety limit)
#
# Output: list of turn dicts matching Table 5 format in the paper:
#   {"speaker": "U"/"S", "annotation": "inform(symptom=জ্বর)", "utterance": "আমার জ্বর।"}

from user_bot import UserBot
from system_bot import SystemBot
from scenario import sample_scenario

MAX_TURNS = 20  # paper uses exhaustive generation; we cap for safety


def run_dialogue() -> list:
    """
    Run one full self-play dialogue between B_U and B_S.
    Returns the dialogue outline as a list of turn dicts.
    """
    goal, personality = sample_scenario()
    bu = UserBot(goal, personality)
    bs = SystemBot()

    outline = []
    last_sys_act = None
    last_sys_slots = {}

    for _ in range(MAX_TURNS):
        # --- User turn ---
        result = bu.step(last_sys_act, last_sys_slots)
        if result is None:
            break

        u_annotation, u_utterance = result
        outline.append({
            "speaker": "U",
            "annotation": u_annotation,
            "utterance": u_utterance,
        })

        # Extract act name and slots from annotation for B_S to consume
        u_act, u_slots = _parse_annotation(u_annotation)

        if u_act == "good_bye":
            break

        # --- System turn ---
        s_annotation, s_utterance = bs.step(u_act, u_slots)
        outline.append({
            "speaker": "S",
            "annotation": s_annotation,
            "utterance": s_utterance,
        })

        last_sys_act, last_sys_slots = _parse_annotation(s_annotation)

        if bs.done:
            break

    return outline


def _parse_annotation(annotation: str) -> tuple:
    """
    Parse an annotation string back into (act, slots_dict).
    e.g. "inform(symptom=জ্বর, duration=৩ দিন)" → ("inform", {"symptom": "জ্বর", "duration": "৩ দিন"})
    """
    if "(" not in annotation:
        return annotation, {}

    act = annotation[:annotation.index("(")]
    inner = annotation[annotation.index("(")+1:annotation.rindex(")")]

    slots = {}
    if inner and inner != "":
        for pair in inner.split(", "):
            if "=" in pair:
                k, v = pair.split("=", 1)
                slots[k.strip()] = v.strip()

    return act, slots
