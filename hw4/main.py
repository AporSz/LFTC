class FiniteAutomaton:
    def __init__(self):
        self.states = {"q0", "q1"}
        self.start_state = "q0"
        self.final_states = {"q1"}
        self.transitions = {}

    def add_transition(self, from_state, symbol_class, to_state):
        if from_state not in self.transitions:
            self.transitions[from_state] = []
        self.transitions[from_state].append((symbol_class, to_state))


def convert_fa_to_rg(fa: FiniteAutomaton):
    productions = []
    state_to_nt = {"q0": "S", "q1": "A"}

    for state, trans_list in fa.transitions.items():
        lhs = state_to_nt[state]
        for symbol_class, target_state in trans_list:
            rhs_nt = state_to_nt[target_state]
            productions.append(f"{lhs} -> {symbol_class} {rhs_nt}")
            if target_state in fa.final_states:
                productions.append(f"{lhs} -> {symbol_class}")

    return productions

identifiers = {
    "states": ["q0", "q1"],
    "start_state": "q0",
    "final_states": ["q1"],
    "transitions": {
        ("q0", "letter", "q1"),
        ("q1", "letter_or_digit", "q1"),
    }
}

numbers = {
    "states": ["q0", "q1", "q2"],
    "start_state": "q0",
    "final_states": ["q1", "q2"],
    "transitions": {
        ("q0", "zero", "q1"),
        ("q0", "nonzero", "q2"),
        ("q2", "digit", "q2"),
    }
}

string = {
    "states": ["q0", "q1", "q2"],
    "start_state": "q0",
    "final_states": ["q1", "q2"],
    "transitions": {
        ("q0", "zero", "q1"),
        ("q0", "nonzero", "q2"),
        ("q2", "digit", "q2"),
    }
}

if __name__ == "__main__":
    fa = FiniteAutomaton()
    fa.add_transition("q0", "letter_or_underscore", "q1")
    fa.add_transition("q1", "char_or_digit", "q1")

    print("=== FINITE AUTOMATON (FA) MODEL ===")
    print(f"States: {fa.states}")
    print(f"Start State: {fa.start_state}")
    print(f"Final States: {fa.final_states}")

    print("\n=== GENERATED REGULAR GRAMMAR (RG) PRODUCTIONS ===")
    rg_productions = convert_fa_to_rg(fa)
    for prod in rg_productions:
        print(prod)