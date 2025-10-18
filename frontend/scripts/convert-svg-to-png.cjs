#!/usr/bin/env node

/**
 * SVG to PNG Conversion Script for NetWiz Frontend
 *
 * This script converts SVG files to PNG format for favicon and other uses.
 * Uses Sharp library for high-quality image conversion.
 */

const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

const PUBLIC_DIR = path.join(__dirname, '..', 'public');

async function convertSvgToPng() {
  console.log('🔄 Converting SVG files to PNG...');

  try {
    // Convert logo.svg to various favicon sizes
    const logoPath = path.join(PUBLIC_DIR, 'logo.svg');
    if (fs.existsSync(logoPath)) {
      console.log('📱 Converting logo.svg to favicon sizes...');

      const logoBuffer = fs.readFileSync(logoPath);

      // Create favicon sizes
      await sharp(logoBuffer)
        .resize(16, 16)
        .png()
        .toFile(path.join(PUBLIC_DIR, 'favicon-16x16.png'));

      await sharp(logoBuffer)
        .resize(32, 32)
        .png()
        .toFile(path.join(PUBLIC_DIR, 'favicon-32x32.png'));

      await sharp(logoBuffer)
        .resize(48, 48)
        .png()
        .toFile(path.join(PUBLIC_DIR, 'favicon-48x48.png'));

      // Create apple-touch-icon
      await sharp(logoBuffer)
        .resize(180, 180)
        .png()
        .toFile(path.join(PUBLIC_DIR, 'apple-touch-icon.png'));

      // Create android-chrome icons
      await sharp(logoBuffer)
        .resize(192, 192)
        .png()
        .toFile(path.join(PUBLIC_DIR, 'android-chrome-192x192.png'));

      await sharp(logoBuffer)
        .resize(512, 512)
        .png()
        .toFile(path.join(PUBLIC_DIR, 'android-chrome-512x512.png'));

      console.log('✅ Favicon files created successfully!');
    } else {
      console.log('❌ logo.svg not found in', PUBLIC_DIR);
    }

    // Convert logo-full.svg to PNG for use in components
    const logoFullPath = path.join(PUBLIC_DIR, 'logo-full.svg');
    if (fs.existsSync(logoFullPath)) {
      console.log('🖼️  Converting logo-full.svg to PNG...');

      const logoFullBuffer = fs.readFileSync(logoFullPath);

      // Create different sizes for various uses
      await sharp(logoFullBuffer)
        .resize(200, 60)
        .png()
        .toFile(path.join(PUBLIC_DIR, 'logo-full-200x60.png'));

      await sharp(logoFullBuffer)
        .resize(300, 90)
        .png()
        .toFile(path.join(PUBLIC_DIR, 'logo-full-300x90.png'));

      await sharp(logoFullBuffer)
        .resize(400, 120)
        .png()
        .toFile(path.join(PUBLIC_DIR, 'logo-full-400x120.png'));

      console.log('✅ Logo PNG files created successfully!');
    } else {
      console.log('❌ logo-full.svg not found in', PUBLIC_DIR);
    }

    console.log('🎉 All conversions completed successfully!');
    console.log('');
    console.log('📁 Generated files:');
    console.log('  - favicon-16x16.png');
    console.log('  - favicon-32x32.png');
    console.log('  - favicon-48x48.png');
    console.log('  - apple-touch-icon.png');
    console.log('  - android-chrome-192x192.png');
    console.log('  - android-chrome-512x512.png');
    console.log('  - logo-full-200x60.png');
    console.log('  - logo-full-300x90.png');
    console.log('  - logo-full-400x120.png');

  } catch (error) {
    console.error('❌ Error converting SVG files:', error.message);
    process.exit(1);
  }
}

// Run the conversion
convertSvgToPng();
