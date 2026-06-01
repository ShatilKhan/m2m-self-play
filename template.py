# Template utterance generator — maps dialogue act annotations to template strings
# Implements the template utterance generator described in Section 2.2 of Shah et al. 2018
# Covers all 15 dialogue acts from Table 4 of the paper.
#
# Each function takes a slot-value dict and returns a plain template string.
# This is the bridge between symbolic annotations and text — what crowd workers
# would later paraphrase into natural language in Phase 2.


def render(act: str, slots: dict = None) -> str:
    """
    Maps a dialogue act + slot-value dict to a template utterance string.
    act: one of the 15 dialogue acts from Table 4
    slots: dict of slot → value relevant to this act
    """
    slots = slots or {}

    if act == "greeting":
        return "হ্যালো।"  # Hello.

    if act == "inform":
        parts = [f"{v}" for v in slots.values()]
        return "আমার " + " এবং ".join(parts) + "।"  # I have [values].

    if act == "request":
        slot = list(slots.keys())[0] if slots else "তথ্য"
        questions = {
            "symptom":    "আপনার কী সমস্যা হচ্ছে?",           # What is your problem?
            "body_part":  "কোথায় সমস্যা হচ্ছে?",             # Where is the problem?
            "duration":   "কতদিন ধরে এই সমস্যা?",             # How long has this been going on?
            "severity":   "সমস্যাটা কতটা গুরুতর?",            # How severe is the problem?
            "specialist": "আপনি কোন বিশেষজ্ঞ চান?",          # Which specialist do you want?
        }
        return questions.get(slot, f"{slot} সম্পর্কে বলুন।")

    if act == "confirm":
        pairs = ", ".join(f"{k}={v}" for k, v in slots.items())
        return f"আপনার {pairs} — এটা কি ঠিক আছে?"  # Your [slot=value...] — is that correct?

    if act == "affirm":
        return "হ্যাঁ।"  # Yes.

    if act == "negate":
        return "না।"  # No.

    if act == "request_alts":
        return "অন্য কোনো বিকল্প আছে?"  # Are there other options?

    if act == "offer":
        specialist = slots.get("specialist", "বিশেষজ্ঞ")
        return f"{specialist} বিশেষজ্ঞের সাথে দেখা করার পরামর্শ দেওয়া হচ্ছে।"  # Recommending a visit to [specialist].

    if act == "select":
        options = list(slots.values())
        return "এগুলো থেকে বেছে নিন: " + ", ".join(str(o) for o in options) + "।"  # Choose from: [options].

    if act == "notify_success":
        specialist = slots.get("specialist", "বিশেষজ্ঞ")
        return f"আপনাকে {specialist} বিশেষজ্ঞের কাছে পাঠানো হচ্ছে।"  # You are being referred to [specialist].

    if act == "notify_failure":
        return "দুঃখিত, এই মুহূর্তে সেবা দেওয়া সম্ভব হচ্ছে না।"  # Sorry, unable to provide service at this time.

    if act == "thank_you":
        return "ধন্যবাদ।"  # Thank you.

    if act == "good_bye":
        return "ভালো থাকুন।"  # Stay well / Goodbye.

    if act == "cant_understand":
        return "দুঃখিত, বুঝতে পারিনি। আবার বলুন।"  # Sorry, I didn't understand. Please repeat.

    if act == "other":
        return "..."

    return f"[unknown act: {act}]"


def make_annotation(act: str, slots: dict = None) -> str:
    """
    Returns the symbolic annotation string for a dialogue act.
    e.g. inform(symptom=জ্বর, body_part=মাথা)
    Matches the annotation format shown in Table 5 of the paper.
    """
    slots = slots or {}
    if slots:
        pairs = ", ".join(f"{k}={v}" for k, v in slots.items())
        return f"{act}({pairs})"
    return f"{act}()"
