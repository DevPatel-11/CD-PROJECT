import pytest
from backend.parser_core import parse_grammar, Grammar
from backend.first_follow import compute_first_sets, compute_follow_sets
from backend.lr1_builder import build_lr1

def test_parse_grammar_basic():
    gtxt = """
    S -> A a
    A -> ε | b
    """
    grammar = parse_grammar(gtxt, "S")
    assert grammar.start == "S"
    assert "A" in grammar.productions

def test_first_follow_sets():
    gtxt = """
    S -> A a
    A -> ε | b
    """
    grammar = parse_grammar(gtxt, "S")
    first = compute_first_sets(grammar)
    follow = compute_follow_sets(grammar, first)
    assert "A" in first
    assert "S" in follow

def test_lr1_builder_items():
    gtxt = """
    S -> A a
    A -> ε | b
    """
    grammar = parse_grammar(gtxt, "S")
    first = compute_first_sets(grammar)
    follow = compute_follow_sets(grammar, first)
    lr1 = build_lr1(grammar, first, follow)
    assert isinstance(lr1["item_sets"], list)
    assert lr1["item_sets"][0]["id"] == 0
