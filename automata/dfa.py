from typing import Dict, Set, FrozenSet
from .nfa import State, NFAFragment, epsilon_closure, move
from graphviz import Digraph
import os

OUTPUT_DIR = "out_images"

class DFA:
    def __init__(
        self,
        start: FrozenSet[State],
        transitions: Dict[tuple, FrozenSet[State]],
        accept_states: Set[FrozenSet[State]],
        alphabet: Set[str],
    ):
        self.start = start
        self.transitions = transitions
        self.accept_states = accept_states
        self.alphabet = alphabet


def nfa_to_dfa(nfa: NFAFragment, alphabet: Set[str]) -> DFA:
    start_set = frozenset(epsilon_closure({nfa.start}))

    transitions: Dict[tuple, FrozenSet[State]] = {}
    accept_states: Set[FrozenSet[State]] = set()
    unmarked: list[FrozenSet[State]] = [start_set]
    all_states: Set[FrozenSet[State]] = {start_set}

    if nfa.accept in start_set:
        accept_states.add(start_set)

    dead_state: FrozenSet[State] | None = None

    while unmarked:
        S = unmarked.pop()

        for a in alphabet:
            T_raw = move(S, a)

            if not T_raw:
                if dead_state is None:
                    dead_state = frozenset()
                    all_states.add(dead_state)
                transitions[(S, a)] = dead_state
            else:
                T = frozenset(epsilon_closure(T_raw))
                transitions[(S, a)] = T

                if T not in all_states:
                    all_states.add(T)
                    unmarked.append(T)
                    if nfa.accept in T:
                        accept_states.add(T)

    if dead_state is not None:
        for a in alphabet:
            transitions[(dead_state, a)] = dead_state

    return DFA(start_set, transitions, accept_states, alphabet)


def dfa_accepts(dfa: DFA, s: str) -> bool:
    current = dfa.start
    for ch in s:
        key = (current, ch)
        if key not in dfa.transitions:
            return False
        current = dfa.transitions[key]
    return current in dfa.accept_states


def enumerate_dfa_states(dfa: DFA) -> Dict[FrozenSet[State], int]:
    """Assign numeric IDs to DFA states in stable order."""
    states = set()
    for (S, _), T in dfa.transitions.items():
        states.add(S)
        states.add(T)
    states.add(dfa.start)
    
    state_list = sorted(states, key=lambda s: (len(s), str(sorted([id(q) for q in s]))))
    return {s: i for i, s in enumerate(state_list)}


def dfa_to_svg(dfa: DFA, filename: str = "dfa", dpi: int = 300):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    idmap = enumerate_dfa_states(dfa)

    dot = Digraph(format="svg", graph_attr={'dpi': str(dpi)})

    # Create nodes with stable IDs
    for state, sid in idmap.items():
        shape = "doublecircle" if state in dfa.accept_states else "circle"
        dot.node(
            name=f"s{sid}",
            label=str(sid),
            shape=shape,
        )

    # Start pseudo-node
    dot.node("start", shape="none", label="")
    dot.edge("start", f"s{idmap[dfa.start]}")

    # Create edges with stable IDs
    for (S, a), T in dfa.transitions.items():
        sid = idmap[S]
        tid = idmap[T]
        # Edge key encodes: from_state-symbol-to_state
        dot.edge(f"s{sid}", f"s{tid}", label=a)

    dot.render(filename, directory=OUTPUT_DIR, view=False)
    print(f"Wrote {os.path.join(OUTPUT_DIR, filename + '.svg')}")


def dfa_trace(dfa: DFA, s: str):
    """Return list of steps with clean numeric state IDs."""
    idmap = enumerate_dfa_states(dfa)
    steps = []

    current = dfa.start
    current_id = idmap[current]
    
    steps.append({
        "pos": 0,
        "char": None,
        "state_id": current_id,
        "next_state_id": current_id,
    })

    pos = 0
    for ch in s:
        pos += 1
        key = (current, ch)
        
        if key not in dfa.transitions:
            steps.append({
                "pos": pos,
                "char": ch,
                "state_id": current_id,
                "next_state_id": None,  # Dead; no transition
            })
            return steps
        
        nxt = dfa.transitions[key]
        next_id = idmap[nxt]
        
        steps.append({
            "pos": pos,
            "char": ch,
            "state_id": current_id,
            "next_state_id": next_id,
        })
        
        current = nxt
        current_id = next_id

    return steps
