# main.py
from automata.regex_parse import add_concat_ops, to_postfix
from automata.nfa import postfix_to_nfa, print_nfa, nfa_to_svg, accepts

def build_and_demo(regex: str):
    with_concat = add_concat_ops(regex)
    postfix = to_postfix(with_concat)
    print("After concatenation:", with_concat)
    print("RPN:", postfix)

    nfa = postfix_to_nfa(postfix)
    print_nfa(nfa)

    nfa_to_svg(nfa, "nfa")

    for w in ["", "k", "kh", "kkh", "kg", "kkghh"]:
        print(w, "->", accepts(nfa, w))

if __name__ == "__main__":
    build_and_demo("(k+kkg+kk)*h*+kh*+kkh")
