#!/usr/bin/env bash

set -e

build_path=""
system=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --path)
            build_path="$2"
            shift 2
            ;;
        --system)
            system="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 1
            ;;
    esac
done

if [[ -z "$build_path" || -z "$system" ]]; then
    echo "Error: both --path and --system must be provided." >&2
    echo "Usage: $0 --path <build_path> --system <system>" >&2
    exit 1
fi

echo
echo "======= build_path $build_path"
echo "======= system     $system"
echo

[[ -e "$build_path" ]] && { echo "Error: '$build_path' exists." >&2; exit 1; }

export PATH=$PWD/stackinator/bin:$PATH

stack-config -r ./recipe -b "$build_path" -s "./alps-cluster-config/$system"

echo
echo "======= done"
echo
