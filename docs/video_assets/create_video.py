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

    # Timing: measured paragraph durations from TTS engine
    # Each paragraph gap adds ~0.15s of natural silence in continuous audio
    # Individual paragraph durations (measured):
    #   1:  9.4s  2: 15.6s  3: 25.7s  4: 11.2s  5: 16.1s  6: 16.5s  7: 18.6s
    #   8: 15.0s  9: 15.3s 10: 13.1s 11: 31.3s 12:  9.2s 13: 12.4s
    # Total measured: 209.5s, continuous audio: 211.4s → ~0.15s gap per paragraph

    GAP = 0.15  # inter-paragraph silence in continuous TTS

    segment_times = [
        (  0.00,  0),   # 01_hero (9.4s)
        (  9.58,  1),   # 02_problem (15.6s)
        ( 25.33,  2),   # 03_architecture (25.7s)
        ( 51.18,  3),   # 04_chatui_live (11.2s)
        ( 62.53,  4),   # 05_scraper (16.1s)
        ( 78.78,  5),   # 06_data (16.5s)
        ( 95.43,  6),   # 07_strategy (18.6s)
        (114.18,  7),   # 08_code (15.0s)
        (129.38,  8),   # 09_security (15.3s)
        (144.88,  9),   # 10_observability (13.1s)
        (158.17, 10),   # 11_concepts (31.3s)
        (189.62, 11),   # 12_stats (9.2s)
        (198.97, 12),   # 13_outro (12.4s)
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
