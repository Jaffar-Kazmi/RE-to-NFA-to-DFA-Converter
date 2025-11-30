from automata.regex_parse import add_concat_ops, to_postfix
from automata.nfa import postfix_to_nfa, accepts, nfa_to_svg
from automata.dfa import nfa_to_dfa, dfa_accepts, dfa_to_svg
from automata.min_dfa import minimize_dfa, mindfa_to_svg

def extract_alphabet(regex: str) -> set[str]:
    return {c for c in regex if c.isalnum()}

def demo(regex: str):
    with_concat = add_concat_ops(regex)
    postfix = to_postfix(with_concat)
    nfa = postfix_to_nfa(postfix)
    nfa_to_svg(nfa, "nfa")

    alphabet = extract_alphabet(regex)
    dfa = nfa_to_dfa(nfa, alphabet)
    dfa_to_svg(dfa, "dfa")

    min_dfa = minimize_dfa(dfa)
    mindfa_to_svg(min_dfa, "mindfa")

    for w in ["", "k", "kh", "kkh", "kg", "kkghh"]:
        print("NFA:", w, "->", accepts(nfa, w))
        print("DFA:", w, "->", dfa_accepts(dfa, w))
        print("MinDFA:", w, "->", dfa_accepts(min_dfa, w))

if __name__ == "__main__":
    demo("(k+kkg+kk)*h*+kh*+kkh")
