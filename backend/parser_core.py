from typing import Dict, List, Tuple, Set, Any, Optional

class Grammar:
    def __init__(self, nonterminals: Set[str], terminals: Set[str], productions: Dict[str, List[List[str]]], start: str):
        self.nonterminals = nonterminals
        self.terminals = terminals
        self.productions = productions
        self.start = start

def parse_grammar(grammar_text: str, start_symbol: Optional[str]) -> Grammar:
    lines = grammar_text.splitlines()
    nonterminals = set()
    productions = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if '->' not in line:
            raise GrammarParseError(f"Invalid production line: {line}")
        lhs, rhs = line.split('->', 1)
        lhs = lhs.strip()
        nonterminals.add(lhs)
        alts = [alt.strip() for alt in rhs.split('|')]
        if lhs not in productions:
            productions[lhs] = []
        for alt in alts:
            syms = alt.split()
            productions[lhs].append(syms)
    # Discover terminals: collect all RHS symbols not in nonterminals or epsilon
    rhs_symbols = set()
    for rules in productions.values():
        for rhs in rules:
            rhs_symbols.update([sym for sym in rhs if sym != 'ε'])
    terminals = rhs_symbols - nonterminals
    # Set start symbol
    start = start_symbol if start_symbol else next(iter(nonterminals))
    if start not in productions:
        raise GrammarParseError(f"Start symbol '{start}' not found in grammar")
    return Grammar(nonterminals, terminals, productions, start)
