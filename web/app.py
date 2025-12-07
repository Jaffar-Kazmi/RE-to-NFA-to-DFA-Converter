import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from flask import Flask, request, jsonify, send_from_directory
from automata.regex_parse import add_concat_ops, to_postfix
from automata.nfa import postfix_to_nfa, accepts
from automata.dfa import nfa_to_dfa, dfa_accepts, dfa_to_svg, dfa_trace

app = Flask(__name__)

PROJECT_ROOT = ROOT_DIR
OUT_DIR = os.path.join(PROJECT_ROOT, "out_images")


@app.route("/")
def index():
    return send_from_directory(
        directory=os.path.dirname(__file__),
        path="index.html"
    )


@app.route("/out_images/<path:filename>")
def serve_out_images(filename: str):
    return send_from_directory(OUT_DIR, filename)


@app.route("/api/test", methods=["POST"])
def test_string():
    data = request.get_json()
    regex = data.get("regex", "")
    word = data.get("word", "")

    if not regex:
        return jsonify({"error": "regex is required"}), 400

    with_concat = add_concat_ops(regex)
    postfix = to_postfix(with_concat)
    nfa = postfix_to_nfa(postfix)

    alphabet = {c for c in regex if c.isalnum()}
    dfa = nfa_to_dfa(nfa, alphabet)

    nfa_result = accepts(nfa, word)
    dfa_result = dfa_accepts(dfa, word)

    return jsonify({
        "word": word,
        "nfa": nfa_result,
        "dfa": dfa_result,
    })


@app.route("/api/dfa_trace", methods=["POST"])
def dfa_trace_api():
    data = request.get_json()
    regex = data.get("regex", "")
    word = data.get("word", "")

    if not regex:
        return jsonify({"error": "regex is required"}), 400

    with_concat = add_concat_ops(regex)
    postfix = to_postfix(with_concat)
    nfa = postfix_to_nfa(postfix)
    alphabet = {c for c in regex if c.isalnum()}
    dfa = nfa_to_dfa(nfa, alphabet)

    trace = dfa_trace(dfa, word)
    accepted = dfa_accepts(dfa, word)

    return jsonify({
        "accepted": accepted,
        "steps": trace
    })


if __name__ == "__main__":
    app.run(debug=True)
