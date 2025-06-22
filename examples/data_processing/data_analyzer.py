#!/usr/bin/env python3
"""Data Analysis Example for DIGY.

This script demonstrates how to perform basic data analysis using pandas.
It reads a CSV file, performs some analysis, and saves the results.
"""

import os
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

# Use non-interactive backend for matplotlib to avoid display issues
matplotlib.use('Agg')


def analyze_data(input_file: str, output_dir: str = 'output') -> None:
    """
    Analyze data from a CSV file and generate a report.

    Args:
        input_file: Path to the input CSV file
        output_dir: Directory to save output files
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True, parents=True)

    # Read the data
    print(f"📊 Loading data from {input_file}")
    try:
        df = pd.read_csv(input_file)
        print(f"✅ Loaded {len(df)} rows")
        print(f"📊 Columns: {', '.join(df.columns)}")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None

    # Basic analysis
    print("\n📈 Basic Statistics:")
    stats = df.describe()
    print(stats)

    # Save basic statistics to a file
    stats_file = os.path.join(output_dir, 'statistics.txt')
    with open(stats_file, 'w', encoding='utf-8') as f:
        f.write("Data Statistics\n" + "="*50 + "\n")
        f.write(stats.to_string())

    # Generate plots for numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns

    if len(numeric_cols) > 0:
        print("\n📊 Generating plots for numeric columns...")
        for col in numeric_cols:
            try:
                plt.figure(figsize=(10, 6))
                df[col].plot(kind='hist', bins=20, 
                           title=f'{col} Distribution')
                plot_file = os.path.join(output_dir, 
                                      f'{col}_distribution.png')
                plt.savefig(plot_file)
                plt.close()
                print(f"✅ Saved {col} distribution plot to {plot_file}")
            except Exception as e:
                print(f"⚠️ Could not generate plot for {col}: {e}")

    abs_path = os.path.abspath(output_dir)
    print(f"\n✅ Analysis complete! Results saved to {abs_path}/")
    return df


def main() -> None:
    """Handle command line arguments and run the analysis."""
    import argparse

    parser = argparse.ArgumentParser(description='Analyze CSV data')
    parser.add_argument(
        '--input-file',
        required=True,
        help='Path to input CSV file'
    )
    parser.add_argument(
        '--output-dir',
        default='analysis_output',
        help='Directory to save output files'
    )

    # For DIGY compatibility, also accept arguments after --
    if '--' in sys.argv:
        args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    else:
        args = parser.parse_args()

    return analyze_data(args.input_file, args.output_dir)


def print_usage() -> None:
    """Print usage instructions."""
    usage = """
Usage with DIGY:
    digy local . examples/data_processing/data_analyzer.py --input-file sample_data.csv
    digy local . examples/data_processing/data_analyzer.py --input-file sample_data.csv --output-dir analysis_results
"""
    print(usage)

if __name__ == "__main__":
    if len(sys.argv) == 1 or '--help' in sys.argv or '-h' in sys.argv:
        print_usage()
    else:
        main()
