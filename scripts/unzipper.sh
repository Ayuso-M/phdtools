#!/bin/bash

# Go through each .zip file in the current directory
for zipfile in *.zip; do
  # Skip if no zip files found
  [ -e "$zipfile" ] || continue

  # Remove .zip extension to get directory name
  dirname="${zipfile%.zip}"

  echo "Unzipping '$zipfile' into './$dirname/'..."

  # Create the directory if it doesn't exist
  mkdir -p "$dirname"

  # Unzip the contents into that directory
  unzip -q "$zipfile" -d "$dirname"

  if ! mv "$dirname"/Takeout/Fitbit/* "$dirname"/; then
        echo "Failed to move files from $dirname/Takeout/Fitbit/"
        continue
  fi

  rm -rf "$dirname/Takeout"

done


echo "✅ All zip files processed."