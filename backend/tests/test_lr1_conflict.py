import pytest
from backend.parser_core import parse_grammar
from backend.first_follow import compute_first_sets, compute_follow_sets
from backend.lr1_builder import build_lr1, build_action_goto_tables, detect_conflicts


@pytest.mark.parametrize("grammar_text,expected_conflict_type", [
    (
        """
        S -> a S | b S | ε
        """, []
    ),
    (
        """
        S -> a S | a
        """, []
    ),
    (
        """
        S -> a S | S a | ε
        """, ["shift/reduce"]
    ),
    (
        """
        S -> A a | B a
        A -> a
        B -> a | ε
        """, []
    ),
])
def test_lr1_conflicts(grammar_text, expected_conflict_type):
    grammar = parse_grammar(grammar_text, None)
    first = compute_first_sets(grammar)
    follow = compute_follow_sets(grammar, first)
    lr1 = build_lr1(grammar, first, follow)
    action, _ = build_action_goto_tables(lr1, grammar)
    result = detect_conflicts(action, lr1["item_sets"])
    if expected_conflict_type:
        assert result["has_conflict"] is True
        found = [c["type"] for c in result["conflicts"]]
        for expected in expected_conflict_type:
            assert any(expected in f for f in found)
    else:
        assert result["has_conflict"] is False
