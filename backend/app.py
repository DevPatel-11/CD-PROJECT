from flask import Flask, request, jsonify
from flask_cors import CORS

from backend.schemas import (
    GrammarAnalyzeRequest,
    GrammarAnalyzeResponse,
    SimulateParseRequest,
    SimulateParseResponse,
)
from backend.parser_core import parse_grammar
from backend.first_follow import compute_first_sets, compute_follow_sets

from backend.lr1_builder import (
    detect_conflicts,
    resolve_conflicts_default_left,
    simulate_parse,
    build_slr,
    build_slr_action_goto_tables,
)


from backend.exceptions import GrammarParseError
from pydantic import ValidationError
import traceback

app = Flask(__name__)
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5173",
                "http://localhost:5174",
            ]
        }
    },
)


# ------------------------------------------------------------------------------
# API: ANALYZE GRAMMAR
# ------------------------------------------------------------------------------
@app.route("/api/analyze", methods=["POST"])
def analyze_grammar():
    try:
        data = request.get_json(force=True)
        req = GrammarAnalyzeRequest.model_validate(data)

        # Parse grammar
        grammar = parse_grammar(req.grammar_text, req.start_symbol)

        # FIRST & FOLLOW
        first_sets = compute_first_sets(grammar)
        follow_sets = compute_follow_sets(grammar, first_sets)

        response = {
            "first_sets": first_sets,
            "follow_sets": follow_sets,
            "slr_item_sets": [],
            "action_table": {},
            "goto_table": {},
            "ambiguity": {"has_conflict": False, "conflicts": []},
            "resolved_conflicts": [],
            "errors": [],
        }

        # SLR parsing tables
        if getattr(req.options, "build_slr", False):
            slr_result = build_slr(grammar, first_sets, follow_sets)
            response["slr_item_sets"] = slr_result["item_sets"]

            action_table, goto_table = build_slr_action_goto_tables(slr_result, grammar, follow_sets)
            response["action_table"] = action_table
            response["goto_table"] = goto_table

            # Detect conflicts BEFORE resolution
            raw_conflicts = detect_conflicts(action_table)
            response["ambiguity"] = raw_conflicts

            # Resolve conflicts using default LEFT associativity
            action_table, resolved_conflicts = resolve_conflicts_default_left(action_table)
            response["action_table"] = action_table
            response["resolved_conflicts"] = resolved_conflicts

        # Ambiguity flag fix
        if req.options.detect_ambiguity and not response["ambiguity"]["has_conflict"]:
            response["ambiguity"]["has_conflict"] = len(response["ambiguity"]["conflicts"]) > 0

    except ValidationError as ve:
        return jsonify({"errors": [ve.errors()]}), 422
    except GrammarParseError as ge:
        return jsonify({"errors": [str(ge)]}), 400
    except Exception as e:
        return jsonify({"errors": [traceback.format_exc()]}), 500

    return jsonify(GrammarAnalyzeResponse.model_validate(response).model_dump())


# ------------------------------------------------------------------------------
# API: SIMULATE PARSING
# ------------------------------------------------------------------------------
@app.route("/api/simulate", methods=["POST"])
def simulate():
    try:
        data = request.get_json(force=True)
        req = SimulateParseRequest.model_validate(data)

        grammar = parse_grammar(req.grammar_text, req.start_symbol)
        first_sets = compute_first_sets(grammar)
        follow_sets = compute_follow_sets(grammar, first_sets)

        # Build SLR tables for simulation (SLR only)
        slr_result = build_slr(grammar, first_sets, follow_sets)
        action_table, goto_table = build_slr_action_goto_tables(slr_result, grammar, follow_sets)

        resp = simulate_parse(
            grammar,
            req.input_tokens,
            action_table,
            goto_table,
            req.start_symbol,
            req.max_steps,
        )

    except ValidationError as ve:
        return jsonify({"errors": [ve.errors()]}), 422
    except GrammarParseError as ge:
        return jsonify({"errors": [str(ge)]}), 400
    except Exception as e:
        return jsonify({"errors": [traceback.format_exc()]}), 500

    return jsonify(SimulateParseResponse.model_validate(resp).model_dump())


# ENTRY POINT
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
