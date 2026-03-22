#!/usr/bin/env python3
"""Monitor GitHub Actions CI runs until success."""
import subprocess
import json
import time
import sys

def get_latest_run_id():
    """Get latest Code Quality run ID."""
    try:
        result = subprocess.run(
            ['gh', 'run', 'list', '--workflow=Code Quality', '--limit=1', '--json', 'databaseId'],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        if data:
            return data[0]['databaseId']
        return None
    except Exception as e:
        print(f"Error getting run ID: {e}")
        return None

def get_run_status(run_id):
    """Get status of a specific run."""
    try:
        result = subprocess.run(
            ['gh', 'run', 'view', str(run_id), '--json', 'status', 'conclusion'],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        return data.get('status'), data.get('conclusion')
    except Exception as e:
        print(f"Error getting run status: {e}")
        return None, None

def get_job_errors(run_id):
    """Get error logs from failed jobs."""
    try:
        result = subprocess.run(
            ['gh', 'run', 'view', str(run_id), '--log'],
            capture_output=True,
            text=True,
            check=True
        )
        logs = result.stdout

        # Extract error lines
        errors = []
        for line in logs.split('\n'):
            if 'Error:' in line or 'Traceback' in line or 'X' in line:
                if 'Checkout code' not in line and 'Set up Python' not in line:
                    errors.append(line)

        return errors[:20]  # Return first 20 errors
    except Exception as e:
        print(f"Error getting job logs: {e}")
        return []

def monitor_run(run_id, max_wait=1800):
    """Monitor a run until it completes or times out."""
    print(f"\n{'='*60}")
    print(f"Monitoring Run ID: {run_id}")
    print(f"{'='*60}\n")

    start_time = time.time()
    check_interval = 30  # Check every 30 seconds

    while True:
        elapsed = time.time() - start_time
        if elapsed > max_wait:
            print(f"\nTimeout after {max_wait} seconds")
            return False

        status, conclusion = get_run_status(run_id)

        if status is None:
            print(f"Unable to get status, retrying...")
            time.sleep(check_interval)
            continue

        if status == 'queued':
            print(f"[QUEUED] ({int(elapsed)}s elapsed)")
        elif status == 'in_progress':
            print(f"[IN PROGRESS] ({int(elapsed)}s elapsed)")
        elif status == 'completed':
            print(f"\nRun completed! Status: {status}, Conclusion: {conclusion}")

            if conclusion == 'success':
                print("\n*** All CI checks passed! ***")
                return True
            else:
                print(f"\nRun failed with conclusion: {conclusion}")
                errors = get_job_errors(run_id)
                if errors:
                    print("\nErrors found:")
                    for i, error in enumerate(errors, 1):
                        print(f"{i}. {error}")
                return False

        time.sleep(check_interval)

if __name__ == "__main__":
    print("GitHub Actions CI Monitor")
    print("="*60)

    # Get latest run ID
    run_id = get_latest_run_id()

    if not run_id:
        print("Could not find any Code Quality runs")
        sys.exit(1)

    # Check if run is already completed
    status, conclusion = get_run_status(run_id)
    if status == 'completed':
        print(f"\nLatest run ({run_id}) already completed")
        print(f"Status: {status}, Conclusion: {conclusion}")
        if conclusion == 'success':
            print("\nAll checks passed!")
            sys.exit(0)
        else:
            print("\nRun failed")
            errors = get_job_errors(run_id)
            if errors:
                print("\nErrors found:")
                for i, error in enumerate(errors, 1):
                    print(f"{i}. {error}")
            sys.exit(1)

    # Monitor the run
    success = monitor_run(run_id)

    sys.exit(0 if success else 1)
