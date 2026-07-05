#!/usr/bin/env python3
"""
KaggleBot Demo Video v2 — Seamless, no subtitles
Uses: Samantha voice + Amex Default Prediction + 13 Amex-themed slides
"""
import os
import subprocess

FFMPEG = "/Users/vishal/bin/ffmpeg"
ASSETS = "/Users/vishal/Downloads/kagglebot/docs/video_assets"
SCREENSHOTS = os.path.join(ASSETS, "screenshots")
AUDIO = os.path.join(ASSETS, "full_narration.aiff")
OUTPUT = "/Users/vishal/Downloads/kagglebot/docs/kagglebot_demo.mp4"


def get_duration(filepath):
    try:
        r = subprocess.run(["afinfo", filepath], capture_output=True, text=True)
        for line in r.stdout.split("\n"):
            if "estimated duration:" in line:
                return float(line.split(":")[1].strip().split()[0])
    except:
        pass
    return 211.0


def create_video():
    print("=" * 60)
    print("KaggleBot Demo Video v2 — No Subtitles")
    print("=" * 60)

    audio_duration = get_duration(AUDIO)
    print(f"Audio: {audio_duration:.1f}s")

    # Screenshots sorted by filename
    screenshots = sorted([
        os.path.join(SCREENSHOTS, f)
        for f in os.listdir(SCREENSHOTS)
        if f.endswith(".png")
    ])
    print(f"Screenshots: {len(screenshots)}")
    for s in screenshots:
        print(f"  {os.path.basename(s)}")

    # Timing: map each screenshot to narration paragraph breaks
    # Total audio: ~211s, 13 segments
    # Script paragraphs map to slides:
    # 1. Hero (0-8s) - KaggleBot intro hook
    # 2. Hero (8-22s) - Problem statement
    # 3. Architecture (22-44s) - 5-agent pipeline description
    # 4. Chat UI (44-57s) - Live deployment intro
    # 5. Scraper (57-73s) - Amex scraper demo
    # 6. Data (73-91s) - Data profiling
    # 7. Strategy (91-111s) - Strategy ranking + HITL
    # 8. Code (111-126s) - Code generation + security check
    # 9. Security (126-143s) - 3 layers of security
    # 10. Observability (143-157s) - Pipeline trace
    # 11. Concepts (157-178s) - 11 concepts overview
    # 12. Stats + Tests (178-193s) - Project stats
    # 13. Outro (193-end) - Closing

    segment_times = [
        (0.0,   0),   # 01_hero — intro hook
        (8.0,   0),   # 01_hero — problem statement
        (22.0,  1),   # 02_architecture
        (44.0,  2),   # 03_chatui
        (57.0,  3),   # 04_scraper
        (73.0,  4),   # 05_data
        (91.0,  5),   # 06_strategy
        (111.0, 6),   # 07_code
        (126.0, 7),   # 08_security
        (143.0, 8),   # 09_observability
        (157.0, 9),   # 10_concepts
        (178.0, 10),  # 11_stats
        (188.0, 11),  # 12_tests
        (198.0, 12),  # 13_outro
    ]

    # Build ffmpeg concat for slideshow
    concat_path = os.path.join(ASSETS, "slideshow.txt")
    with open(concat_path, "w") as f:
        for i, (start, si) in enumerate(segment_times):
            end = segment_times[i + 1][0] if i + 1 < len(segment_times) else audio_duration
            duration = end - start
            img = screenshots[min(si, len(screenshots) - 1)]
            f.write(f"file '{img}'\n")
            f.write(f"duration {duration:.2f}\n")
        # ffmpeg concat needs the last file listed again
        f.write(f"file '{screenshots[-1]}'\n")

    print("\nBuilding slideshow...")

    # Step 1: Create slideshow from images
    temp_slideshow = os.path.join(ASSETS, "temp_slideshow.mp4")
    r1 = subprocess.run([
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_path,
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#0a0e17",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-pix_fmt", "yuv420p", "-r", "30",
        temp_slideshow
    ], capture_output=True, text=True)

    if r1.returncode != 0:
        print(f"Slideshow error: {r1.stderr[-500:]}")
        return

    print("Combining with audio (no subtitles)...")

    # Step 2: Combine slideshow + audio — NO subtitles
    r2 = subprocess.run([
        FFMPEG, "-y",
        "-i", temp_slideshow,
        "-i", AUDIO,
        "-c:v", "libx264", "-preset", "medium", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-pix_fmt", "yuv420p",
        OUTPUT
    ], capture_output=True, text=True)

    if r2.returncode != 0:
        print(f"Error: {r2.stderr[-500:]}")
        return

    # Cleanup
    if os.path.exists(temp_slideshow):
        os.remove(temp_slideshow)

    if os.path.exists(OUTPUT):
        size_mb = os.path.getsize(OUTPUT) / (1024 * 1024)
        print(f"\n✅ FINAL VIDEO: {OUTPUT}")
        print(f"   Duration: ~{audio_duration:.0f}s ({audio_duration/60:.1f} min)")
        print(f"   Size: {size_mb:.1f} MB")
        print(f"   Voice: Samantha (en_US)")
        print(f"   Subtitles: None")
        print(f"   Competition: Amex Default Prediction")
    else:
        print("❌ Video not created")


if __name__ == "__main__":
    create_video()
