#!/usr/bin/env python3
"""
LangtraceSampler File Generator

This script generates multiple Python files containing the LangtraceSampler class
with proper formatting, error handling, and logging.
Files are created in a timestamped directory for better organization.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Template content for the LangtraceSampler class
LANGTRACE_SAMPLER_TEMPLATE = '''from typing import Optional, Sequence
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
'''


class LangtraceFileGenerator:
    """Generator for creating multiple LangtraceSampler files in timestamped directories."""
    
    def __init__(self, base_output_dir: str = "langtrace_files", use_timestamp: bool = True):
        """Initialize the generator.
        
        Args:
            base_output_dir: Base directory where timestamped folders will be created
            use_timestamp: Whether to create a timestamped subdirectory (default: True)
        """
        self.base_output_dir = Path(base_output_dir)
        self.use_timestamp = use_timestamp
        self.created_files: List[Path] = []
        
        # Create timestamped directory if enabled
        if use_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_dir = self.base_output_dir / f"langtrace_{timestamp}"
        else:
            self.output_dir = self.base_output_dir
    
    def create_output_directory(self) -> None:
        """Create the output directory structure if it doesn't exist."""
        try:
            # Create both base and timestamped directories
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            if self.use_timestamp:
                logger.info(f"Created timestamped directory: {self.output_dir}")
            else:
                logger.info(f"Output directory created/verified: {self.output_dir}")
                
        except OSError as e:
            logger.error(f"Failed to create output directory: {e}")
            raise
    
    def generate_file(self, filename: str, add_init: bool = False) -> Path:
        """Generate a single LangtraceSampler file.
        
        Args:
            filename: Name of the file to create (without .py extension)
            add_init: Whether to add __init__.py content
            
        Returns:
            Path to the created file
        """
        if not filename.endswith('.py'):
            filename += '.py'
        
        file_path = self.output_dir / filename
        
        try:
            content = LANGTRACE_SAMPLER_TEMPLATE
            
            # Add __init__.py specific content if requested
            if add_init and filename == '__init__.py':
                init_content = '''"""
Langtrace Sampler Module

This module provides the LangtraceSampler class for OpenTelemetry tracing.
"""

from .langtrace_sampler import LangtraceSampler

__all__ = ['LangtraceSampler']
__version__ = '1.0.0'
'''
                content = init_content + content
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.created_files.append(file_path)
            logger.info(f"Generated file: {file_path}")
            return file_path
            
        except IOError as e:
            logger.error(f"Failed to create file {file_path}: {e}")
            raise
    
    def generate_multiple_files(
        self, 
        filenames: Optional[List[str]] = None,
        count: Optional[int] = None,
        create_init: bool = True,
        base_filename: str = "langtrace_sampler"
    ) -> List[Path]:
        """Generate multiple LangtraceSampler files.
        
        Args:
            filenames: List of specific filenames to create (optional)
            count: Number of files to create with auto-generated names (optional)
            create_init: Whether to create an __init__.py file
            base_filename: Base name for auto-generated files when using count
            
        Returns:
            List of paths to created files
            
        Raises:
            ValueError: If neither filenames nor count is provided, or both are provided
        """
        if filenames is None and count is None:
            raise ValueError("Either 'filenames' or 'count' must be provided")
        
        if filenames is not None and count is not None:
            raise ValueError("Cannot specify both 'filenames' and 'count'. Choose one.")
        
        self.create_output_directory()
        
        # Create __init__.py if requested
        if create_init:
            self.generate_file('__init__.py', add_init=True)
        
        # Generate files based on count or filenames
        if count is not None:
            self._generate_files_by_count(count, base_filename)
        else:
            self._generate_files_by_names(filenames)
        
        return self.created_files
    
    def _generate_files_by_count(self, count: int, base_filename: str) -> None:
        """Generate files based on count with auto-generated names.
        
        Args:
            count: Number of files to create
            base_filename: Base name for the files
        """
        if count <= 0:
            raise ValueError("Count must be a positive integer")
        
        logger.info(f"Generating {count} files with base name '{base_filename}'")
        
        for i in range(1, count + 1):
            if count == 1:
                filename = base_filename
            else:
                # Zero-pad for better sorting (e.g., 001, 002, ..., 010)
                padding = len(str(count))
                filename = f"{base_filename}_{str(i).zfill(padding)}"
            
            self.generate_file(filename)
    
    def _generate_files_by_names(self, filenames: List[str]) -> None:
        """Generate files based on provided filenames.
        
        Args:
            filenames: List of filenames to create
        """
        logger.info(f"Generating {len(filenames)} files with custom names")
        
        for filename in filenames:
            self.generate_file(filename)
    
    def cleanup(self) -> None:
        """Remove all created files (useful for testing)."""
        for file_path in self.created_files:
            try:
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"Removed file: {file_path}")
            except OSError as e:
                logger.error(f"Failed to remove file {file_path}: {e}")
        
        # Remove directory if empty
        try:
            if self.output_dir.exists() and not any(self.output_dir.iterdir()):
                self.output_dir.rmdir()
                logger.info(f"Removed empty directory: {self.output_dir}")
                
                # If base directory is also empty and different from output_dir, remove it too
                if (self.use_timestamp and 
                    self.base_output_dir.exists() and 
                    not any(self.base_output_dir.iterdir())):
                    self.base_output_dir.rmdir()
                    logger.info(f"Removed empty base directory: {self.base_output_dir}")
        except OSError as e:
            logger.error(f"Failed to remove directory: {e}")
        
        self.created_files.clear()
    
    def get_output_dir(self) -> Path:
        """Get the current output directory path.
        
        Returns:
            Path object for the output directory
        """
        return self.output_dir


def main():
    """Main function to demonstrate usage."""
    import argparse
    
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description="Generate multiple LangtraceSampler Python files"
    )
    parser.add_argument(
        "--count", "-c",
        type=int,
        help="Number of files to generate (e.g., --count 10)"
    )
    parser.add_argument(
        "--filenames", "-f",
        nargs="+",
        help="Specific filenames to create (e.g., --filenames sampler1 sampler2)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="langtrace_samplers",
        help="Base output directory (default: langtrace_samplers)"
    )
    parser.add_argument(
        "--base-name", "-b",
        default="langtrace_sampler",
        help="Base filename when using --count (default: langtrace_sampler)"
    )
    parser.add_argument(
        "--no-init",
        action="store_true",
        help="Don't create __init__.py file"
    )
    parser.add_argument(
        "--no-timestamp",
        action="store_true",
        help="Don't create timestamped directory"
    )
    
    args = parser.parse_args()
    
    # Default behavior if no arguments provided
    if not args.count and not args.filenames:
        logger.info("No count or filenames specified. Generating 5 files by default.")
        args.count = 5
    
    # Create generator instance
    generator = LangtraceFileGenerator(
        base_output_dir=args.output_dir,
        use_timestamp=not args.no_timestamp
    )
    
    try:
        # Generate files
        logger.info("Starting file generation...")
        
        if args.count:
            created_files = generator.generate_multiple_files(
                count=args.count,
                create_init=not args.no_init,
                base_filename=args.base_name
            )
        else:
            created_files = generator.generate_multiple_files(
                filenames=args.filenames,
                create_init=not args.no_init
            )
        
        # Summary
        logger.info(f"Successfully generated {len(created_files)} files:")
        for file_path in created_files:
            logger.info(f"  - {file_path}")
        
        logger.info(f"All files created in directory: {generator.output_dir}")
        
    except Exception as e:
        logger.error(f"File generation failed: {e}")
        raise


def generate_files_programmatically():
    """Example function showing programmatic usage with different scenarios."""
    
    # Example 1: Generate 10 files in timestamped directory
    print("Example 1: Generating 10 files in timestamped directory")
    generator1 = LangtraceFileGenerator("example_10_files")
    files1 = generator1.generate_multiple_files(count=10)
    print(f"Created {len(files1)} files in {generator1.output_dir}")


if __name__ == "__main__":
    main()