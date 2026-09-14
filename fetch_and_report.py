#!/usr/bin/env python3
"""
Fetches test result folders from a remote server and generates reports.

Usage:
    python3 fetch_and_report.py performance   # fetch results & generate performance report
    python3 fetch_and_report.py scale         # fetch results & generate scale report
    python3 fetch_and_report.py both          # fetch results & generate both reports
    python3 fetch_and_report.py performance --report-only  # skip SCP, just generate report
"""

import argparse
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(REPO_ROOT, "venv")
VENV_PYTHON = os.path.join(VENV_DIR, "bin", "python")

REMOTE_USER = "ubuntu"
REMOTE_HOST = "107.23.221.35"
REMOTE_HOST_AND_USER = REMOTE_USER + "@" + REMOTE_HOST
SSH_KEY = os.path.expanduser("~/.ssh/dc.pem")
REMOTE_BASE = "/home/ubuntu/repositories/dc-app-performance-toolkit"

PROFILES_DIR = os.path.join(REPO_ROOT, "app", "reports_generation")
PROFILE_MAP = {
    "performance": "performance_profile.yml",
    "scale": "scale_profile.yml",
}


def ensure_venv():
    """Create virtualenv and install requirements if needed."""
    if os.path.isfile(VENV_PYTHON):
        return
    print("[setup] Creating virtualenv...")
    subprocess.run(["virtualenv", VENV_DIR, "-p", "python3"], check=True)
    print("[setup] Installing requirements...")
    subprocess.run(
        [os.path.join(VENV_DIR, "bin", "pip"), "install", "-r",
         os.path.join(REPO_ROOT, "requirements.txt")],
        check=True,
    )


def reexec_in_venv():
    """If not running inside the venv, set it up and re-exec this script in it."""
    if sys.executable == VENV_PYTHON:
        return
    ensure_venv()
    print("[setup] Re-launching inside venv...\n")
    os.execv(VENV_PYTHON, [VENV_PYTHON] + sys.argv)


# --- Re-exec into venv before importing any third-party libs ---
reexec_in_venv()

import yaml  # noqa: E402 — available after venv bootstrap


def parse_relative_paths(profile_path):
    """Extract relativePath values from a profile YAML file."""
    with open(profile_path) as f:
        data = yaml.safe_load(f)

    paths = []
    for run in data.get("runs", []):
        rel = run.get("relativePath", "")
        # Skip placeholder paths that haven't been filled in
        if "{PRODUCT}" in rel or "{TIMESTAMP}" in rel or not rel:
            continue
        paths.append(rel)
    return paths


def scp_folder(relative_path):
    """SCP a result folder from the remote server to the local repo."""
    # relative_path looks like ./app/results/jira/2026-02-11_10-58-47
    clean = relative_path.lstrip("./")  # app/results/jira/2026-02-11_10-58-47
    remote_path = f"{REMOTE_BASE}/{clean}"

    # Local destination is the parent dir, e.g. app/results/jira/
    local_dest = os.path.join(REPO_ROOT, os.path.dirname(clean))
    os.makedirs(local_dest, exist_ok=True)

    local_full = os.path.join(REPO_ROOT, clean)
    if os.path.isdir(local_full):
        print(f"  [skip] Already exists locally: {clean}")
        return

    cmd = [
        "scp", "-r", "-i", SSH_KEY,
        "-o", "StrictHostKeyChecking=no",
        f"{REMOTE_HOST_AND_USER}:{remote_path}",
        local_dest,
    ]
    print(f"  [scp]  {REMOTE_HOST_AND_USER}:{remote_path} -> {local_dest}/")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"  [error] SCP failed for {remote_path}")
        sys.exit(1)


def generate_report(profile_name):
    """Run csv_chart_generator.py for the given profile."""
    profile_file = PROFILE_MAP[profile_name]
    generator = os.path.join(PROFILES_DIR, "csv_chart_generator.py")

    print(f"\n[report] Generating {profile_name} report from {profile_file}...")
    result = subprocess.run(
        [VENV_PYTHON, generator, profile_file],
        cwd=PROFILES_DIR,
    )
    if result.returncode != 0:
        print(f"[error] Report generation failed for {profile_file}")
        sys.exit(1)
    print(f"[done] {profile_name} report generated.")


def process_profile(profile_name, report_only=False):
    """Fetch results and generate report for a single profile."""
    profile_file = PROFILE_MAP[profile_name]
    profile_path = os.path.join(PROFILES_DIR, profile_file)

    print(f"\n{'='*60}")
    print(f"Processing: {profile_file}")
    print(f"{'='*60}")

    paths = parse_relative_paths(profile_path)
    if not paths:
        print(f"[warn] No valid relativePath entries found in {profile_file}.")
        print("       Fill in the paths and re-run.")
        return

    if not report_only:
        print(f"\n[fetch] Fetching {len(paths)} result folder(s)...")
        for p in paths:
            scp_folder(p)
    else:
        print("\n[skip] --report-only: skipping SCP")

    generate_report(profile_name)


def main():
    parser = argparse.ArgumentParser(description="Fetch results and generate DCAPT reports")
    parser.add_argument(
        "profile",
        choices=["performance", "scale", "both"],
        help="Which profile(s) to process",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Skip SCP, only generate report (results must already be local)",
    )
    args = parser.parse_args()

    profiles = ["performance", "scale"] if args.profile == "both" else [args.profile]

    for profile in profiles:
        process_profile(profile, report_only=args.report_only)

    print("\nAll done.")


if __name__ == "__main__":
    main()