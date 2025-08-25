

# fix-camoufox-bin.sh

#!/bin/bash
set -e

echo "Fixing camoufox-bin for NixOS..."

# Check if camoufox-bin exists
CAMOUFOX_BIN="$HOME/.cache/camoufox/camoufox-bin"
if [ ! -f "$CAMOUFOX_BIN" ]; then
    echo "Error: $CAMOUFOX_BIN not found."
    echo "You may need to run 'python -m camoufox fetch' first."
    exit 1
fi

# Make it executable
chmod +x "$CAMOUFOX_BIN"

# Get the NixOS dynamic linker path
DYNAMIC_LINKER=$(cat $NIX_CC/nix-support/dynamic-linker)
if [ -z "$DYNAMIC_LINKER" ]; then
    echo "Error: Could not find NixOS dynamic linker."
    exit 1
fi

echo "Found NixOS dynamic linker: $DYNAMIC_LINKER"

# Patch the binary to use the NixOS dynamic linker
echo "Patching binary with patchelf..."
patchelf --set-interpreter "$DYNAMIC_LINKER" "$CAMOUFOX_BIN"

# Print needed libraries to help diagnose any remaining issues
echo "Libraries needed by camoufox-bin:"
patchelf --print-needed "$CAMOUFOX_BIN"

echo "Patch completed successfully!"
echo "If you still encounter issues, you may need to add missing libraries to LD_LIBRARY_PATH."
