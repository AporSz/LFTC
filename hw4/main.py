class FiniteAutomaton:
    def __init__(self, states, start_state, final_states):
        self.states = states
        self.start_state = start_state
        self.final_states = final_states
        self.transitions = {}

    def add_transition(self, from_state, symbol_class, to_state):
        if from_state not in self.transitions:
            self.transitions[from_state] = []
        self.transitions[from_state].append((symbol_class, to_state))

def convert_fa_to_rg(fa: FiniteAutomaton):
    productions = []
    state_to_nt = {"q0": "S", "q1": "A", "q2": "B", "q3": "C", "q4": "D", "q5": "E", "q6": "F"}

    for state, trans_list in fa.transitions.items():
        lhs = state_to_nt[state]
        for symbol_class, target_state in trans_list:
            rhs_nt = state_to_nt[target_state]
            productions.append(f"{lhs} -> {symbol_class} {rhs_nt}")
            # if target_state in fa.final_states:
            #     productions.append(f"{lhs} -> {symbol_class}")

    for final_state in fa.final_states:
        productions.append(f"{state_to_nt[final_state]} -> epsilon")

    return productions

def write_rg_for_fa(fa_mapping, name, filename):
    fa = FiniteAutomaton(fa_mapping["states"], fa_mapping["start_state"], fa_mapping["final_states"])
    for transition in fa_mapping["transitions"]:
        fa.add_transition(transition[0], transition[1], transition[2])

    rg_productions = convert_fa_to_rg(fa)
    with open(filename, "w") as output_file:
        output_file.write(f"=== FINITE AUTOMATON (FA) MODEL FOR {name} ===\n")
        output_file.write(f"States: {fa.states}\n")
        output_file.write(f"Start State: {fa.start_state}\n")
        output_file.write(f"Final States: {fa.final_states}\n")
        output_file.write("\n=== GENERATED REGULAR GRAMMAR (RG) PRODUCTIONS ===\n")
        for production in rg_productions:
            output_file.write(f"{production}\n")

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

strings = {
    "states": ["q0", "q1", "q2"],
    "start_state": "q0",
    "final_states": ["q2"],
    "transitions": {
        ("q0", "first_quote", "q1"),
        ("q1", "character", "q1"),
        ("q1", "second_quote", "q2"),
    }
}

if __name__ == "__main__":
    write_rg_for_fa(identifiers, "identifiers", "identifiers_rg.txt")
    write_rg_for_fa(numbers, "numbers", "numbers_rg.txt")
    write_rg_for_fa(strings, "strings", "strings_rg.txt")
