#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "jinja2",
# ]
# ///

import argparse
import os
import pathlib
import platform
import shutil
import sys
import tarfile
import tempfile
import urllib.request

from jinja2 import Environment, FileSystemLoader

def make_argparser():
    parser = argparse.ArgumentParser(description=("generate a uenv disk benchmark."))
    parser.add_argument("-n", "--nodes", required=True, type=int)
    parser.add_argument("-j", "--jobname", required=True, type=str)
    parser.add_argument("-d", "--dir", required=True, type=str)
    parser.add_argument("-p", "--partition", required=False, type=str)
    parser.add_argument("-r", "--ranks-per-node", required=True, type=int)
    parser.add_argument("-s", "--slurm", required=False, type=str)
    parser.add_argument("-u", "--uenv", required=True, type=str)
    parser.add_argument("-t", "--test", required=False, type=str, choices=("ldd", "mksquashfs", "sha256", "mpiinit"), default="ldd")

    return parser


# examples:
#   gettool("sharkdp", "fd",        "v10.2.0", "./path")
#   gettool("sharkdp", "hyperfine", "v1.19.0", "./path")
def gettool(repo, tool, version, path):
    # Determine the system architecture
    arch = platform.machine()
    if arch == "x86_64":
        arch_str = "x86_64"
    elif arch in ("aarch64", "arm64"):
        arch_str = "aarch64"
    else:
        raise RuntimeError(f"Unsupported architecture: {arch}")

    # Construct download URL for fd release (adjust version as needed)
    filename=f"{tool}-{version}-{arch_str}-unknown-linux-gnu.tar.gz"
    url = f"https://github.com/{repo}/{tool}/releases/download/{version}/{filename}"

    # Download and extract fd binary
    with tempfile.TemporaryDirectory() as tmpdir:
        archive_path = os.path.join(tmpdir, filename)
        urllib.request.urlretrieve(url, archive_path)

        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(path=tmpdir, filter="tar")

        # Find the binary
        for root, _, files in os.walk(tmpdir):
            if tool in files:
                src_path = os.path.join(root, tool)
                break
        else:
            raise FileNotFoundError("fd binary not found in archive")

        # Ensure the output directory exists
        os.makedirs(path, exist_ok=True)

        # Copy to destination path
        dest_path = os.path.join(path, tool)
        shutil.copy2(src_path, dest_path)
        os.chmod(dest_path, 0o755)
        print(f"{tool} installed at {dest_path}")

def generate(args):
    path = os.path.realpath(args.dir)
    jobname = args.jobname
    scriptname = f"{jobname}.script"
    output = f"{jobname}.out"
    nodes = args.nodes
    rankspernode = args.ranks_per_node
    ranks = nodes*rankspernode
    config = {
            "path": path,
            "output": output,
            "jobname": jobname,
            "scriptname": scriptname,
            "ranks": ranks,
            "nodes": nodes,
            "uenv": args.uenv,
            "partition": args.partition,
            "test": args.test,
    }

    os.makedirs(path, exist_ok=True)

    environment = Environment(loader=FileSystemLoader("templates/"))

    template = environment.get_template("sbatch")
    jobpath = os.path.join(path,jobname)
    with open(jobpath, mode="w", encoding="utf-8") as fid:
        fid.write(template.render(config=config))
    os.chmod(jobpath, 0o755)
    print(f"wrote {jobpath}")

    template = environment.get_template("script")
    scriptpath = os.path.join(path,scriptname)
    with open(scriptpath, mode="w", encoding="utf-8") as fid:
        fid.write(template.render(config=config))
    os.chmod(scriptpath, 0o755)
    print(f"wrote {scriptpath}")

    try:
        outputpath=os.path.join(path,output)
        os.remove(outputpath)
        print(f"delete {outputpath}")
    except FileNotFoundError:
        pass

    # download tools
    exepath = os.path.join(path, "hyperfine")
    if not os.path.exists(exepath):
        gettool("sharkdp", "hyperfine", "v1.19.0", path)
    exepath = os.path.join(path, "fd")
    if not os.path.exists(exepath):
        gettool("sharkdp", "fd", "v10.2.0", path)

if __name__ == "__main__":
    parser = make_argparser()
    args = parser.parse_args()

    generate(args)

