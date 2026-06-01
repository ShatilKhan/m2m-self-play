# Scenario generator: samples si = (pi, gi) from the task schema
# Section 2.2 of Shah et al. 2018:
#   pi = user profile (personality vector)
#   gi = user goal (slot-value pairs the user wants to achieve)

import random
from schema import SCHEMA, get_specialist


def sample_goal() -> dict:
    """
    Randomly sample a user goal gi by picking one value per required slot.
    Also derives the target specialist from the sampled symptom + body part.
    Returns a dict of slot → value including the resolved specialist.
    """
    goal = {}
    for slot in SCHEMA["required_slots"]:
        goal[slot] = random.choice(SCHEMA["slots"][slot])

    goal["specialist"] = get_specialist(goal["symptom"], goal["body_part"])
    return goal


def sample_personality() -> dict:
    """
    Sample a user personality profile pi.
    verbose: 0.0 = gives one piece of info per turn, 1.0 = dumps everything at once
    flexible: whether the user accepts alternatives if their preference isn't available
    """
    return {
        "verbose": round(random.uniform(0.0, 1.0), 2),
        "flexible": random.choice([True, False]),
    }


def sample_scenario() -> tuple:
    """Returns (goal, personality): the full scenario si = (pi, gi)."""
    return sample_goal(), sample_personality()
