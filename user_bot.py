# B_U: Agenda-based User Simulator
# Implements the user bot described in Section 3 of Shah et al. 2018,
# based on the agenda-based user simulation of Schatzmann et al. (2007).
#
# How it works:
#   1. At init, convert the user goal into an agenda, an ordered list of
#      (act, slots) pairs representing what the user needs to communicate.
#   2. Each turn: pop the top item off the agenda and speak it.
#   3. If B_S requests a slot that is in the user's goal, push an inform act.
#   4. When the agenda is empty and the goal is satisfied, emit good_bye.
#
# B_U = P(aj | a1...aj-1, pi, gi)   [Equation 6 in the paper]
# In this rule-based version P(...) is always 1.0 for exactly one action.

from template import render, make_annotation


class UserBot:
    def __init__(self, goal: dict, personality: dict):
        """
        goal: dict of slot → value (e.g. {"symptom": "জ্বর", "duration": "৩ দিন", ...})
        personality: dict with "verbose" (float 0-1) and "flexible" (bool)
        """
        self.goal = goal
        self.personality = personality
        self.informed = set()   # slots already communicated to B_S
        self.satisfied = False  # True once B_S confirms the booking

        # Build initial agenda from goal
        # verbose=1.0 means push all informs at once (one big turn)
        # verbose=0.0 means push one inform per turn
        self.agenda = self._build_agenda()

    def _build_agenda(self) -> list:
        """
        Convert goal into a list of (act, slots) tuples.
        Order: greeting first, then one inform per required slot, then thank_you.
        Verbose users batch multiple informs into the first turn.
        """
        agenda = [("greeting", {})]

        inform_slots = {k: v for k, v in self.goal.items() if k != "specialist"}

        if self.personality["verbose"] > 0.5:
            # Verbose: push all informs as a single turn
            agenda.append(("inform", inform_slots))
        else:
            # Not verbose: one inform per slot
            for slot, value in inform_slots.items():
                agenda.append(("inform", {slot: value}))

        return agenda

    def step(self, system_act: str = None, system_slots: dict = None) -> tuple:
        """
        Process the system's last act (if any), then produce the next user turn.
        Returns (annotation_str, utterance_str) or None if conversation is over.

        system_act: the act B_S just performed (e.g. "request", "confirm")
        system_slots: slots referenced in B_S's act
        """
        system_slots = system_slots or {}

        # If B_S confirmed, respond with affirm then queue thank_you + good_bye
        if system_act == "confirm":
            self.satisfied = True
            self.agenda = [("affirm", {}), ("thank_you", {}), ("good_bye", {})]

        # If B_S notified success, just wait for good_bye
        if system_act == "notify_success":
            if not self.agenda:
                self.agenda = [("good_bye", {})]

        # If B_S requested a slot, push an inform for it if we have it and haven't said it
        if system_act == "request" and system_slots:
            for slot in system_slots:
                if slot in self.goal and slot not in self.informed:
                    self.agenda.insert(0, ("inform", {slot: self.goal[slot]}))

        # Nothing left to say
        if not self.agenda:
            return None

        act, slots = self.agenda.pop(0)

        # Track which slots have been informed
        if act == "inform":
            self.informed.update(slots.keys())

        annotation = make_annotation(act, slots)
        utterance = render(act, slots)
        return annotation, utterance

    @property
    def done(self) -> bool:
        return not self.agenda
