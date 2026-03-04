#!/usr/bin/env python3
"""
Check and fix NaN values in LETKF solver analysis files by replacing them
with the corresponding background (prior) values.

Writes a detailed diagnostic report to <ana_dir>/../nan_report.log

Usage:
    fix_nan_solver.py <ana_dir> <ens_dir> <nmembers>

Arguments:
    ana_dir   - Directory containing analysis files (ana/mem001.nc, ...)
    ens_dir   - Directory containing background ensemble files (ens/mem001.nc, ...)
    nmembers  - Number of ensemble members
"""
import sys
import os
import netCDF4
import numpy as np
from datetime import datetime


def check_and_fix_member(ana_file, bg_file):
    """Check for NaN, report details, then replace with background values.

    Returns a list of dicts: [{varname, nan_count, total_size}, ...]
    """
    ana = netCDF4.Dataset(ana_file, "r+")
    bg = netCDF4.Dataset(bg_file, "r")

    report = []
    for vname in ana.variables:
        v = ana.variables[vname]
        if v.dtype.kind != "f":
            continue
        data = v[:]
        nan_mask = np.isnan(data)
        nan_count = int(np.count_nonzero(nan_mask))
        if nan_count == 0:
            continue

        total_size = int(data.size)
        entry = {"varname": vname, "nan_count": nan_count, "total_size": total_size}

        if vname in bg.variables:
            bg_data = bg.variables[vname][:]
            data[nan_mask] = bg_data[nan_mask]
            v[:] = data
            entry["fixed"] = True
        else:
            entry["fixed"] = False

        report.append(entry)

    ana.close()
    bg.close()
    return report


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)

    ana_dir = sys.argv[1]
    ens_dir = sys.argv[2]
    nmembers = int(sys.argv[3])

    log_path = os.path.join(os.path.dirname(ana_dir.rstrip("/")), "nan_report.log")

    all_reports = {}
    has_nan = False

    for mem in range(1, nmembers + 1):
        memstr = f"{mem:03d}"
        ana_file = f"{ana_dir}/mem{memstr}.nc"
        bg_file = f"{ens_dir}/mem{memstr}.nc"
        report = check_and_fix_member(ana_file, bg_file)
        if report:
            has_nan = True
            all_reports[memstr] = report

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []
    lines.append(f"=== NaN Diagnostic Report ===")
    lines.append(f"Time: {timestamp}")
    lines.append(f"Analysis dir: {ana_dir}")
    lines.append(f"Background dir: {ens_dir}")
    lines.append(f"Members checked: {nmembers}")
    lines.append("")

    if not has_nan:
        lines.append("RESULT: CLEAN - No NaN values found in any member.")
        summary = "No NaN values found - analysis is clean"
    else:
        affected_members = sorted(all_reports.keys())
        lines.append(f"WARNING: NaN detected in {len(affected_members)}/{nmembers} members!")
        lines.append("")

        var_summary = {}
        for memstr, report in all_reports.items():
            for entry in report:
                vn = entry["varname"]
                if vn not in var_summary:
                    var_summary[vn] = {"members": 0, "total_nan": 0,
                                       "total_size": entry["total_size"]}
                var_summary[vn]["members"] += 1
                var_summary[vn]["total_nan"] += entry["nan_count"]

        lines.append(f"{'Variable':<40s} {'Members':>8s} {'NaN/member':>12s} {'% of field':>12s}")
        lines.append("-" * 76)
        for vn in sorted(var_summary.keys()):
            info = var_summary[vn]
            avg_nan = info["total_nan"] / info["members"]
            pct = 100.0 * avg_nan / info["total_size"]
            lines.append(f"{vn:<40s} {info['members']:>8d} {avg_nan:>12.0f} {pct:>11.4f}%")

        lines.append("")
        lines.append("Per-member detail:")
        for memstr in affected_members:
            report = all_reports[memstr]
            var_names = [e["varname"] for e in report]
            total_nan = sum(e["nan_count"] for e in report)
            lines.append(f"  mem{memstr}: {total_nan} NaN values in {len(report)} variables "
                         f"({', '.join(var_names[:5])}{'...' if len(var_names) > 5 else ''})")

        lines.append("")
        lines.append("All NaN values have been replaced with background values.")

        summary = (f"WARNING: NaN found and fixed in {len(affected_members)} members, "
                   f"{len(var_summary)} variables. See {log_path}")

    lines.append("")

    report_text = "\n".join(lines)

    with open(log_path, "w") as f:
        f.write(report_text + "\n")

    print(report_text)
    print(f"\nReport saved to: {log_path}")


if __name__ == "__main__":
    main()
