#!/usr/bin/env python3
"""
Parse spack uenv build logs and extract per-package timing data.

Produces two dicts (compiler bootstrap and full environment), each mapping
package name to a list of timing records:
  {"pkg": [{"stage": X, "configure": X, "build": X, "install": X, "total": X}]}

Usage:
  python parse_timings.py <logfile> [logfile2 ...]
"""

import re
import sys

CONFIGURE_CATEGORIES = {'bootstrap', 'cmake', 'configure', 'autoreconf', 'edit'}
BUILD_CATEGORIES     = {'build'}
INSTALL_CATEGORIES   = {'install', 'post-install'}


def parse_time(s):
    """Parse a time string like '1h 2m 3.45s', '1m 17.38s', or '36.71s' into seconds."""
    m = re.match(r'(?:(\d+)h\s*)?(?:(\d+)m\s*)?(\d+(?:\.\d+)?)s', s.strip())
    if not m:
        return 0.0
    hours   = float(m.group(1) or 0)
    minutes = float(m.group(2) or 0)
    seconds = float(m.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds


def parse_timing_line(line):
    """Parse a timing line into a dict of {category: seconds}.

    Example: '  Stage: 16.90s.  Cmake: 36.71s.  Build: 20.70s.  Total: 1m 17.38s'
    """
    result = {}
    for m in re.finditer(r'([\w-]+):\s+((?:\d+h\s*)?(?:\d+m\s*)?\d+(?:\.\d+)?s)\.?', line):
        category = m.group(1).lower()
        result[category] = parse_time(m.group(2))
    return result


def aggregate_timings(raw):
    """Roll up raw categories into stage / configure / build / install / total."""
    return {
        'stage':     raw.get('stage', 0.0),
        'configure': sum(v for k, v in raw.items() if k in CONFIGURE_CATEGORIES),
        'build':     sum(v for k, v in raw.items() if k in BUILD_CATEGORIES),
        'install':   sum(v for k, v in raw.items() if k in INSTALL_CATEGORIES),
        'total':     raw.get('total', 0.0),
    }


def parse_wall_times(filepath):
    """Parse the real/user/sys lines from the bash `time` output at end of file.

    Returns a dict {'real': s, 'user': s, 'sys': s} in whole seconds, or None.
    """
    result = {}
    with open(filepath) as f:
        for line in f:
            m = re.match(r'^(real|user|sys)\s+(?:(\d+)m)?(\d+(?:\.\d+)?)s', line)
            if m:
                minutes = int(m.group(2) or 0)
                seconds = float(m.group(3))
                result[m.group(1)] = round(minutes * 60 + seconds)
    return result if len(result) == 3 else None


def parse_log(filepath):
    """Parse a spack build log.

    Returns (compiler_packages, env_packages) where each is a dict mapping
    package name -> list of aggregated timing dicts.
    """
    SECTION_NONE     = 0
    SECTION_COMPILER = 1
    SECTION_ENV      = 2

    compiler_packages = {}
    env_packages      = {}
    section           = SECTION_NONE
    pending_name      = None

    with open(filepath) as f:
        for line in f:
            # --- section boundary detection ---
            if 'make[1]: Entering directory' in line:
                if '/compilers' in line:
                    section = SECTION_COMPILER
                elif '/environments' in line:
                    section = SECTION_ENV
                continue

            if 'make[1]: Leaving directory' in line:
                if '/compilers' in line or '/environments' in line:
                    section = SECTION_NONE
                continue

            # --- package name from "Successfully installed" ---
            m = re.match(r'==>\s+(\S+):\s+Successfully installed\s+\S+', line)
            if m:
                pending_name = m.group(1)
                continue

            # --- timing line (leading whitespace optional) ---
            if re.match(r'\s*Stage:', line):
                if pending_name is None:
                    continue
                entry = aggregate_timings(parse_timing_line(line))
                target = compiler_packages if section == SECTION_COMPILER else env_packages
                target.setdefault(pending_name, []).append(entry)
                pending_name = None

    return compiler_packages, env_packages


COLUMNS = ['stage', 'configure', 'build', 'install', 'total']
COL_W   = 6  # numeric column width (matches %6.1f)


def flatten(packages):
    """Sum multiple entries per package into a single dict."""
    return {name: {col: sum(e[col] for e in entries) for col in COLUMNS}
            for name, entries in packages.items()}


def print_table(title, packages):
    """Single-file detail table: all timing columns."""
    if not packages:
        return

    rows = sorted(flatten(packages).items(), key=lambda r: r[1]['total'], reverse=True)

    name_w = max(max(len(n) for n, _ in rows), len('package'))
    col_w  = max(COL_W, *(len(col) for col in COLUMNS))
    header = f"{'package':<{name_w}}" + "".join(f"  {col:>{col_w}}" for col in COLUMNS)
    sep    = "-" * name_w + "".join("  " + "-" * col_w for col in COLUMNS)
    print(f"\n{title}")
    print(header)
    print(sep)
    for name, d in rows:
        print(f"{name:<{name_w}}" + "".join(f"  {d[col]:{col_w}.1f}" for col in COLUMNS))


def print_comparison_table(title, all_packages, labels):
    """Multi-file comparison table: one total column per file."""
    # Collect the union of all package names
    all_names = dict.fromkeys(name for packages in all_packages for name in packages)
    if not all_names:
        return

    rows = sorted(all_names,
                  key=lambda name: -max(p.get(name, {}).get('total', 0.0)
                                        for p in all_packages))

    name_w = max(max(len(n) for n in rows), len('package'))
    col_w  = max(COL_W, *(len(lab) for lab in labels))

    header = f"{'package':<{name_w}}" + "".join(f"  {lab:>{col_w}}" for lab in labels)
    sep    = "-" * name_w + "".join("  " + "-" * col_w for lab in labels)
    print(f"\n{title}")
    print(header)
    print(sep)
    for name in rows:
        row = f"{name:<{name_w}}"
        for packages in all_packages:
            val = packages.get(name, {}).get('total')
            row += f"  {val:{col_w}.1f}" if val is not None else f"  {'---':>{col_w}}"
        print(row)


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <logfile> [logfile2 ...]", file=sys.stderr)
        sys.exit(1)

    filepaths = sys.argv[1:]

    if len(filepaths) == 1:
        filepath = filepaths[0]
        print(f"\n{'=' * 60}\n{filepath}\n{'=' * 60}")
        compiler, env = parse_log(filepath)
        print_table("compiler", compiler)
        print_table("environment", env)
    else:
        labels = [p.split('/')[-1] for p in filepaths]
        all_compiler  = []
        all_env       = []
        all_wall      = []
        for filepath in filepaths:
            compiler, env = parse_log(filepath)
            all_compiler.append(flatten(compiler))
            all_env.append(flatten(env))
            all_wall.append(parse_wall_times(filepath))
        print_comparison_table("compiler",    all_compiler, labels)
        print_comparison_table("environment", all_env,      labels)

        # wall-time summary table
        time_keys = ['real', 'user', 'sys']
        col_w = max(COL_W, *(len(lab) for lab in labels))
        header = f"{'':10}" + "".join(f"  {lab:>{col_w}}" for lab in labels)
        sep    = "-" * 10  + "".join("  " + "-" * col_w for lab in labels)
        print("\nwall time (seconds)")
        print(header)
        print(sep)
        for key in time_keys:
            row = f"{key:<10}"
            for wt in all_wall:
                val = wt.get(key) if wt else None
                row += f"  {val:{col_w}d}" if val is not None else f"  {'---':>{col_w}}"
            print(row)


if __name__ == '__main__':
    main()
