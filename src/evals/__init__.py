"""
Evaluation Framework for Product Recommendation Agent

This module provides tools to measure:
- Search relevance and accuracy
- Recommendation quality
- Response authenticity
- Agent performance metrics
"""

from .metrics import (
    SearchMetrics,
    RecommendationMetrics,
    ResponseQualityMetrics,
    AgentPerformanceMetrics
)

from .evaluators import (
    SearchEvaluator,
    RecommendationEvaluator,
    ResponseEvaluator,
    EndToEndEvaluator
)

__all__ = [
    'SearchMetrics',
    'RecommendationMetrics',
    'ResponseQualityMetrics',
    'AgentPerformanceMetrics',
    'SearchEvaluator',
    'RecommendationEvaluator',
    'ResponseEvaluator',
    'EndToEndEvaluator'
]
