from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AnalyzeOptions(BaseModel):
    detect_ambiguity: bool
    build_lr1: bool


class GrammarAnalyzeRequest(BaseModel):
    grammar_text: str
    start_symbol: Optional[str]
    options: AnalyzeOptions


class LR1Item(BaseModel):
    production: str
    dot: int
    lookahead: str


class LR1ItemSet(BaseModel):
    id: int
    items: List[LR1Item]


class ConflictInfo(BaseModel):
    state: int
    symbol: str
    type: str
    details: str


class AmbiguityInfo(BaseModel):
    has_conflict: bool
    conflicts: List[ConflictInfo]


class GrammarAnalyzeResponse(BaseModel):
    first_sets: Dict[str, List[str]]
    follow_sets: Dict[str, List[str]]
    lr1_item_sets: List[LR1ItemSet]
    action_table: Dict[str, Dict[str, str]]
    goto_table: Dict[str, Dict[str, int]]
    ambiguity: AmbiguityInfo
    errors: List[str]


class SimulateParseRequest(BaseModel):
    grammar_text: str
    input_tokens: List[str]
    start_symbol: Optional[str]
    max_steps: int


class ParseStep(BaseModel):
    step: int
    stack: List[Any]
    input: List[str]
    action: str
    notes: str


class SimulateParseResponse(BaseModel):
    steps: List[ParseStep]
    final_status: str
    errors: List[str]
