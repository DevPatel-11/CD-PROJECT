from typing import Any, List, Dict, Set, Tuple, Optional
from .parser_core import Grammar


# ----------------------------------------------------------------------
# LR(1) helpers
# ----------------------------------------------------------------------
def _closure_lr1(items: Set[Tuple[str, Tuple[str, ...], int]], grammar: Grammar):
    closure = set(items)
    added = True

    while added:
        added = False
        new_items = set()

        for lhs, rhs, dot in list(closure):
            if dot < len(rhs):
                B = rhs[dot]
                if B in grammar.nonterminals:
                    for prod_rhs in grammar.productions[B]:
                        item = (B, tuple(prod_rhs), 0)
                        if item not in closure:
                            new_items.add(item)

        if new_items:
            closure.update(new_items)
            added = True

    return closure


def _goto_lr1(
    items: Set[Tuple[str, Tuple[str, ...], int]], symbol: str, grammar: Grammar
):
    shifted = set()
    for lhs, rhs, dot in items:
        if dot < len(rhs) and rhs[dot] == symbol:
            shifted.add((lhs, rhs, dot + 1))
    return _closure_lr1(shifted, grammar) if shifted else set()


def _canonical_lr1_collection(grammar: Grammar):
    # Build an augmented grammar locally to detect accept state
    aug_start = grammar.start + "'"
    while aug_start in grammar.nonterminals or aug_start in grammar.terminals:
        aug_start += "'"

    # shallow copy productions and add augmented production
    productions = {k: [list(rhs) for rhs in v] for k, v in grammar.productions.items()}
    productions[aug_start] = [[grammar.start]]
    nonterminals = set(grammar.nonterminals) | {aug_start}
    aug_grammar = Grammar(nonterminals, grammar.terminals, productions, aug_start)

    start_rhs = aug_grammar.productions[aug_grammar.start][0]
    start_item = (aug_grammar.start, tuple(start_rhs), 0)

    c0 = _closure_lr1({start_item}, aug_grammar)

    collection = [c0]
    state_map = {frozenset(c0): 0}
    queue = [c0]

    while queue:
        I = queue.pop(0)
        symbols = set()
        for lhs, rhs, dot in I:
            if dot < len(rhs):
                symbols.add(rhs[dot])

        for X in symbols:
            gotoI = _goto_lr1(I, X, aug_grammar)
            if gotoI:
                key = frozenset(gotoI)
                if key not in state_map:
                    state_map[key] = len(collection)
                    collection.append(gotoI)
                    queue.append(gotoI)

    return collection, state_map, aug_grammar


def build_lr1(grammar, first_sets, follow_sets):
    items, state_map, aug_grammar = _canonical_lr1_collection(grammar)

    lr1_item_sets = []
    for idx, item_set in enumerate(items):
        lr1_item_sets.append(
            {
                "id": idx,
                "items": [
                    {
                        "production": f"{lhs} -> {' '.join(rhs)}",
                        "dot": dot,
                        # keep lookahead key for frontend compatibility
                        "lookahead": "",
                    }
                    for (lhs, rhs, dot) in sorted(item_set)
                ],
            }
        )

    return {
        "item_sets": lr1_item_sets,
        "states": items,
        "state_map": state_map,
        "grammar": aug_grammar,
    }


def build_lr1_action_goto_tables(lr1_result, grammar, follow_sets):
    action = {}
    goto = {}

    state_map = lr1_result["state_map"]
    items = lr1_result["states"]

    aug_grammar = lr1_result.get("grammar")
    aug_start = aug_grammar.start if aug_grammar is not None else None

    for s, item_set in enumerate(items):
        s_str = str(s)
        action[s_str] = {}
        goto[s_str] = {}

        for lhs, rhs, dot in item_set:
            # SHIFT or GOTO
            if dot < len(rhs):
                sym = rhs[dot]

                # SHIFT
                if sym in grammar.terminals:
                    next_items = _goto_lr1(item_set, sym, aug_grammar)
                    next_state = state_map.get(frozenset(next_items))
                    if next_state is not None:
                        entry = f"shift {next_state}"

                        if sym in action[s_str]:
                            parts = set(action[s_str][sym].split(" | "))
                            parts.add(entry)
                            action[s_str][sym] = " | ".join(sorted(parts))
                        else:
                            action[s_str][sym] = entry

                # GOTO
                elif sym in grammar.nonterminals:
                    next_items = _goto_lr1(item_set, sym, aug_grammar)
                    next_state = state_map.get(frozenset(next_items))
                    if next_state is not None:
                        goto[s_str][sym] = next_state

            # REDUCE or ACCEPT
            else:
                if aug_start is not None and lhs == aug_start:
                    action[s_str]["$"] = "accept"
                else:
                    prod_str = f"{lhs} -> {' '.join(rhs)}"
                    entry = f"reduce {prod_str}"

                    # place reduce on all terminals in FOLLOW(lhs)
                    for a in follow_sets.get(lhs, []):
                        if a in action[s_str]:
                            parts = set(action[s_str][a].split(" | "))
                            parts.add(entry)
                            action[s_str][a] = " | ".join(sorted(parts))
                        else:
                            action[s_str][a] = entry

    return action, goto


# ----------------------------------------------------------------------
# Detect Conflicts
# ----------------------------------------------------------------------
def detect_conflicts(action_table, item_sets=None):
    conflicts = []

    for state, row in action_table.items():
        for symbol, cell in row.items():
            actions = [a.strip() for a in cell.split("|")]
            types = [a.split()[0] for a in actions if a != "accept"]

            if types.count("shift") and types.count("reduce"):
                detail_str = " | ".join(actions)
                conflicts.append(
                    {
                        "state": int(state),
                        "symbol": symbol,
                        "type": "shift/reduce",
                        "details": f"Actions: {detail_str}",
                    }
                )

            if types.count("reduce") > 1:
                detail_str = " | ".join(actions)
                conflicts.append(
                    {
                        "state": int(state),
                        "symbol": symbol,
                        "type": "reduce/reduce",
                        "details": f"Actions: {detail_str}",
                    }
                )

    return {"has_conflict": len(conflicts) > 0, "conflicts": conflicts}


# ----------------------------------------------------------------------
# Resolve Conflicts (left associative default)
# ----------------------------------------------------------------------
def resolve_conflicts_default_left(action_table):
    resolutions = []

    for st, row in action_table.items():
        for sym, cell in list(row.items()):
            acts = [a.strip() for a in cell.split("|")]
            types = [a.split()[0] for a in acts if a != "accept"]

            if types.count("shift") and types.count("reduce"):
                reduce_act = [a for a in acts if a.startswith("reduce")][0]
                row[sym] = reduce_act
                resolutions.append(
                    {
                        "state": int(st),
                        "symbol": sym,
                        "type": "shift/reduce",
                        "original": acts,
                        "chosen": reduce_act,
                    }
                )

    return action_table, resolutions


# ----------------------------------------------------------------------
# PARSE SIMULATION
# ----------------------------------------------------------------------
def simulate_parse(
    grammar,
    input_tokens,
    action_table,
    goto_table,
    start_symbol,
    max_steps=250,
):
    stack = [0]
    tokens = list(input_tokens) + ["$"]
    index = 0
    steps = []
    errors = []
    final_status = "in_progress"

    for step_no in range(1, max_steps + 1):
        state = stack[-1]
        token = tokens[index] if index < len(tokens) else "$"
        action = action_table.get(str(state), {}).get(token)

        step_entry = {
            "step": step_no,
            "stack": [str(s) for s in stack],
            "input": tokens[index:],
            "action": action or "error",
            "notes": "",
        }
        steps.append(step_entry)

        if not action:
            errors.append(f"No action for state {state} on symbol '{token}'")
            final_status = "rejected"
            step_entry["notes"] = "Parsing halted due to missing ACTION entry."
            break

        if action == "accept":
            final_status = "accepted"
            step_entry["notes"] = "Input accepted."
            break

        if action.startswith("shift"):
            next_state = int(action.split()[1])
            stack.extend([token, next_state])
            index += 1
            step_entry["notes"] = f"Shift '{token}' and goto state {next_state}."
            continue

        if action.startswith("reduce"):
            prod = action[len("reduce ") :]
            lhs, rhs = prod.split("->")
            lhs = lhs.strip()
            rhs_symbols = rhs.strip().split()

            pop_count = (
                0 if rhs_symbols == ["ε"] or rhs_symbols == [] else len(rhs_symbols)
            )
            for _ in range(2 * pop_count):
                stack.pop()

            prev_state = stack[-1]
            stack.append(lhs)
            goto_state = goto_table.get(str(prev_state), {}).get(lhs)

            if goto_state is None:
                errors.append(f"No goto for state {prev_state} on symbol '{lhs}'")
                final_status = "rejected"
                step_entry["notes"] = "Parsing halted due to missing GOTO entry."
                break

            stack.append(goto_state)
            rhs_desc = (
                "ε"
                if not rhs_symbols or rhs_symbols == ["ε"]
                else " ".join(rhs_symbols)
            )
            step_entry["notes"] = (
                f"Reduce {lhs} -> {rhs_desc}; goto state {goto_state}."
            )
            continue

        errors.append(f"Unknown parser action '{action}'")
        final_status = "rejected"
        step_entry["notes"] = "Parsing halted due to unknown action."
        break
    else:
        final_status = "max_steps"
        errors.append(f"Simulation exceeded {max_steps} steps.")

    return {
        "steps": steps,
        "final_status": final_status,
        "errors": errors,
    }


# ----------------------------------------------------------------------
# SIMULATE PARSING (for frontend/back-end interaction)
# ----------------------------------------------------------------------
def simulate_parse(
    grammar, input_tokens, action_table, goto_table, start_symbol, max_steps=1000
):
    steps = []
    errors = []

    stack = [0]
    tokens = list(input_tokens) + ["$"]
    index = 0

    step_no = 0

    while True:
        if step_no >= max_steps:
            errors.append("Maximum steps exceeded")
            return {"steps": steps, "final_status": "timeout", "errors": errors}

        state = stack[-1]
        lookahead = tokens[index] if index < len(tokens) else "$"

        act = action_table.get(str(state), {}).get(lookahead)

        # Record current snapshot
        steps.append(
            {
                "step": step_no,
                "stack": list(stack),
                "input": tokens[index:],
                "action": act if act is not None else "error",
                "notes": "",
            }
        )

        if not act:
            errors.append(f"No action for state {state} and symbol '{lookahead}'")
            return {"steps": steps, "final_status": "error", "errors": errors}

        act = act.strip()

        # SHIFT
        if act.startswith("shift"):
            try:
                next_state = int(act.split()[1])
            except Exception:
                errors.append(f"Invalid shift action '{act}'")
                return {"steps": steps, "final_status": "error", "errors": errors}

            stack.append(lookahead)
            stack.append(next_state)
            index += 1

        # REDUCE
        elif act.startswith("reduce"):
            prod = act[len("reduce ") :]
            if "->" not in prod:
                errors.append(f"Invalid reduce production '{prod}'")
                return {"steps": steps, "final_status": "error", "errors": errors}

            lhs, rhs = prod.split("->")
            lhs = lhs.strip()
            rhs_symbols = rhs.strip().split()

            # pop 2*len(rhs_symbols) items (state and symbol) unless epsilon
            if rhs_symbols == ["ε"] or rhs_symbols == []:
                pop_len = 0
            else:
                pop_len = 2 * len(rhs_symbols)

            for _ in range(pop_len):
                if stack:
                    stack.pop()

            prev_state = stack[-1]
            stack.append(lhs)
            goto_state = goto_table.get(str(prev_state), {}).get(lhs)
            if goto_state is None:
                errors.append(
                    f"GOTO error: no entry for state {prev_state} and symbol {lhs}"
                )
                return {"steps": steps, "final_status": "error", "errors": errors}

            stack.append(goto_state)

        # ACCEPT
        elif act == "accept":
            steps.append(
                {
                    "step": step_no + 1,
                    "stack": list(stack),
                    "input": ["$"],
                    "action": "accept",
                    "notes": "",
                }
            )
            return {"steps": steps, "final_status": "accepted", "errors": []}

        else:
            # Unknown action
            errors.append(f"Unknown action '{act}'")
            return {"steps": steps, "final_status": "error", "errors": errors}

        step_no += 1
