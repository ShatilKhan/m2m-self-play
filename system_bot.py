# B_S — Finite State Machine Health Assistant
# Implements the system bot described in Section 3 of Shah et al. 2018.
# B_S is modelled as a finite state machine (Hopcroft et al. 2006) which
# encodes a set of task-independent rules for constructing system turns.
#
# Each turn consists of:
#   - a response frame: acknowledges the user's last act
#   - an initiate frame: drives the dialogue forward to the next state
#
# States move forward one at a time based on which slots have been filled.
#
# B_S = P(aj+1 | a1...aj, S, C)   [Equation 7 in the paper]
# In this rule-based version P(...) is always 1.0 for exactly one action.

from schema import SCHEMA, get_specialist
from template import render, make_annotation


# FSM states in order
STATES = [
    "GREET",
    "REQUEST_SYMPTOM",
    "REQUEST_BODY_PART",
    "REQUEST_DURATION",
    "REQUEST_SEVERITY",
    "CONFIRM",
    "NOTIFY_SUCCESS",
    "CLOSE",
]

# Maps FSM state → which slot to request
STATE_TO_SLOT = {
    "REQUEST_SYMPTOM":   "symptom",
    "REQUEST_BODY_PART": "body_part",
    "REQUEST_DURATION":  "duration",
    "REQUEST_SEVERITY":  "severity",
}


class SystemBot:
    def __init__(self):
        self.state = "GREET"
        self.filled = {}     # slot → value collected so far

    def step(self, user_act: str, user_slots: dict = None) -> tuple:
        """
        Process the user's act and produce the system's response.
        Returns (annotation_str, utterance_str).

        user_act: the act B_U just performed
        user_slots: slot-value pairs from B_U's act
        """
        user_slots = user_slots or {}

        # Absorb any inform acts from the user
        if user_act == "inform":
            self.filled.update(user_slots)

        # Absorb affirm as confirmation of the confirm state
        if user_act == "affirm" and self.state == "CONFIRM":
            self.state = "NOTIFY_SUCCESS"

        # Absorb negate — go back to re-request the first unfilled slot
        if user_act == "negate" and self.state == "CONFIRM":
            self.state = self._next_unfilled_state()

        # Absorb greeting — move to first request
        if user_act == "greeting" and self.state == "GREET":
            self.state = "REQUEST_SYMPTOM"

        # Produce response based on current state
        return self._respond()

    def _respond(self) -> tuple:
        """Generate the system's act and utterance for the current state."""

        if self.state == "GREET":
            act = "greeting"
            slots = {}
            self.state = "REQUEST_SYMPTOM"

        elif self.state in STATE_TO_SLOT:
            slot = STATE_TO_SLOT[self.state]
            if slot in self.filled:
                # Already have this slot — advance
                self.state = self._advance_state()
                return self._respond()
            act = "request"
            slots = {slot: "?"}
            # Advance state after requesting — next call will be for next slot
            self.state = self._advance_state()

        elif self.state == "CONFIRM":
            act = "confirm"
            slots = dict(self.filled)
            # Don't advance — wait for affirm/negate from user

        elif self.state == "NOTIFY_SUCCESS":
            specialist = get_specialist(
                self.filled.get("symptom", ""),
                self.filled.get("body_part", "")
            )
            act = "notify_success"
            slots = {"specialist": specialist}
            self.state = "CLOSE"

        elif self.state == "CLOSE":
            act = "good_bye"
            slots = {}

        else:
            act = "cant_understand"
            slots = {}

        annotation = make_annotation(act, slots)
        utterance = render(act, slots)
        return annotation, utterance

    def _advance_state(self) -> str:
        """Move to the next FSM state in order."""
        idx = STATES.index(self.state)
        if idx + 1 < len(STATES):
            return STATES[idx + 1]
        return "CLOSE"

    def _next_unfilled_state(self) -> str:
        """Find the first request state whose slot isn't filled yet."""
        for state, slot in STATE_TO_SLOT.items():
            if slot not in self.filled:
                return state
        return "CONFIRM"

    @property
    def done(self) -> bool:
        return self.state == "CLOSE"
