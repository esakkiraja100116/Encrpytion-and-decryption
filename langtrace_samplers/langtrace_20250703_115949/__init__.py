"""
Langtrace Sampler Module

This module provides the LangtraceSampler class for OpenTelemetry tracing.
"""

from .langtrace_sampler import LangtraceSampler

__all__ = ['LangtraceSampler']
__version__ = '1.0.0'
from typing import Optional, Sequence
from opentelemetry.sdk.trace.sampling import (
    Sampler,
    Decision,
    SamplingResult,
)
from opentelemetry.trace import SpanKind, Link, TraceState, TraceFlags
from opentelemetry.util.types import Attributes
from opentelemetry.context import Context
from opentelemetry import trace


class LangtraceSampler(Sampler):
    """Custom sampler for Langtrace that filters spans based on disabled methods."""
    
    _disabled_methods_names: set
    
    def __init__(
        self,
        disabled_methods: dict,
    ):
        """Initialize the sampler with disabled methods configuration.
        
        Args:
            disabled_methods: Dictionary mapping components to their disabled methods
        """
        self._disabled_methods_names = set()
        if disabled_methods:
            for _, methods in disabled_methods.items():
                for method in methods:
                    self._disabled_methods_names.add(method)
    
    def should_sample(
        self,
        parent_context: Optional[Context],
        trace_id: int,
        name: str,
        kind: Optional[SpanKind] = None,
        attributes: Attributes = None,
        links: Optional[Sequence[Link]] = None,
        trace_state: Optional["TraceState"] = None,
    ) -> SamplingResult:
        """Determine whether a span should be sampled.
        
        Args:
            parent_context: The parent context
            trace_id: The trace ID
            name: The span name
            kind: The span kind
            attributes: The span attributes
            links: The span links
            trace_state: The trace state
            
        Returns:
            SamplingResult indicating whether to sample the span
        """
        parent_span = trace.get_current_span(parent_context)
        parent_span_context = parent_span.get_span_context()
        
        if not self._disabled_methods_names:
            return SamplingResult(decision=Decision.RECORD_AND_SAMPLE)
        
        if parent_context:
            if (
                parent_span_context.span_id != 0
                and parent_span_context.trace_flags != TraceFlags.SAMPLED
            ):
                return SamplingResult(decision=Decision.DROP)
        
        if name in self._disabled_methods_names:
            return SamplingResult(decision=Decision.DROP)
        
        return SamplingResult(decision=Decision.RECORD_AND_SAMPLE)
    
    def get_description(self) -> str:
        """Get a description of this sampler.
        
        Returns:
            A string description of the sampler
        """
        return "Langtrace Sampler"
