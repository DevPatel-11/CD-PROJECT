from typing import Dict, List, Set
from .parser_core import Grammar

def compute_first_sets(grammar: Grammar) -> Dict[str, List[str]]:
    first: Dict[str, Set[str]] = {nt: set() for nt in grammar.nonterminals}
    for t in grammar.terminals:
        first[t] = {t}
    changed = True
    while changed:
        changed = False
        for nt in grammar.nonterminals:
            for rhs in grammar.productions.get(nt, []):
                nullable = True
                for sym in rhs:
                    sym_first = first[sym] if sym in first else {sym}
                    before = len(first[nt])
                    first[nt].update(sym_first - {'ε'})
                    if 'ε' in sym_first:
                        continue
                    else:
                        nullable = False
                        break
                if nullable:
                    if 'ε' not in first[nt]:
                        first[nt].add('ε')
                        changed = True
                if len(first[nt]) > before:
                    changed = True
    return {nt: sorted(first[nt]) for nt in grammar.nonterminals}

def compute_follow_sets(grammar: Grammar, first: Dict[str, List[str]]) -> Dict[str, List[str]]:
    first_sets = {sym: set(first[sym]) if sym in first else {sym} for sym in list(grammar.nonterminals) + list(grammar.terminals)}
    follow: Dict[str, Set[str]] = {nt: set() for nt in grammar.nonterminals}
    follow[grammar.start].add('$')
    changed = True
    while changed:
        changed = False
        for lhs, alternatives in grammar.productions.items():
            for rhs in alternatives:
                for i, curr in enumerate(rhs):
                    if curr in grammar.nonterminals:
                        # Beta = symbols after curr
                        trailer = rhs[i+1:]
                        if trailer:
                            # Add FIRST(trailer) \ {ε} to FOLLOW(curr)
                            beta_first = set()
                            nullable = True
                            for sym in trailer:
                                sym_first = set(first_sets.get(sym, {sym}))
                                beta_first.update(sym_first - {'ε'})
                                if 'ε' in sym_first:
                                    continue
                                else:
                                    nullable = False
                                    break
                            before = set(follow[curr])
                            follow[curr].update(beta_first)
                            if nullable:
                                follow[curr].update(follow[lhs])
                            if set(follow[curr]) != before:
                                changed = True
                        else:
                            before = set(follow[curr])
                            follow[curr].update(follow[lhs])
                            if set(follow[curr]) != before:
                                changed = True
    follow[grammar.start].add('$')  # Always ensure start symbol contains '$'
    return {nt: sorted(follow[nt]) for nt in grammar.nonterminals}
