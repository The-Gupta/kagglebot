#!/usr/bin/env python3
"""
KaggleBot Demo Video Generator v3 - Slideshow with narration + subtitles
Creates MP4 from 14 screenshots + 13 audio segments + SRT subtitles
"""
import os
import subprocess
import glob

FFMPEG = "/Users/vishal/bin/ffmpeg"
ASSETS = "/Users/vishal/Downloads/kagglebot/docs/video_assets"
SCREENSHOTS = os.path.join(ASSETS, "screenshots")
OUTPUT = "/Users/vishal/Downloads/kagglebot/docs/kagglebot_demo.mp4"


def get_audio_duration(filepath):
    try:
        result = subprocess.run(["afinfo", filepath], capture_output=True, text=True)
        for line in result.stdout.split("\n"):
            if "estimated duration:" in line:
                return float(line.split(":")[1].strip().split()[0])
    except:
        pass
    return 5.0


def create_video():
    print("=" * 60)
    print("KaggleBot Demo Video - Slideshow Generator v3")
    print("=" * 60)

    # Get audio segments
    audio_files = sorted(glob.glob(os.path.join(ASSETS, "[0-1]*.aiff")))
    # Filter out test files
    audio_files = [f for f in audio_files if "test_" not in os.path.basename(f)]
    print(f"Audio segments: {len(audio_files)}")

    # Get screenshots (sorted by name)
    screenshots = sorted(glob.glob(os.path.join(SCREENSHOTS, "*.png")))
    # Remove the duplicate hero screenshot (use only the bigger one)
    screenshots = [s for s in screenshots if "1783274793297" not in s]
    print(f"Screenshots: {len(screenshots)}")

    # Map screenshots to audio segments
    # Audio: 01_hook, 02_problem, 03_arch, 04_scraper, 05_data, 06_strategy, 07_code, 08_security, 09_obs, 10_concepts, 11_stats, 12_tests, 13_outro
    # Screenshots: 01_hero, 02_arch, 03_scraper, 04_data, 05_strategy, 06_code, 07_security, 08_obs, 09_concepts, 10_stats, 11_tests, 12_footer, 13_cloudrun
    segment_mapping = [
        # (audio_idx, screenshot_idx, subtitle_text)
        (0, 0, "KaggleBot — AI-Powered Kaggle\nCompetition Strategy Agent"),
        (1, 0, "When you join a Kaggle competition,\nyou spend 4-8 hours on discovery..."),
        (2, 1, "5-agent system built with Google ADK\nOrchestrator → Scraper → Data → Strategy → Code"),
        (3, 2, "🔍 Scraper Agent: Titanic Competition\nBinary Classification | Metric: Accuracy"),
        (4, 3, "📊 Data Agent: 100 rows × 12 columns\nQuality: 89/100 | Target: Survived"),
        (5, 4, "📋 Strategy Agent: 3 Ranked Approaches\n⏸️ HITL — User Approves Strategy #1"),
        (6, 5, "💻 Code Agent: 170 Lines of Secure Python\n🔒 Security Check: safe=True"),
        (7, 6, "🔒 Three Layers of Security\nValidation + Scanning + AST Analysis"),
        (8, 7, "📡 Full Pipeline Trace\n5 Agents | 10 Tool Calls | 210ms"),
        (9, 8, "🧩 11 Concepts Demonstrated\n6 Core + 5 Bonus"),
        (10, 9, "📊 43 Files | 5,239 Lines | 5 Agents\n8 MCP Tools | 7/7 Tests"),
        (11, 10, "✅ All 7 E2E Tests Pass\nThree Competitions Verified"),
        (12, 11, "Built with ❤️ using\nGoogle ADK + Antigravity IDE"),
    ]

    SILENCE_GAP = 1.0  # seconds between segments

    # Step 1: Get durations for each audio segment
    durations = []
    for af in audio_files:
        d = get_audio_duration(af)
        durations.append(d)
        print(f"  {os.path.basename(af)}: {d:.1f}s")

    total_duration = sum(durations) + SILENCE_GAP * (len(durations) - 1)
    print(f"\nTotal audio duration: {total_duration:.1f}s")

    # Step 2: Create individual video clips for each segment (screenshot + audio)
    clip_files = []
    srt_entries = []
    current_time = 0.0

    for i, (audio_idx, screen_idx, subtitle) in enumerate(segment_mapping):
        if audio_idx >= len(audio_files) or screen_idx >= len(screenshots):
            continue

        audio = audio_files[audio_idx]
        screenshot = screenshots[screen_idx]
        duration = durations[audio_idx]
        clip_duration = duration + SILENCE_GAP

        clip_path = os.path.join(ASSETS, f"clip_{i:02d}.mp4")

        # Create clip: screenshot displayed for audio duration + gap
        result = subprocess.run([
            FFMPEG, "-y",
            "-loop", "1",
            "-i", screenshot,
            "-i", audio,
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#0a0e17",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(clip_duration),
            "-pix_fmt", "yuv420p",
            "-r", "30",
            clip_path
        ], capture_output=True, text=True)

        if result.returncode == 0 and os.path.exists(clip_path):
            clip_files.append(clip_path)

            # SRT entry
            start = current_time
            end = current_time + duration
            srt_entries.append((i + 1, start, end, subtitle))
            current_time += clip_duration
        else:
            print(f"  ❌ Failed clip {i}: {result.stderr[-200:]}")

    print(f"\nCreated {len(clip_files)} clips")

    # Step 3: Write SRT file
    srt_path = os.path.join(ASSETS, "subtitles.srt")
    with open(srt_path, "w") as f:
        for idx, start, end, text in srt_entries:
            sh, sm, ss, sms = int(start//3600), int((start%3600)//60), int(start%60), int((start%1)*1000)
            eh, em, es, ems = int(end//3600), int((end%3600)//60), int(end%60), int((end%1)*1000)
            f.write(f"{idx}\n")
            f.write(f"{sh:02d}:{sm:02d}:{ss:02d},{sms:03d} --> {eh:02d}:{em:02d}:{es:02d},{ems:03d}\n")
            f.write(f"{text}\n\n")
    print(f"SRT saved: {srt_path}")

    # Step 4: Concatenate all clips
    concat_list = os.path.join(ASSETS, "clips_concat.txt")
    with open(concat_list, "w") as f:
        for clip in clip_files:
            f.write(f"file '{clip}'\n")

    # Concat without re-encoding (all clips have same codec/resolution)
    temp_concat = os.path.join(ASSETS, "concat_nosub.mp4")
    result = subprocess.run([
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        temp_concat
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Concat error: {result.stderr[-300:]}")
        return

    print(f"Concatenated video: {get_audio_duration(temp_concat):.1f}s")

    # Step 5: Burn in subtitles
    result = subprocess.run([
        FFMPEG, "-y",
        "-i", temp_concat,
        "-vf", (
            f"subtitles='{srt_path}':force_style="
            "'FontName=Helvetica,FontSize=22,PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H80000000,BackColour=&H80000000,"
            "Bold=1,Outline=2,Shadow=1,MarginV=45,Alignment=2'"
        ),
        "-c:v", "libx264", "-preset", "medium", "-crf", "22",
        "-c:a", "copy",
        "-pix_fmt", "yuv420p",
        OUTPUT
    ], capture_output=True, text=True)

    if result.returncode == 0 and os.path.exists(OUTPUT):
        size_mb = os.path.getsize(OUTPUT) / (1024 * 1024)
        dur = get_audio_duration(OUTPUT)
        print(f"\n✅ FINAL VIDEO: {OUTPUT}")
        print(f"   Duration: {dur:.0f}s ({dur/60:.1f} min)")
        print(f"   Size: {size_mb:.1f} MB")
        print(f"   Subtitles: burned in")
    else:
        # Fallback: output without subtitles, upload SRT separately
        print(f"Subtitle burn-in failed: {result.stderr[-300:]}")
        os.rename(temp_concat, OUTPUT)
        size_mb = os.path.getsize(OUTPUT) / (1024 * 1024)
        print(f"\n✅ Video (no subtitles): {OUTPUT} ({size_mb:.1f} MB)")
        print(f"   Upload {srt_path} as subtitle track on YouTube")

    # Cleanup temp clips
    for clip in clip_files:
        os.remove(clip)
    if os.path.exists(temp_concat):
        os.remove(temp_concat)
    print("\nCleaned up temp files.")


if __name__ == "__main__":
    create_video()
