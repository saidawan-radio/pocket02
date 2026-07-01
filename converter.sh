#!/bin/bash

extensions=("*.mp3" "*.m4a" "*.ogg" "*.flac" "*.acc" "*.wav" "*.webm" "*.aiff")


export DOWNLOAD_PATH
export COVER_PATH_DIR

mkdir -p ./"$COVER_PATH_DIR"
echo $COVER_PATH_DIR
for ext in "${extensions[@]}"; do
    find "$DOWNLOAD_PATH" -iname "$ext" -exec sh -c '
        input="$1"
        input_basename=$( basename $input)
        temp="${input}.temp.opus"
        song_output="${input}.opus"
        cover_name=$(echo "$input_basename" | grep -oE '^[0-9]+')
        cover_output="$COVER_PATH_DIR/$cover_name.jpg"
        ffmpeg -i ${input} -an -c:v copy -frames:v 1 -update 1 -y "$cover_output"  || echo "No cover found in $input"

         # Get bitrate in kbps
        br=$(ffprobe -v error -show_entries format=bit_rate -of default=noprint_wrappers=1:nokey=1 "$input")
        br_kbps=$((br / 1000))

        if [ "$br_kbps" -gt 128 ]; then
            target="128k"
        else
            target="${br_kbps}k"
        fi

        if ffmpeg -i "${input}" -vn -c:a libopus -b:a "$target" -map_metadata 0 "$temp" 2>/dev/null; then
            mv -f "$temp" "$song_output"
            rm -f "$input"
            echo "Converted: $input"
        else
            rm -f "$temp"
            echo "Failed: $input"
        fi
    ' _ {} \;

    if [ ! $? -eq 0 ]; then
        exit 1
    fi
done
