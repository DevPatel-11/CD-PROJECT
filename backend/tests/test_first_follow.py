import pytest
from backend.parser_core import parse_grammar
from backend.first_follow import compute_first_sets, compute_follow_sets


@pytest.mark.parametrize(
    "grammar_text,expected_first,expected_follow",
    [
        (
            """
        S -> A a
        A -> ε | b
        """,
            {"S": ["a", "b"], "A": ["ε", "b"]},
            {"S": ["$"], "A": ["a"]},
        ),
        (
            """
        E -> T E'
        E' -> + T E' | ε
        T -> F T'
        T' -> * F T' | ε
        F -> ( E ) | id
        """,
            {
                "E": ["(", "id"],
                "E'": ["+", "ε"],
                "T": ["(", "id"],
                "T'": ["*", "ε"],
                "F": ["(", "id"],
            },
            {
                "E": [")", "$"],
                "E'": [")", "$"],
                "T": ["+", ")", "$"],
                "T'": ["+", ")", "$"],
                "F": ["*", "+", ")", "$"],
            },
        ),
    ],
)
def test_first_follow(grammar_text, expected_first, expected_follow):
    grammar = parse_grammar(grammar_text, None)
    actual_first = compute_first_sets(grammar)
    actual_follow = compute_follow_sets(grammar, actual_first)
    print("GRAMMAR:", grammar.terminals, grammar.nonterminals)
    print("FIRST:", actual_first)
    print("FOLLOW:", actual_follow)
    for nt in expected_first:
        assert set(actual_first[nt]) >= set(expected_first[nt])
    for nt in expected_follow:
        assert set(actual_follow[nt]) >= set(expected_follow[nt])
