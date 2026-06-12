"""
run_pipeline.py — runs everything in one command
Run: python run_pipeline.py
"""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).parent

def run(script, label):
    print(f"\n{'='*48}\n  {label}\n{'='*48}")
    r = subprocess.run([sys.executable, script], cwd=ROOT)
    if r.returncode != 0:
        print(f"ERROR in {script}"); sys.exit(1)

if __name__ == "__main__":
    print("\n🚀 Retail Analytics — Full Pipeline\n")
    run("etl/etl_pipeline.py",      "Stage 1: ETL Pipeline")
    run("sql/analytics_queries.py", "Stage 2: SQL Analytics")
    run("analysis/rfm_analysis.py", "Stage 3: RFM Segmentation")
    print("\n✅ Pipeline complete! Launching dashboard...\n")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard/app.py"], cwd=ROOT)
