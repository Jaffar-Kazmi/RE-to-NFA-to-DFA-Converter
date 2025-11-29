# automata/nfa.py
import os
from graphviz import Digraph

OUTPUT_DIR = "out_images"
EPSILON = None

class State:
    def __init__(self):
        self.transitions = []

class NFAFragment:
    def __init__(self, start, accept):
        self.start = start
        self.accept = accept

# Thompson primitives
def symbol_nfa(c):
    start = State()
    accept = State()
    start.transitions.append((c, accept))
    return NFAFragment(start, accept)

def concat_nfa(a: NFAFragment, b: NFAFragment) -> NFAFragment:
    a.accept.transitions.append((EPSILON, b.start))
    return NFAFragment(a.start, b.accept)

def union_nfa(a: NFAFragment, b: NFAFragment) -> NFAFragment:
    start = State()
    accept = State()
    start.transitions.append((EPSILON, a.start))
    start.transitions.append((EPSILON, b.start))
    a.accept.transitions.append((EPSILON, accept))
    b.accept.transitions.append((EPSILON, accept))
    return NFAFragment(start, accept)

def star_nfa(a: NFAFragment) -> NFAFragment:
    start = State()
    accept = State()
    start.transitions.append((EPSILON, a.start))
    start.transitions.append((EPSILON, accept))
    a.accept.transitions.append((EPSILON, a.start))
    a.accept.transitions.append((EPSILON, accept))
    return NFAFragment(start, accept)

# postfix -> NFA
def postfix_to_nfa(postfix: str) -> NFAFragment:
    stack = []
    for c in postfix:
        if c.isalnum():
            stack.append(symbol_nfa(c))
        elif c == '*':
            a = stack.pop()
            stack.append(star_nfa(a))
        elif c == '.':
            b = stack.pop()
            a = stack.pop()
            stack.append(concat_nfa(a, b))
        elif c == '+':
            b = stack.pop()
            a = stack.pop()
            stack.append(union_nfa(a, b))
        else:
            raise ValueError(f"Unknown token: {c}")
    return stack.pop()

# state numbering
def enumerate_states(nfa: NFAFragment):
    mapping = {}
    counter = 0
    def dfs(state):
        nonlocal counter
        if state in mapping:
            return
        mapping[state] = counter
        counter += 1
        for _, t in state.transitions:
            dfs(t)
    dfs(nfa.start)
    return mapping

def print_nfa(nfa: NFAFragment):
    idmap = enumerate_states(nfa)
    print("Start:", idmap[nfa.start], "Accept:", idmap[nfa.accept])
    visited = set()
    def dfs(state):
        if state in visited:
            return
        visited.add(state)
        for sym, target in state.transitions:
            label = sym if sym is not None else 'ε'
            print(f"{idmap[state]} --{label}--> {idmap[target]}")
            dfs(target)
    dfs(nfa.start)

def nfa_to_svg(nfa: NFAFragment, filename: str = "nfa", dpi: int = 300):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    idmap = enumerate_states(nfa)
    dot = Digraph(format="svg", graph_attr={'dpi': str(dpi)})
    visited = set()

    def visit(state):
        if state in visited:
            return
        visited.add(state)
        sid = str(idmap[state])
        shape = "doublecircle" if state is nfa.accept else "circle"
        dot.node(sid, sid, shape=shape)
        for sym, target in state.transitions:
            tid = str(idmap[target])
            label = sym if sym is not None else "ε"
            dot.edge(sid, tid, label=label)
            visit(target)

    dot.node("start", shape="none", label="")
    dot.edge("start", str(idmap[nfa.start]))
    visit(nfa.start)

    dot.render(filename, directory=OUTPUT_DIR, view=False)
    print("Wrote", os.path.join(OUTPUT_DIR, filename + ".svg"))

# simulation
def epsilon_closure(states):
    stack = list(states)
    closure = set(states)
    while stack:
        s = stack.pop()
        for sym, t in s.transitions:
            if sym is None and t not in closure:
                closure.add(t)
                stack.append(t)
    return closure

def move(states, c):
    result = set()
    for s in states:
        for sym, t in s.transitions:
            if sym == c:
                result.add(t)
    return result

def accepts(nfa: NFAFragment, s: str) -> bool:
    current = epsilon_closure({nfa.start})
    for ch in s:
        current = epsilon_closure(move(current, ch))
    return nfa.accept in current
