"""
Run the entire 5-day pipeline end-to-end, in order.

Usage:
    python main.py
"""

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SCRIPTS = [
    "src/day1_generate_and_clean_data.py",
    "src/day2_eda.py",
    "src/day3_visualizations.py",
    "src/day4_customer_rfm_analysis.py",
    "src/day5_dashboard_report.py",
]

if __name__ == "__main__":
    for script in SCRIPTS:
        print(f"\n{'=' * 60}\nRunning {script}\n{'=' * 60}")
        result = subprocess.run([sys.executable, str(BASE_DIR / script)])
        if result.returncode != 0:
            print(f"\nStopped: {script} failed.")
            sys.exit(1)
    print("\nAll 5 stages completed successfully. Check outputs/ for results.")
