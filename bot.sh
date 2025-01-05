#!/bin/bash

# Sticker2gif shell version
# Based on github.com/rhythmcache
# Dependencies: curl, jq, ffmpeg
BOT_TOKEN="Enter Your Bot Token Here"
TEMP_DIR="temp_files"
API_URL="https://api.telegram.org/bot$BOT_TOKEN"
UPDATES_URL="$API_URL/getUpdates"
SEND_DOC_URL="$API_URL/sendDocument"
SEND_MSG_URL="$API_URL/sendMessage"
GET_FILE_URL="$API_URL/getFile"
mkdir -p "$TEMP_DIR"
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> bot.log
}
download_file() {
    local file_path="$1"
    local output_path="$2"
    curl -s "https://api.telegram.org/file/bot$BOT_TOKEN/$file_path" -o "$output_path"
}
send_message() {
    local chat_id="$1"
    local text="$2"
    curl -s -X POST "$SEND_MSG_URL" \
        -F "chat_id=$chat_id" \
        -F "text=$text"
}
send_document() {
    local chat_id="$1"
    local file_path="$2"
    curl -s -X POST "$SEND_DOC_URL" \
        -F "chat_id=$chat_id" \
        -F "document=@$file_path"
}
handle_sticker() {
    local chat_id="$1"
    local file_id="$2"
    local is_animated="$3"
    local file_info
    file_info=$(curl -s -X POST "$GET_FILE_URL" -F "file_id=$file_id")
    local file_path
    file_path=$(echo "$file_info" | jq -r '.result.file_path')
    local sticker_path="$TEMP_DIR/${file_id}.webp"
    download_file "$file_path" "$sticker_path"

    if [ "$is_animated" = "true" ]; then
        local output_path="$TEMP_DIR/${file_id}.gif"
        ffmpeg -i "$sticker_path" -y "$output_path" 2>/dev/null
        send_document "$chat_id" "$output_path"
        rm "$output_path"
    else
        local output_path="$TEMP_DIR/${file_id}.png"
        ffmpeg -i "$sticker_path" -y "$output_path" 2>/dev/null
        send_document "$chat_id" "$output_path"
        rm "$output_path"
    fi
    rm "$sticker_path"
}
last_update_id=0
log "Bot started"
send_startup_message=true
while true; do
    updates=$(curl -s "$UPDATES_URL?offset=$((last_update_id + 1))")   
    while read -r update; do
        [ -z "$update" ] && continue 
        update_id=$(echo "$update" | jq -r '.update_id')
        chat_id=$(echo "$update" | jq -r '.message.chat.id')
        message_type=$(echo "$update" | jq -r '.message.sticker // empty')
        if [ "$send_startup_message" = true ] && [ ! -z "$chat_id" ]; then
            send_message "$chat_id" "Hi! Send me a sticker, and I'll convert it to PNG or GIF for you!"
            send_startup_message=false
        fi
        if [ ! -z "$message_type" ]; then
            file_id=$(echo "$update" | jq -r '.message.sticker.file_id')
            is_animated=$(echo "$update" | jq -r '.message.sticker.is_animated // .message.sticker.is_video')
            handle_sticker "$chat_id" "$file_id" "$is_animated"
        elif [ ! -z "$chat_id" ]; then
            # Handle non-sticker message
            send_message "$chat_id" "Please send me a sticker, and I'll convert it to PNG or GIF for you!"
        fi

        # Update last_update_id
        if [ "$update_id" -gt "$last_update_id" ]; then
            last_update_id=$update_id
        fi
    done < <(echo "$updates" | jq -c '.result[]')

    sleep 1
done
