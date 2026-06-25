#!/usr/bin/env bash
# Package script: builds the Kotlin app and zips the desktop distribution with the backend
set -e

# Build Kotlin app
pushd kotlin-frontend
./gradlew distZip -x test
popd

# Create a package folder
PKG=life-sim-package
rm -rf $PKG
mkdir -p $PKG

# Copy backend and frontend distribution
cp -r python-backend $PKG/
cp kotlin-frontend/build/compose/binaries/main/zip/release/* $PKG/ || true

# Zip it
zip -r ${PKG}.zip $PKG

echo "Packaged ${PKG}.zip"
