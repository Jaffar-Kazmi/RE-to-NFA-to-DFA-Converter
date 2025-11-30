from typing import Set, FrozenSet, Dict, List
from .dfa import DFA
from graphviz import Digraph
import os

OUTPUT_DIR = "out_images"

def minimize_dfa(dfa: DFA) -> DFA:
    # 1. Collect all states from transitions + start
    states: Set[FrozenSet] = set()
    for (S, _), T in dfa.transitions.items():
        states.add(S)
        states.add(T)
    states.add(dfa.start)

    # 2. Initial partition: accepting vs non-accepting
    F = set(dfa.accept_states)
    NF = states - F

    partitions: List[Set[FrozenSet]] = []
    if F:
        partitions.append(F)
    if NF:
        partitions.append(NF)

    changed = True
    while changed:
        changed = False
        new_partitions: List[Set[FrozenSet]] = []

        for block in partitions:
            # refine this block
            # grouping by "signature": where each state goes under each symbol
            signature_map: Dict[tuple, Set[FrozenSet]] = {}

            for s in block:
                sig = []
                for a in dfa.alphabet:
                    t = dfa.transitions.get((s, a))
                    # find which partition index t is in
                    idx = None
                    if t is not None:
                        for i, P in enumerate(partitions):
                            if t in P:
                                idx = i
                                break
                    sig.append(idx)
                sig_tuple = tuple(sig)
                signature_map.setdefault(sig_tuple, set()).add(s)

            # signature_map.values() are the refined sub-blocks of block
            if len(signature_map) == 1:
                new_partitions.append(block)
            else:
                changed = True
                new_partitions.extend(signature_map.values())

        partitions = new_partitions

    # 3. Build minimized DFA from partitions
    # Map each old state to its partition index
    state_to_block: Dict[FrozenSet, int] = {}
    for i, block in enumerate(partitions):
        for s in block:
            state_to_block[s] = i

    # new start state
    new_start_block = state_to_block[dfa.start]

    # new accept states: blocks that contain any old accepting state
    new_accept_blocks: Set[int] = set()
    for i, block in enumerate(partitions):
        if any(s in dfa.accept_states for s in block):
            new_accept_blocks.add(i)

    # new transitions
    new_transitions: Dict[tuple, int] = {}
    for i, block in enumerate(partitions):
        rep = next(iter(block))  # representative state
        for a in dfa.alphabet:
            t = dfa.transitions.get((rep, a))
            if t is not None:
                j = state_to_block[t]
                new_transitions[(i, a)] = j

    # wrap minimized DFA in a similar DFA class, but now states are ints (block indices)
    # we can re-use DFA by treating states as ints rather than frozensets
    from .nfa import State  # type placeholder, not used structurally

    class MinDFA(DFA):
        pass

    # But easiest: reuse DFA with generic typing, just ignore type hints:
    # start: int, transitions: (int, symbol) -> int, accept_states: set[int]
    min_start = new_start_block
    min_accept_states = {b for b in new_accept_blocks}
    # remap transitions to have keys as (int, symbol), values as int
    min_transitions: Dict[tuple, int] = dict(new_transitions)

    # Abuse DFA class for now (Python doesn’t enforce types at runtime)
    minimized = DFA(
        start=min_start,                # type: ignore
        transitions=min_transitions,    # type: ignore
        accept_states=min_accept_states, # type: ignore
        alphabet=dfa.alphabet,
    )

    return minimized


def mindfa_to_svg(dfa: DFA, filename: str = "mindfa", dpi: int = 300):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # states are ints now
    states = set()
    for (s, _), t in dfa.transitions.items():
        states.add(s)
        states.add(t)
    states.add(dfa.start)

    idmap = {s: s for s in states}  # identity

    dot = Digraph(format="svg", graph_attr={'dpi': str(dpi)})
    visited = set()

    def visit(s):
        if s in visited:
            return
        visited.add(s)

        sid = str(idmap[s])
        shape = "doublecircle" if s in dfa.accept_states else "circle"
        dot.node(sid, sid, shape=shape)

        for a in dfa.alphabet:
            key = (s, a)
            if key in dfa.transitions:
                t = dfa.transitions[key]
                tid = str(idmap[t])
                dot.edge(sid, tid, label=a)
                visit(t)

    dot.node("start", shape="none", label="")
    dot.edge("start", str(idmap[dfa.start]))

    visit(dfa.start)

    dot.render(filename, directory=OUTPUT_DIR, view=False)
    print("Wrote", os.path.join(OUTPUT_DIR, filename + ".svg"))
