import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from flask import Flask, request, jsonify, send_from_directory
from automata.regex_parse import add_concat_ops, to_postfix
from automata.nfa import postfix_to_nfa, accepts
from automata.dfa import nfa_to_dfa, dfa_accepts
from automata.min_dfa import minimize_dfa  


app = Flask(__name__)

PROJECT_ROOT = ROOT_DIR
OUT_DIR = os.path.join(PROJECT_ROOT, "out_images")

REGEX = "(k+kkg+kk)*h*+kh*+kkh"

def extract_alphabet(regex: str) -> set[str]:
    return {c for c in regex if c.isalnum()}

with_concat = add_concat_ops(REGEX)
postfix = to_postfix(with_concat)
NFA = postfix_to_nfa(postfix)
ALPHABET = extract_alphabet(REGEX)
DFA = nfa_to_dfa(NFA, ALPHABET)
MIN_DFA = minimize_dfa(DFA)  # once implemented

@app.route("/")
def index():
    return send_from_directory(
        directory=os.path.dirname(__file__),
        path="index.html"
    )


@app.route("/out_images/<path:filename>")
def serve_out_images(filename: str):
    # Serve generated SVGs
    return send_from_directory(OUT_DIR, filename)

@app.route("/api/test", methods=["POST"])
def test_string():
    data = request.get_json()
    word = data.get("word", "")

    nfa_result = accepts(NFA, word)
    dfa_result = dfa_accepts(DFA, word)
    mindfa_result = dfa_accepts(MIN_DFA, word)


    return jsonify(
        {
            "word": word,
            "nfa": nfa_result,
            "dfa": dfa_result,
            "mindfa": mindfa_result,  # this is correct
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
