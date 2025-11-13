#!/usr/bin/env bash
# ==============================================================================
# Copyright (C) 2025 Intel Corporation
#
# SPDX-License-Identifier: MIT
# ==============================================================================
set -euo pipefail

PATCH_FILE="$(dirname "$0")/gstreamer-1-26-6-vacompositor-vafilter-fixes.patch"

if [ ! -f "$PATCH_FILE" ]; then
  echo "Patch file not found: $PATCH_FILE" >&2
  exit 2
fi

echo "Applying GStreamer VA patches (idempotent)..."
# Run patch; capture exit but do not exit immediately on non-zero
set +e
patch --forward --batch -p1 < "$PATCH_FILE"
rc=$?
set -e

case $rc in
  0)
    echo "GStreamer patch applied successfully." ;;
  1)
    echo "GStreamer patch already applied (hunks skipped)." ;;
  *)
    echo "GStreamer patch failed rc=$rc" >&2
    exit $rc ;;
esac

exit 0
