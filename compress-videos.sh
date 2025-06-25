#!/bin/bash

# Base directories
DESKTOP_DIR="/Users/justincannon/Desktop"
VIDEO_COMPRESSION_DIR="$DESKTOP_DIR/video-compression"
OUTPUT_DIR="$VIDEO_COMPRESSION_DIR/compressed"
UNCOMPRESSED_DIR="$VIDEO_COMPRESSION_DIR/uncompressed"
PROJECT_DIR="/Users/justincannon/Desktop/Spanish Book/spanish-book/public/video/"

# Change to desktop directory
cd "$DESKTOP_DIR"

# Loop through all mp4 files on the desktop
for video in *.mp4; do
    # Check if file exists (in case no mp4 files are found)
    [ -e "$video" ] || continue

    echo "Compressing $video..."

    # Get filename without extension
    filename="${video%.*}"

    # Compress the video
    ffmpeg -i "$video" \
           -c:v libx264 -preset slow -crf 23 \
           -b:v 400k -maxrate 800k -bufsize 800k \
           -vf "scale=350:350" \
           -c:a aac -b:a 128k \
           "$OUTPUT_DIR/${filename}.mp4"

    if [ $? -eq 0 ]; then
        echo "Successfully compressed $video"
        mv "$video" "$UNCOMPRESSED_DIR/"
        mv "$OUTPUT_DIR/${filename}.mp4" "$PROJECT_DIR"
    else
        echo "Failed to compress $video"
    fi
done

echo "All videos processed."