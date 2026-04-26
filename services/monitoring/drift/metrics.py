from __future__ import annotations

import math
from typing import Iterable, List, Tuple


def histogram(values: Iterable[float], lower: float, upper: float, bins: int = 10) -> List[float]:
    values_list = list(values)
    width = (upper - lower) / bins
    counts = [0.0 for _ in range(bins)]

    if width <= 0:
        raise ValueError("Upper bound must be larger than lower bound.")

    for value in values_list:
        if value <= lower:
            index = 0
        elif value >= upper:
            index = bins - 1
        else:
            index = min(int((value - lower) / width), bins - 1)
        counts[index] += 1.0

    total = sum(counts) or 1.0
    return [count / total for count in counts]


def psi(reference_distribution: Iterable[float], current_distribution: Iterable[float]) -> float:
    total = 0.0
    for reference_value, current_value in zip(reference_distribution, current_distribution):
        expected = max(reference_value, 1e-6)
        actual = max(current_value, 1e-6)
        total += (actual - expected) * math.log(actual / expected)
    return round(total, 3)


def ks_statistic(reference_values: Iterable[float], current_values: Iterable[float]) -> float:
    left = sorted(reference_values)
    right = sorted(current_values)

    if not left or not right:
        return 0.0

    left_index = 0
    right_index = 0
    max_gap = 0.0
    left_size = float(len(left))
    right_size = float(len(right))

    while left_index < len(left) and right_index < len(right):
        if left[left_index] <= right[right_index]:
            left_index += 1
        else:
            right_index += 1

        gap = abs((left_index / left_size) - (right_index / right_size))
        if gap > max_gap:
            max_gap = gap

    while left_index < len(left):
        left_index += 1
        max_gap = max(max_gap, abs((left_index / left_size) - (right_index / right_size)))

    while right_index < len(right):
        right_index += 1
        max_gap = max(max_gap, abs((left_index / left_size) - (right_index / right_size)))

    return round(max_gap, 3)


def compare_feature(
    reference_values: Iterable[float],
    current_values: Iterable[float],
    lower: float,
    upper: float,
    bins: int = 10,
) -> Tuple[List[float], List[float], float, float]:
    reference_distribution = histogram(reference_values, lower, upper, bins)
    current_distribution = histogram(current_values, lower, upper, bins)
    return (
        reference_distribution,
        current_distribution,
        psi(reference_distribution, current_distribution),
        ks_statistic(reference_values, current_values),
    )
