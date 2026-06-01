# Task schema T = (S, C) from Shah et al. 2018, Section 2.1
# S = set of slots, C = API client (simulated here as the slot value lists themselves)
#
# Slot values sourced from:
# - Bengali Medical Named Entity Recognition dataset (Kaggle: shashwatwork/bengali-medical-dataset, CC BY 4.0)
# - Specialist Classification dataset (same source)
# Top gazetteer-confirmed tokens by frequency used for symptoms and body parts.

SCHEMA = {
    "slots": {
        "symptom": [
            "জ্বর",          # fever
            "ব্যথা",         # pain
            "বমি",           # vomiting
            "জ্বালা",        # burning sensation
            "শ্বাস কষ্ট",   # shortness of breath
            "অস্বস্তি",     # discomfort
            "দুর্বল",        # weakness
            "কাশি",          # cough
            "সর্দি",         # cold/runny nose
            "চুলকানি",       # itching
        ],
        "body_part": [
            "মাথা",   # head
            "বুক",    # chest
            "পেট",    # stomach
            "গলা",    # throat
            "চোখ",    # eye
            "নাক",    # nose
            "কান",    # ear
            "হাত",    # hand
            "পা",     # leg/foot
            "দাঁত",   # teeth
        ],
        "duration": [
            "১ দিন",      # 1 day
            "২ দিন",      # 2 days
            "৩ দিন",      # 3 days
            "১ সপ্তাহ",   # 1 week
            "২ সপ্তাহ",   # 2 weeks
            "১ মাস",      # 1 month
        ],
        "severity": [
            "mild",
            "moderate",
            "severe",
        ],
        "specialist": [
            "Medicine",
            "Skin",
            "Surgery",
            "ENT",
            "Dentist",
            "Cardiologist",
            "Orthopedic",
            "Gynecologist",
            "Ophthalmologist",
        ],
    },
    # Slots B_S must collect before confirming (required slots)
    "required_slots": ["symptom", "body_part", "duration", "severity"],
    # All 15 dialogue acts from Table 4 of the paper
    "dialogue_acts": [
        "greeting",
        "inform",
        "confirm",
        "request",
        "request_alts",
        "offer",
        "select",
        "affirm",
        "negate",
        "notify_success",
        "notify_failure",
        "thank_you",
        "good_bye",
        "cant_understand",
        "other",
    ],
}

# Specialist routing: map symptom → most likely specialist
# Derived from Specialist Classification dataset patterns
SYMPTOM_TO_SPECIALIST = {
    "জ্বর":        "Medicine",
    "ব্যথা":       "Medicine",
    "বমি":         "Medicine",
    "জ্বালা":      "Skin",
    "শ্বাস কষ্ট": "Medicine",
    "অস্বস্তি":   "Medicine",
    "দুর্বল":      "Medicine",
    "কাশি":        "Medicine",
    "সর্দি":       "ENT",
    "চুলকানি":     "Skin",
}

# Body part routing overrides symptom routing when more specific
BODY_PART_TO_SPECIALIST = {
    "মাথা": "Medicine",
    "বুক":  "Cardiologist",
    "পেট":  "Medicine",
    "গলা":  "ENT",
    "চোখ":  "Ophthalmologist",
    "নাক":  "ENT",
    "কান":  "ENT",
    "হাত":  "Orthopedic",
    "পা":   "Orthopedic",
    "দাঁত": "Dentist",
}


def get_specialist(symptom: str, body_part: str) -> str:
    """Route to specialist based on body part first, then symptom."""
    return BODY_PART_TO_SPECIALIST.get(body_part) or SYMPTOM_TO_SPECIALIST.get(symptom, "Medicine")
