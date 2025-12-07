from typing import Dict, Set, FrozenSet
from .nfa import State, NFAFragment, EPSILON, epsilon_closure, move
from graphviz import Digraph
import os

OUTPUT_DIR = "out_images"

class DFA:
    def __init__(
        self,
        start: FrozenSet[State],
        transitions: Dict[tuple, FrozenSet[State]],
        accept_states: Set[FrozenSet[State]],
        alphabet: Set[str]
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
                # Create/use dead state for undefined transitions
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

    # Dead state loops to itself on all symbols
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

import os
from graphviz import Digraph

OUTPUT_DIR = "out_images"

def dfa_to_svg(dfa: DFA, filename: str = "dfa", dpi: int = 300):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # collect all DFA states
    states = set()
    for (S, _), T in dfa.transitions.items():
        states.add(S)
        states.add(T)
    if dfa.start not in states:
        states.add(dfa.start)
    
    # number them
    idmap = {s: i for i, s in enumerate(states)}
    
    dot = Digraph(format="svg", graph_attr={'dpi': str(dpi)})
    visited = set()
    
    def visit(S):
        if S in visited:
            return
        visited.add(S)
        sid = str(idmap[S])
        
        # Check if this state is accepting
        is_accepting = S in dfa.accept_states
        shape = "doublecircle" if is_accepting else "circle"
        dot.node(sid, sid, shape=shape)
        
        for a in sorted(dfa.alphabet):  # sort for consistent ordering
            key = (S, a)
            if key in dfa.transitions:
                T = dfa.transitions[key]
                tid = str(idmap[T])
                dot.edge(sid, tid, label=a)
                visit(T)
    
    dot.node("start", shape="none", label="")
    dot.edge("start", str(idmap[dfa.start]))
    visit(dfa.start)
    
    dot.render(filename, directory=OUTPUT_DIR, view=False)
    print("Wrote", os.path.join(OUTPUT_DIR, filename + ".svg"))