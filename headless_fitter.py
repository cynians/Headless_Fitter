"""Match two name-only JSON or YAML lists without an ontology."""

from __future__ import annotations

import argparse
import ast
import json
import re
from dataclasses import asdict, dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable, Sequence


DEFAULT_MINIMUM_SCORE = 45

@dataclass(frozen=True)
class CandidateMatch:
    target_index: int
    target: str
    score: int
    method: str
    matched_terms: tuple[str, ...]


@dataclass(frozen=True)
class NameMatch:
    source_index: int
    source: str
    target_index: int
    target: str
    score: int
    method: str
    matched_terms: tuple[str, ...]


@dataclass
class _AssignmentSearch:
    column: int
    minimum: list[float]
    used: list[bool]


def _expand_name_syntax(value: str) -> str:
    value = re.sub(r"(?i)\bsign[\s_-]*in\b", "login", value)
    value = value.replace("%", " percentage ").replace("&", " and ")
    value = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", value)
    value = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", value)
    value = re.sub(r"(?<=[A-Za-z])(?=[0-9])", " ", value)
    return re.sub(r"(?<=[0-9])(?=[A-Za-z])", " ", value)


def _clean_name_tokens(value: str) -> list[str]:
    value = value.lower().replace("_", " ").replace("-", " ")
    return re.sub(r"[^a-z0-9 ]", " ", value).split()


def _normalize_number(token: str) -> str:
    return str(int(token)) if token.isdigit() else token


def normalize_and_tokenize(text: object) -> tuple[str, ...]:
    """Normalize a name into ordered tokens."""
    value = _expand_name_syntax(str(text or "").strip())
    return tuple(_normalize_number(token) for token in _clean_name_tokens(value) if token)


def _singularize(token: str) -> str:
    if len(token) > 4 and token.endswith("ies"):
        return f"{token[:-3]}y"
    if len(token) > 4 and token.endswith("sses"):
        return token[:-2]
    if len(token) > 3 and token.endswith("s") and not token.endswith(("ss", "us", "is")):
        return token[:-1]
    return token


def canonical_tokens(text: object) -> tuple[str, ...]:
    """Return singularized tokens."""
    return tuple(_singularize(token) for token in normalize_and_tokenize(text))


def _acronym(tokens: Sequence[str]) -> str:
    return "".join(token[0] for token in tokens if token)


def _has_acronym_match(left: Sequence[str], right: Sequence[str]) -> bool:
    if len(left) == 1 and len(left[0]) >= 2 and len(right) >= 2:
        return left[0] == _acronym(right)
    if len(right) == 1 and len(right[0]) >= 2 and len(left) >= 2:
        return right[0] == _acronym(left)
    return False


def _partial_similarity(left: str, right: str) -> float:
    if min(len(left), len(right)) < 3:
        return 0.0
    contains = left in right or right in left
    similarity = SequenceMatcher(None, left, right).ratio()
    if not contains and similarity < 0.82:
        return 0.0
    return max(similarity, 0.88 if contains else 0.0)


def _partial_possibilities(left: Sequence[str], right: Sequence[str], exact: set[str]):
    possibilities = []
    for left_token in (token for token in left if token not in exact):
        for right_token in (token for token in right if token not in exact):
            similarity = _partial_similarity(left_token, right_token)
            if similarity:
                possibilities.append((similarity, left_token, right_token))
    return sorted(possibilities, key=lambda item: (-item[0], item[1], item[2]))


def _take_partial(pair, used_left: set[str], used_right: set[str]) -> bool:
    _, left_token, right_token = pair
    if left_token in used_left or right_token in used_right:
        return False
    used_left.add(left_token)
    used_right.add(right_token)
    return True


def _partial_token_pairs(left: Sequence[str], right: Sequence[str], exact: set[str]):
    pairs, used_left, used_right = [], set(), set()
    for pair in _partial_possibilities(left, right, exact):
        if _take_partial(pair, used_left, used_right):
            similarity, left_token, right_token = pair
            pairs.append((left_token, right_token, similarity))
    return pairs


def _normalized_exact_match(left: str, right: str):
    if not left or not right:
        return 0, "none", ()
    if left == right:
        return 100, "normalized_exact", tuple(sorted(set(left.split())))
    if left.replace(" ", "") == right.replace(" ", ""):
        return 99, "separator_only", tuple(sorted(set(left.split())))
    return None


def _canonical_exact_match(left: Sequence[str], right: Sequence[str]):
    exact = set(left) & set(right)
    if set(left) != set(right):
        return None
    method = "token_reorder" if left != right else "canonical_exact"
    return 96, method, tuple(sorted(exact))


def _similarity_metrics(left, right, exact, pairs):
    overlap = len(exact) + sum(pair[2] for pair in pairs)
    smaller = max(1, min(len(set(left)), len(set(right))))
    union = max(1.0, len(set(left)) + len(set(right)) - overlap)
    coverage, jaccard = min(1.0, overlap / smaller), min(1.0, overlap / union)
    ordered = SequenceMatcher(None, " ".join(left), " ".join(right)).ratio()
    sorted_ratio = SequenceMatcher(None, " ".join(sorted(left)), " ".join(sorted(right))).ratio()
    return coverage, jaccard, max(ordered, sorted_ratio)


def _score_metrics(metrics) -> int:
    coverage, jaccard, similarity = metrics
    return max(0, min(95, round(65 * coverage + 20 * jaccard + 10 * similarity)))


def _match_evidence(exact: set[str], pairs) -> tuple[str, ...]:
    evidence = list(sorted(exact))
    evidence.extend(f"{left}~{right}" for left, right, _ in pairs)
    return tuple(evidence)


def _match_method(exact: set[str], pairs, score: int) -> str:
    if exact and pairs:
        return "token_and_partial"
    if exact:
        return "token_overlap"
    if pairs:
        return "partial_token"
    return "weak_similarity" if score else "none"


def _score_canonical_names(left: Sequence[str], right: Sequence[str]):
    if _has_acronym_match(left, right):
        acronym = left[0] if len(left) == 1 else right[0]
        return 90, "acronym", (acronym,)
    exact = set(left) & set(right)
    pairs = _partial_token_pairs(left, right, exact)
    score = _score_metrics(_similarity_metrics(left, right, exact, pairs))
    return score, _match_method(exact, pairs, score), _match_evidence(exact, pairs)


def score_names(left_name: str, right_name: str) -> tuple[int, str, tuple[str, ...]]:
    """Score two names from 0 to 100 and return their evidence."""
    left_normalized = " ".join(normalize_and_tokenize(left_name))
    right_normalized = " ".join(normalize_and_tokenize(right_name))
    direct = _normalized_exact_match(left_normalized, right_normalized)
    if direct:
        return direct
    left, right = canonical_tokens(left_name), canonical_tokens(right_name)
    direct = _canonical_exact_match(left, right) if left and right else None
    return direct or _score_canonical_names(left, right) if left and right else (0, "none", ())


def _candidate(source_name: str, target: str, target_index: int) -> CandidateMatch:
    score, method, terms = score_names(source_name, target)
    return CandidateMatch(target_index, target, score, method, terms)


def rank_candidates(source_name: str, targets: Sequence[str], *, limit: int | None = None):
    """Rank every target for one source with stable tie-breaking."""
    ranked = [_candidate(source_name, target, index) for index, target in enumerate(targets)]
    ranked.sort(key=lambda item: (-item.score, item.target.lower(), item.target_index))
    return ranked if limit is None else ranked[: max(0, limit)]


class _AssignmentSolver:
    def __init__(self, weights: Sequence[Sequence[int]]):
        self.rows, self.columns = len(weights), len(weights[0])
        maximum = max(max(row) for row in weights)
        self.costs = [[maximum - value for value in row] for row in weights]
        self.u = [0] * (self.rows + 1)
        self.v = [0] * (self.columns + 1)
        self.p = [0] * (self.columns + 1)
        self.way = [0] * (self.columns + 1)

    def _new_search(self, row: int) -> _AssignmentSearch:
        self.p[0] = row
        return _AssignmentSearch(0, [float("inf")] * (self.columns + 1), [False] * (self.columns + 1))

    def _relax(self, row: int, column: int, previous: int, state: _AssignmentSearch):
        current = self.costs[row - 1][column - 1] - self.u[row] - self.v[column]
        if current < state.minimum[column]:
            state.minimum[column] = current
            self.way[column] = previous

    def _scan(self, row: int, previous: int, state: _AssignmentSearch):
        delta, next_column = float("inf"), 0
        for column in range(1, self.columns + 1):
            if state.used[column]:
                continue
            self._relax(row, column, previous, state)
            if state.minimum[column] < delta:
                delta, next_column = state.minimum[column], column
        return delta, next_column

    def _shift(self, state: _AssignmentSearch, delta: float):
        for column in range(self.columns + 1):
            if state.used[column]:
                self.u[self.p[column]] += delta
                self.v[column] -= delta
            else:
                state.minimum[column] -= delta

    def _advance(self, state: _AssignmentSearch) -> bool:
        state.used[state.column] = True
        row, previous = self.p[state.column], state.column
        delta, next_column = self._scan(row, previous, state)
        self._shift(state, delta)
        state.column = next_column
        return self.p[state.column] != 0

    def _rewire(self, column: int):
        while True:
            previous = self.way[column]
            self.p[column] = self.p[previous]
            column = previous
            if column == 0:
                return

    def _augment(self, row: int):
        state = self._new_search(row)
        while self._advance(state):
            pass
        self._rewire(state.column)

    def solve(self) -> list[int]:
        for row in range(1, self.rows + 1):
            self._augment(row)
        result = [-1] * self.rows
        for column in range(1, self.columns + 1):
            if self.p[column]:
                result[self.p[column] - 1] = column - 1
        return result


def _maximum_weight_assignment(weights: Sequence[Sequence[int]]) -> list[int]:
    if not weights:
        return []
    if len(weights[0]) < len(weights):
        raise ValueError("Assignment requires at least as many columns as rows.")
    return _AssignmentSolver(weights).solve()


def _score_matrix(sources: Sequence[str], targets: Sequence[str]):
    return [[score_names(source, target) for target in targets] for source in sources]


def _assignment_weights(matrix, source_count: int, minimum_score: int):
    return [[item[0] for item in row] + [minimum_score] * source_count for row in matrix]


def _selected_match(source_index, target_index, sources, targets, matrix, minimum_score):
    if target_index < 0 or target_index >= len(targets):
        return None
    score, method, terms = matrix[source_index][target_index]
    if score < minimum_score:
        return None
    return NameMatch(source_index, sources[source_index], target_index, targets[target_index], score, method, terms)


def _selected_matches(assignment, sources, targets, matrix, minimum_score):
    matches = [_selected_match(index, target, sources, targets, matrix, minimum_score) for index, target in enumerate(assignment)]
    return sorted((match for match in matches if match), key=lambda item: item.source_index)


def _unmatched_items(names: Sequence[str], matched_indexes: set[int]):
    return [{"index": index, "name": name} for index, name in enumerate(names) if index not in matched_indexes]


def _match_report(matches, sources: Sequence[str], targets: Sequence[str]):
    source_indexes = {match.source_index for match in matches}
    target_indexes = {match.target_index for match in matches}
    return {"matches": [asdict(match) for match in matches], "unmatched_source": _unmatched_items(sources, source_indexes), "unmatched_target": _unmatched_items(targets, target_indexes)}


def fit_loudly(sources: Sequence[str], targets: Sequence[str], *, minimum_score: int = DEFAULT_MINIMUM_SCORE):
    """Globally match two lists while using each target at most once."""
    if not 0 <= minimum_score <= 100:
        raise ValueError("minimum_score must be between 0 and 100")
    matrix = _score_matrix(sources, targets)
    weights = _assignment_weights(matrix, len(sources), minimum_score)
    assignment = _maximum_weight_assignment(weights) if sources else []
    matches = _selected_matches(assignment, sources, targets, matrix, minimum_score)
    return _match_report(matches, sources, targets)


def _silent_candidates(source: str, targets: Sequence[str], minimum_score: int):
    ranked = rank_candidates(source, targets)
    return [{"candidate": item.target, "score": item.score} for item in ranked if item.score >= minimum_score]


def fit_silently(sources: Sequence[str], targets: Sequence[str]):
    """Map each source to its ranked candidates at or above the score cutoff."""
    return {
        source: _silent_candidates(source, targets, DEFAULT_MINIMUM_SCORE)
        for source in sources
    }


def _yaml_rows(text: str):
    rows = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and stripped != "---":
            rows.append((line_number, stripped))
    return rows


def _quoted_yaml_value(value: str, line_number: int) -> str:
    try:
        parsed = ast.literal_eval(value)
    except (SyntaxError, ValueError) as exc:
        raise ValueError(f"Line {line_number}: invalid quoted YAML string") from exc
    if not isinstance(parsed, str):
        raise ValueError(f"Line {line_number}: list item must be a string")
    return parsed


def _yaml_item(line_number: int, line: str) -> str:
    if not line.startswith("-"):
        raise ValueError(f"Line {line_number}: expected a top-level YAML list item")
    value = line[1:].strip()
    if not value:
        raise ValueError(f"Line {line_number}: empty YAML list item")
    if value[0] in {'\"', "'"}:
        return _quoted_yaml_value(value, line_number)
    return re.split(r"\s+#", value, maxsplit=1)[0].rstrip()


def _parse_simple_yaml_list(text: str) -> list[str]:
    """Parse the supported dependency-free YAML subset."""
    return [_yaml_item(line_number, line) for line_number, line in _yaml_rows(text)]


def _validate_name_list(value: object, path: Path) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{path}: expected a top-level list")
    if any(not isinstance(item, str) for item in value):
        raise ValueError(f"{path}: every list item must be a string")
    return value


def _load_yaml(text: str):
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        return _parse_simple_yaml_list(text)
    return yaml.safe_load(text)


def load_name_list(path: str | Path) -> list[str]:
    """Load a top-level string list from JSON, YAML, or YML."""
    file_path = Path(path)
    text, suffix = file_path.read_text(encoding="utf-8-sig"), file_path.suffix.lower()
    if suffix == ".json":
        return _validate_name_list(json.loads(text), file_path)
    if suffix not in {".yaml", ".yml"}:
        raise ValueError(f"{file_path}: supported extensions are .json, .yaml, and .yml")
    return _validate_name_list(_load_yaml(text), file_path)


def build_report(source_path: str | Path, target_path: str | Path, *, minimum_score: int = DEFAULT_MINIMUM_SCORE):
    sources, targets = load_name_list(source_path), load_name_list(target_path)
    report = {"source_file": str(Path(source_path).resolve()), "target_file": str(Path(target_path).resolve())}
    report.update({"minimum_score": minimum_score, "source_count": len(sources), "target_count": len(targets)})
    report.update(fit_loudly(sources, targets, minimum_score=minimum_score))
    return report


def _add_path_arguments(parser: argparse.ArgumentParser, project_dir: Path):
    parser.add_argument("source", nargs="?", default=project_dir / "source_names.yaml", help="Source .json, .yaml, or .yml name list")
    parser.add_argument("target", nargs="?", default=project_dir / "target_names.json", help="Target .json, .yaml, or .yml name list")


def _add_option_arguments(parser: argparse.ArgumentParser):
    parser.add_argument("--minimum-score", type=int, default=DEFAULT_MINIMUM_SCORE, metavar="0-100", help=f"Lowest accepted score (default: {DEFAULT_MINIMUM_SCORE})")
    parser.add_argument("--output", type=Path, help="Write the JSON report to this file")


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    _add_path_arguments(parser, Path(__file__).resolve().parent)
    _add_option_arguments(parser)
    return parser


def _report_from_args(args):
    try:
        return build_report(args.source, args.target, minimum_score=args.minimum_score)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"headless-fitter: {exc}") from exc


def _emit_report(report, output: Path | None):
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    if output:
        output.write_text(f"{rendered}\n", encoding="utf-8")
    else:
        print(rendered)


def main(argv: Iterable[str] | None = None) -> int:
    args = _argument_parser().parse_args(argv)
    _emit_report(_report_from_args(args), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
