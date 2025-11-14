"""
Quick diagnostic script to find recent errors
"""
from pathlib import Path
import datetime

print("=" * 70)
print("HAVEN DIAGNOSTICS - Error Investigation")
print("=" * 70)

# Check for recent errors in logs
log_dir = Path("logs")
now = datetime.datetime.now()
cutoff = now - datetime.timedelta(minutes=30)

print("\n[1] Checking recent log files (last 30 minutes)...")
recent_logs = []
for log_file in log_dir.rglob("*.log"):
    mtime = datetime.datetime.fromtimestamp(log_file.stat().st_mtime)
    if mtime > cutoff:
        size = log_file.stat().st_size
        recent_logs.append((log_file, mtime, size))

recent_logs.sort(key=lambda x: x[1], reverse=True)

if not recent_logs:
    print("  No recent log files found.")
else:
    for log_file, mtime, size in recent_logs[:10]:
        print(f"  {log_file.name:<40} {mtime.strftime('%H:%M:%S')}  {size:>8} bytes")

# Check for ERROR or Exception in recent logs
print("\n[2] Searching for errors in recent logs...")
error_count = 0
for log_file, mtime, size in recent_logs:
    if size > 0 and size < 1_000_000:  # Skip huge logs
        try:
            content = log_file.read_text(encoding='utf-8', errors='ignore')
            if 'ERROR' in content or 'Exception' in content or 'Traceback' in content:
                print(f"\n  Found errors in: {log_file.name}")
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'ERROR' in line or 'Exception' in line or 'Traceback' in line:
                        # Show context
                        start = max(0, i-2)
                        end = min(len(lines), i+5)
                        print(f"    Lines {start+1}-{end}:")
                        for j in range(start, end):
                            if j < len(lines):
                                print(f"      {lines[j]}")
                        error_count += 1
                        if error_count >= 3:
                            break
        except Exception as e:
            print(f"  Could not read {log_file.name}: {e}")
    if error_count >= 3:
        break

if error_count == 0:
    print("  No errors found in recent logs.")

# Check data.json for issues
print("\n[3] Checking data.json integrity...")
data_file = Path("data/data.json")
if data_file.exists():
    try:
        import json
        data = json.loads(data_file.read_text(encoding='utf-8'))
        print(f"  ✓ data.json is valid JSON")
        print(f"  ✓ Contains {len(data)-1} systems (excluding _meta)")

        # Check for moons
        moon_count = 0
        for key, system in data.items():
            if key != "_meta" and isinstance(system, dict):
                planets = system.get("planets", [])
                for planet in planets:
                    if isinstance(planet, dict):
                        moons = planet.get("moons", [])
                        moon_count += len(moons)
        print(f"  ✓ Found {moon_count} total moons in dataset")
    except json.JSONDecodeError as e:
        print(f"  ✗ data.json has JSON errors: {e}")
    except Exception as e:
        print(f"  ✗ Error reading data.json: {e}")
else:
    print("  ✗ data.json not found!")

# Check if wizard/control room are running
print("\n[4] Checking for running processes...")
import psutil
python_processes = []
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        if proc.info['name'] and 'python' in proc.info['name'].lower():
            cmdline = proc.info['cmdline'] or []
            cmdline_str = ' '.join(cmdline)
            if 'system_entry_wizard' in cmdline_str or 'control_room' in cmdline_str:
                python_processes.append((proc.info['pid'], cmdline_str))
    except:
        pass

if python_processes:
    print(f"  Found {len(python_processes)} Haven processes:")
    for pid, cmd in python_processes:
        print(f"    PID {pid}: {cmd[:80]}")
else:
    print("  No Haven processes currently running.")

print("\n" + "=" * 70)
print("DIAGNOSIS COMPLETE")
print("=" * 70)
print("\nIf you're seeing errors, please share:")
print("1. The error message you see")
print("2. What you were trying to do when the error occurred")
print("3. Any output from the [2] section above")
