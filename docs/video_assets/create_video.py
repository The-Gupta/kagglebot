#!/usr/bin/env python3
"""
KaggleBot Demo Video - Seamless version
Uses single continuous narration + screenshot slideshow + subtitles
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
    return 170.0


def create_video():
    print("=" * 60)
    print("KaggleBot Demo Video — Seamless Build")
    print("=" * 60)

    audio_duration = get_duration(AUDIO)
    print(f"Audio: {audio_duration:.1f}s")

    # Screenshots sorted by filename
    screenshots = sorted([
        os.path.join(SCREENSHOTS, f)
        for f in os.listdir(SCREENSHOTS)
        if f.endswith(".png") and not f.startswith("01_hero_17832747932")  # skip duplicate
    ])
    print(f"Screenshots: {len(screenshots)}")

    # Timing: map each screenshot to a time range in the narration
    # These timestamps correspond to paragraph breaks in full_script.txt
    # Total: ~170s across 13 segments
    segment_times = [
        # (start_time, screenshot_index, subtitle)
        (0.0,   0,  "KaggleBot — AI-Powered Kaggle\nCompetition Strategy Agent"),
        (10.0,  0,  "4-8 hours on competition discovery...\nKaggleBot automates all of that"),
        (25.0,  1,  "5-agent system built with Google ADK\nOrchestrator → Scraper → Data → Strategy → Code"),
        (42.0,  2,  "🔍 Scraper Agent: Titanic Competition\nMetadata + Discussion Insights"),
        (54.0,  3,  "📊 Data Agent: 100 rows × 12 columns\nQuality: 89/100 | Target: Survived"),
        (69.0,  4,  "📋 Strategy Agent: 3 Ranked Approaches\n⏸️ HITL Gate — User Approves #1"),
        (84.0,  5,  "💻 Code Agent: 170 Lines of Python\n🔒 Security: safe = True"),
        (95.0,  6,  "🔒 Three Layers of Security\nValidation + Scanning + AST Analysis"),
        (109.0, 7,  "📡 Full Pipeline Trace\n5 Agents | 10 Tool Calls | 210ms"),
        (123.0, 8,  "🧩 11 Concepts Demonstrated\n6 Core + 5 Bonus"),
        (138.0, 9,  "📊 43 Files | 5,239 Lines\n5 Agents | 8 MCP Tools | 7/7 Tests"),
        (146.0, 10, "✅ All 7 E2E Tests Pass\nThree Competitions Verified"),
        (155.0, 11, "Built with ❤️ using\nGoogle ADK + Antigravity IDE"),
    ]

    # Generate SRT
    srt_path = os.path.join(ASSETS, "subtitles.srt")
    with open(srt_path, "w") as f:
        for i, (start, _, text) in enumerate(segment_times):
            end = segment_times[i + 1][0] if i + 1 < len(segment_times) else audio_duration
            sh, sm, ss = int(start//3600), int((start%3600)//60), int(start%60)
            sms = int((start % 1) * 1000)
            eh, em, es = int(end//3600), int((end%3600)//60), int(end%60)
            ems = int((end % 1) * 1000)
            f.write(f"{i+1}\n")
            f.write(f"{sh:02d}:{sm:02d}:{ss:02d},{sms:03d} --> {eh:02d}:{em:02d}:{es:02d},{ems:03d}\n")
            f.write(f"{text}\n\n")
    print(f"SRT: {srt_path}")

    # Build ffmpeg concat input for slideshow
    # Each screenshot displayed for its segment duration
    concat_path = os.path.join(ASSETS, "slideshow.txt")
    with open(concat_path, "w") as f:
        for i, (start, si, _) in enumerate(segment_times):
            end = segment_times[i + 1][0] if i + 1 < len(segment_times) else audio_duration
            duration = end - start
            img = screenshots[min(si, len(screenshots) - 1)]
            f.write(f"file '{img}'\n")
            f.write(f"duration {duration:.2f}\n")
        # ffmpeg concat needs the last file listed twice
        f.write(f"file '{screenshots[-1]}'\n")

    print("Building video...")

    # Step 1: Create slideshow video from images
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
        print(f"Slideshow error: {r1.stderr[-300:]}")
        return

    # Step 2: Combine slideshow + audio + subtitles
    r2 = subprocess.run([
        FFMPEG, "-y",
        "-i", temp_slideshow,
        "-i", AUDIO,
        "-vf", (
            f"subtitles='{srt_path}':force_style="
            "'FontName=Helvetica,FontSize=22,PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H80000000,BackColour=&H80000000,"
            "Bold=1,Outline=2,Shadow=1,MarginV=45,Alignment=2'"
        ),
        "-c:v", "libx264", "-preset", "medium", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-pix_fmt", "yuv420p",
        OUTPUT
    ], capture_output=True, text=True)

    if r2.returncode != 0:
        print(f"Subtitle burn-in failed: {r2.stderr[-300:]}")
        # Fallback without subtitles
        r3 = subprocess.run([
            FFMPEG, "-y",
            "-i", temp_slideshow,
            "-i", AUDIO,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            OUTPUT
        ], capture_output=True, text=True)
        if r3.returncode != 0:
            print(f"Final fallback failed: {r3.stderr[-300:]}")
            return

    # Cleanup
    os.remove(temp_slideshow)

    if os.path.exists(OUTPUT):
        size_mb = os.path.getsize(OUTPUT) / (1024 * 1024)
        dur = get_duration(OUTPUT)
        print(f"\n✅ FINAL VIDEO: {OUTPUT}")
        print(f"   Duration: {dur:.0f}s ({dur/60:.1f} min)")
        print(f"   Size: {size_mb:.1f} MB")
    else:
        print("❌ Video not created")


if __name__ == "__main__":
    create_video()
