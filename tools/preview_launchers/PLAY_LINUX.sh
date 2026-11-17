#!/usr/bin/env bash
set -e
preview_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
profile_dir="$preview_dir/profile/linux"
mkdir -p "$profile_dir/config" "$profile_dir/data"
export XDG_CONFIG_HOME="$profile_dir/config"
export XDG_DATA_HOME="$profile_dir/data"
export AYAY_OPTIONS_PATH="$profile_dir/options.json"
export AYAY_DIALOGUE_SAVE_PATH="$profile_dir/dialogue.json"
export AYAY_P06_DIALOGUE_SAVE_PATH="$profile_dir/cast.json"
export AYAY_CHAPTER_SAVE_PATH="$profile_dir/chapter.json"
export AYAY_STORY_SAVE_PATH="$profile_dir/story.json"
exec "$preview_dir/linux/last-skuf.x86_64" -- --open-mission "$@"
