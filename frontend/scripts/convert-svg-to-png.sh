#!/bin/bash

# SVG to PNG Conversion Script for NetWiz Frontend
# This script converts SVG files to PNG format for favicon and other uses

set -e

FRONTEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PUBLIC_DIR="$FRONTEND_DIR/public"

echo "🔄 Converting SVG files to PNG..."

# Check if we have the required tools
if ! command -v rsvg-convert &> /dev/null; then
    echo "❌ rsvg-convert not found. Installing librsvg2-bin..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y librsvg2-bin
    elif command -v brew &> /dev/null; then
        brew install librsvg
    else
        echo "❌ Cannot install rsvg-convert. Please install librsvg2-bin manually."
        exit 1
    fi
fi

# Convert logo.svg to various favicon sizes
if [ -f "$PUBLIC_DIR/logo.svg" ]; then
    echo "📱 Converting logo.svg to favicon sizes..."

    # Create favicon.ico (16x16, 32x32, 48x48)
    rsvg-convert -w 16 -h 16 "$PUBLIC_DIR/logo.svg" -o "$PUBLIC_DIR/favicon-16x16.png"
    rsvg-convert -w 32 -h 32 "$PUBLIC_DIR/logo.svg" -o "$PUBLIC_DIR/favicon-32x32.png"
    rsvg-convert -w 48 -h 48 "$PUBLIC_DIR/logo.svg" -o "$PUBLIC_DIR/favicon-48x48.png"

    # Create apple-touch-icon
    rsvg-convert -w 180 -h 180 "$PUBLIC_DIR/logo.svg" -o "$PUBLIC_DIR/apple-touch-icon.png"

    # Create android-chrome icons
    rsvg-convert -w 192 -h 192 "$PUBLIC_DIR/logo.svg" -o "$PUBLIC_DIR/android-chrome-192x192.png"
    rsvg-convert -w 512 -h 512 "$PUBLIC_DIR/logo.svg" -o "$PUBLIC_DIR/android-chrome-512x512.png"

    echo "✅ Favicon files created successfully!"
else
    echo "❌ logo.svg not found in $PUBLIC_DIR"
    exit 1
fi

# Convert logo-full.svg to PNG for use in components
if [ -f "$PUBLIC_DIR/logo-full.svg" ]; then
    echo "🖼️  Converting logo-full.svg to PNG..."

    # Create different sizes for various uses
    rsvg-convert -w 200 -h 60 "$PUBLIC_DIR/logo-full.svg" -o "$PUBLIC_DIR/logo-full-200x60.png"
    rsvg-convert -w 300 -h 90 "$PUBLIC_DIR/logo-full.svg" -o "$PUBLIC_DIR/logo-full-300x90.png"
    rsvg-convert -w 400 -h 120 "$PUBLIC_DIR/logo-full.svg" -o "$PUBLIC_DIR/logo-full-400x120.png"

    echo "✅ Logo PNG files created successfully!"
else
    echo "❌ logo-full.svg not found in $PUBLIC_DIR"
    exit 1
fi

echo "🎉 All conversions completed successfully!"
echo ""
echo "📁 Generated files:"
echo "  - favicon-16x16.png"
echo "  - favicon-32x32.png"
echo "  - favicon-48x48.png"
echo "  - apple-touch-icon.png"
echo "  - android-chrome-192x192.png"
echo "  - android-chrome-512x512.png"
echo "  - logo-full-200x60.png"
echo "  - logo-full-300x90.png"
echo "  - logo-full-400x120.png"
