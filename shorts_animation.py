
import os
import sys
import math
import random
import shutil
import subprocess
import asyncio
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ============================================================
# PREMIUM YOUTUBE SHORTS GENERATOR
# Vertical 9:16 educational videos with animated visuals,
# kinetic typography, diagrams, transitions and narration.
# ============================================================

WIDTH = 720
HEIGHT = 1280
FPS = 24
DURATION = 24
TOTAL_FRAMES = FPS * DURATION

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

VIDEO_PATH = OUTPUT_DIR / "short.mp4"
TEMP_VIDEO = OUTPUT_DIR / "silent_video.mp4"
VOICE_PATH = OUTPUT_DIR / "voice.mp3"

# Change these details to create another science Short.
TITLE = "WHY IS THE SKY BLUE?"
CATEGORY = "SCIENCE EXPLAINED"
ACCENT = (70, 220, 255)
SECOND_ACCENT = (140, 105, 255)

NARRATION = (
    "Have you ever wondered why the sky is blue, "
    "instead of purple or green? Here's the science. "
    "Sunlight looks white, but it actually contains "
    "every colour of the rainbow. When sunlight enters "
    "Earth's atmosphere, it collides with tiny air molecules. "
    "These molecules scatter blue light much more strongly "
    "than red light. That scattered blue light travels "
    "in every direction, reaching your eyes from across "
    "the sky. And that's why the sky looks blue! "
    "Follow for more science explained in seconds."
)

SCENES = [
    {
        "start": 0, "end": 3,
        "eyebrow": "THE EVERYDAY MYSTERY",
        "lines": ["WHY IS THE", "SKY BLUE?"],
        "visual": "hook",
        "small": "There's a surprising reason."
    },
    {
        "start": 3, "end": 6,
        "eyebrow": "STEP 01  /  SUNLIGHT",
        "lines": ["SUNLIGHT", "CONTAINS", "EVERY COLOUR"],
        "visual": "sun",
        "small": "White light is a mixture of colours."
    },
    {
        "start": 6, "end": 10,
        "eyebrow": "STEP 02  /  ATMOSPHERE",
        "lines": ["LIGHT MEETS", "AIR MOLECULES"],
        "visual": "molecules",
        "small": "Tiny particles interact with sunlight."
    },
    {
        "start": 10, "end": 14,
        "eyebrow": "STEP 03  /  SCATTERING",
        "lines": ["BLUE LIGHT", "SCATTERS MORE"],
        "visual": "scatter",
        "small": "Shorter wavelengths scatter more strongly."
    },
    {
        "start": 14, "end": 19,
        "eyebrow": "THE SCIENCE",
        "lines": ["BLUE LIGHT", "REACHES YOUR", "EYES"],
        "visual": "eyes",
        "small": "Scattered light comes from across the sky."
    },
    {
        "start": 19, "end": 24,
        "eyebrow": "NOW YOU KNOW",
        "lines": ["THAT'S WHY", "THE SKY IS", "BLUE!"],
        "visual": "ending",
        "small": "Follow for more science in seconds."
    }
]

# ------------------------------------------------------------
# FONTS
# ------------------------------------------------------------

def load_font(size, bold=False):
    candidates = []

    if bold:
        candidates += [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ]
    else:
        candidates += [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]

    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


FONT_HUGE = load_font(82, True)
FONT_BIG = load_font(64, True)
FONT_MED = load_font(32, True)
FONT_SMALL = load_font(23)
FONT_TINY = load_font(18, True)

# ------------------------------------------------------------
# BACKGROUND
# ------------------------------------------------------------

def create_background():
    img = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = img.load()

    for y in range(HEIGHT):
        t = y / HEIGHT
        for x in range(WIDTH):
            glow = max(
                0,
                1 - math.sqrt(
                    ((x - 550) / 850) ** 2
                    + ((y - 350) / 1000) ** 2
                )
            )

            pixels[x, y] = (
                int(5 + 9 * t + 8 * glow),
                int(10 + 12 * t + 15 * glow),
                int(27 + 24 * t + 45 * glow),
            )

    return img


BACKGROUND = create_background()

random.seed(42)

PARTICLES = [
    (
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.uniform(0.3, 1.0),
        random.randint(1, 3),
        random.random() * math.pi * 2,
    )
    for _ in range(65)
]


def draw_background(draw, t):
    for x, y, speed, radius, phase in PARTICLES:
        yy = (y - t * 22 * speed) % HEIGHT
        xx = x + math.sin(t * 0.8 + phase) * 10
        brightness = int(65 + 80 * (0.5 + 0.5 * math.sin(t + phase)))

        draw.ellipse(
            (xx, yy, xx + radius * 2, yy + radius * 2),
            fill=(brightness // 2, brightness, min(255, brightness + 25))
        )

    # Subtle moving scanning line
    scan_y = int((t * 100) % HEIGHT)
    draw.line(
        (0, scan_y, WIDTH, scan_y),
        fill=(12, 33, 60),
        width=1
    )


# ------------------------------------------------------------
# TEXT AND GRAPHICS
# ------------------------------------------------------------

def centered_text(draw, text, y, font, fill, stroke=0):
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke)
    text_width = bbox[2] - bbox[0]
    x = (WIDTH - text_width) // 2

    draw.text(
        (x, y), text, font=font, fill=fill,
        stroke_width=stroke,
        stroke_fill=(5, 10, 25)
    )


def rounded_card(draw, box, fill, outline=None, radius=24, width=2):
    draw.rounded_rectangle(
        box,
        radius=radius,
        fill=fill,
        outline=outline,
        width=width
    )


def draw_header(draw, eyebrow, progress):
    draw.text(
        (42, 48), "SCIENCE / 001",
        font=FONT_TINY, fill=ACCENT
    )

    draw.text(
        (42, 83), eyebrow,
        font=FONT_SMALL, fill=(190, 205, 230)
    )

    # Progress track
    draw.rounded_rectangle(
        (42, 126, WIDTH - 42, 133),
        radius=4, fill=(35, 48, 75)
    )

    draw.rounded_rectangle(
        (42, 126, 42 + int((WIDTH - 84) * progress), 133),
        radius=4, fill=ACCENT
    )


def draw_footer(draw, text):
    draw.line(
        (42, HEIGHT - 100, WIDTH - 42, HEIGHT - 100),
        fill=(45, 61, 90), width=2
    )

    draw.text(
        (42, HEIGHT - 76), text,
        font=FONT_SMALL, fill=(185, 203, 225)
    )

    draw.text(
        (WIDTH - 172, HEIGHT - 75), "24 SEC",
        font=FONT_TINY, fill=ACCENT
    )


def draw_sun(draw, t):
    cx, cy = WIDTH // 2, 570
    pulse = 1 + 0.05 * math.sin(t * 4)
    radius = int(75 * pulse)

    # Rays
    for i in range(16):
        angle = i * math.pi / 8 + t * 0.12
        x1 = cx + math.cos(angle) * 105
        y1 = cy + math.sin(angle) * 105
        x2 = cx + math.cos(angle) * 140
        y2 = cy + math.sin(angle) * 140

        draw.line(
            (x1, y1, x2, y2),
            fill=(255, 185, 85), width=5
        )

    draw.ellipse(
        (cx-radius, cy-radius, cx+radius, cy+radius),
        fill=(255, 192, 75)
    )

    draw.ellipse(
        (cx-radius+14, cy-radius+14,
         cx+radius-14, cy+radius-14),
        fill=(255, 224, 125)
    )

    # Spectrum beams
    colours = [
        (255, 75, 75), (255, 150, 65), (255, 225, 80),
        (90, 225, 120), (70, 180, 255), (105, 110, 255),
        (190, 95, 255)
    ]

    for i, colour in enumerate(colours):
        y = 750 + i * 22
        draw.line(
            (170, 720, 550, y),
            fill=colour, width=5
        )


def draw_molecules(draw, t):
    # Floating air molecules
    centres = [
        (150, 500), (340, 430), (530, 520),
        (230, 680), (440, 730), (350, 900),
        (125, 870), (570, 920)
    ]

    for i, (x, y) in enumerate(centres):
        xx = x + math.sin(t * 1.8 + i) * 20
        yy = y + math.cos(t * 1.5 + i * 0.7) * 17
        r = 23 + int(3 * math.sin(t * 3 + i))

        draw.ellipse(
            (xx-r, yy-r, xx+r, yy+r),
            fill=(30, 105, 155),
            outline=ACCENT, width=3
        )

        draw.ellipse(
            (xx-r//2, yy-r//2, xx, yy),
            fill=(140, 230, 255)
        )

    # Light ray crossing the molecules
    start_x = 65
    end_x = int(655 + math.sin(t * 2) * 20)

    draw.line(
        (start_x, 615, end_x, 615),
        fill=(255, 211, 110), width=7
    )

    for i in range(6):
        x = (start_x + int(t * 170) + i * 115) % WIDTH
        draw.ellipse(
            (x-7, 607, x+7, 621),
            fill=(255, 245, 190)
        )


def draw_scattering(draw, t):
    cx, cy = WIDTH // 2, 660

    draw.ellipse(
        (cx-32, cy-32, cx+32, cy+32),
        fill=(90, 205, 255)
    )

    # Blue rays scatter in different directions
    for i in range(14):
        angle = i * math.pi / 7 + t * 0.18
        length = 140 + 35 * math.sin(t * 3 + i)

        x = cx + math.cos(angle) * length
        y = cy + math.sin(angle) * length

        draw.line(
            (cx, cy, x, y),
            fill=(75, 195, 255), width=4
        )

        draw.ellipse(
            (x-5, y-5, x+5, y+5),
            fill=(180, 240, 255)
        )

    # Red light continues forward
    draw.line(
        (cx+40, cy+60, cx+220, cy+240),
        fill=(255, 105, 105), width=5
    )

    draw.text(
        (cx+100, cy+250), "RED",
        font=FONT_TINY, fill=(255, 135, 135)
    )

    draw.text(
        (cx-245, cy+250), "BLUE",
        font=FONT_TINY, fill=ACCENT
    )


def draw_earth_and_sky(draw, t):
    # Atmospheric glow
    draw.ellipse(
        (40, 680, 680, 1320),
        fill=(13, 51, 94),
        outline=(45, 155, 230), width=5
    )

    draw.ellipse(
        (65, 705, 655, 1295),
        fill=(14, 78, 125),
        outline=(65, 190, 255), width=3
    )

    # Simplified continents
    draw.ellipse((180, 820, 330, 920), fill=(40, 150, 115))
    draw.ellipse((380, 930, 510, 1050), fill=(40, 150, 115))

    # Scattered light reaching the observer
    for i in range(9):
        x = 120 + i * 60
        draw.line(
            (x, 720, WIDTH // 2, 1040),
            fill=(65, 190, 255), width=2
        )

    # Observer
    cx = WIDTH // 2
    draw.ellipse(
        (cx-23, 1015, cx+23, 1061),
        fill=(240, 244, 255)
    )

    draw.rounded_rectangle(
        (cx-42, 1060, cx+42, 1150),
        radius=20, fill=(235, 240, 255)
    )


def draw_hook(draw, t):
    # Giant glowing question mark
    pulse = 1 + 0.04 * math.sin(t * 5)
    radius = int(115 * pulse)
    cx, cy = WIDTH // 2, 680

    draw.ellipse(
        (cx-radius, cy-radius, cx+radius, cy+radius),
        fill=(15, 40, 75),
        outline=ACCENT, width=5
    )

    centered_text(draw, "?", cy-90, FONT_HUGE, (240, 250, 255))

    # Floating mini colour spectrum
    colours = [
        (255, 85, 85), (255, 160, 70),
        (255, 220, 75), (80, 220, 135),
        (70, 175, 255), (155, 115, 255)
    ]

    for i, colour in enumerate(colours):
        x = 100 + i * 90
        y = 890 + math.sin(t * 3 + i) * 18

        draw.rounded_rectangle(
            (x, y, x+55, y+14),
            radius=7, fill=colour
        )


def draw_ending(draw, t):
    cx, cy = WIDTH // 2, 720

    # Radiating rings
    for i in range(5):
        r = 75 + i * 36 + int(8 * math.sin(t * 3 + i))
        draw.ellipse(
            (cx-r, cy-r, cx+r, cy+r),
            outline=(40 + i * 15, 140 + i * 15, 255),
            width=3
        )

    # Bright central sphere
    draw.ellipse(
        (cx-55, cy-55, cx+55, cy+55),
        fill=(85, 205, 255)
    )

    draw.ellipse(
        (cx-28, cy-35, cx-5, cy-12),
        fill=(225, 250, 255)
    )

    # CTA card
    rounded_card(
        draw,
        (80, 925, WIDTH-80, 1030),
        (20, 45, 82),
        outline=ACCENT, radius=25, width=3
    )

    centered_text(
        draw, "FOLLOW FOR MORE", 950,
        FONT_MED, (240, 250, 255)
    )


# ------------------------------------------------------------
# SCENE RENDERING
# ------------------------------------------------------------

def render_frame(t):
    frame = BACKGROUND.copy()
    draw = ImageDraw.Draw(frame)

    draw_background(draw, t)

    scene = SCENES[-1]

    for candidate in SCENES:
        if candidate["start"] <= t < candidate["end"]:
            scene = candidate
            break

    local_t = t - scene["start"]
    scene_duration = scene["end"] - scene["start"]

    # Smooth entrance
    entrance = min(1, local_t / 0.35)
    progress = min(1, t / DURATION)

    draw_header(draw, scene["eyebrow"], progress)

    visual = scene["visual"]

    if visual == "hook":
        draw_hook(draw, local_t)
    elif visual == "sun":
        draw_sun(draw, local_t)
    elif visual == "molecules":
        draw_molecules(draw, local_t)
    elif visual == "scatter":
        draw_scattering(draw, local_t)
    elif visual == "eyes":
        draw_earth_and_sky(draw, local_t)
    elif visual == "ending":
        draw_ending(draw, local_t)

    # Kinetic captions
    line_count = len(scene["lines"])
    line_height = 82

    if visual in ("hook", "sun", "molecules", "scatter"):
        text_start_y = 190
    elif visual == "eyes":
        text_start_y = 185
    else:
        text_start_y = 235

    if visual == "ending":
        text_start_y = 240

    for i, line in enumerate(scene["lines"]):
        y = text_start_y + i * line_height

        # Small vertical entrance movement
        y += int((1 - entrance) * 25)

        colour = (
            ACCENT if i == line_count - 1
            else (248, 250, 255)
        )

        centered_text(
            draw, line, y,
            FONT_BIG, colour, stroke=2
        )

    # Explanatory subtitle card
    card_y = 1090 if visual not in ("eyes", "ending") else 1080

    rounded_card(
        draw,
        (42, card_y, WIDTH-42, card_y+70),
        (12, 24, 47),
        outline=(38, 66, 100),
        radius=18, width=2
    )

    # Wrap small text to fit the card
    subtitle = scene["small"]
    centered_text(
        draw, subtitle, card_y+22,
        FONT_SMALL, (215, 228, 245)
    )

    # Persistent footer and progress
    draw.line(
        (42, HEIGHT-48, WIDTH-42, HEIGHT-48),
        fill=(40, 57, 82), width=2
    )

    draw.text(
        (42, HEIGHT-38), "THE SCIENCE IS EVERYWHERE",
        font=FONT_TINY, fill=(145, 175, 210)
    )

    draw.text(
        (WIDTH-110, HEIGHT-38),
        f"{int(t)+1:02d}/24",
        font=FONT_TINY, fill=ACCENT
    )

    return frame


# ------------------------------------------------------------
# OPTIONAL AI NARRATION
# ------------------------------------------------------------

async def generate_voice():
    try:
        import edge_tts

        communicate = edge_tts.Communicate(
            NARRATION,
            voice="en-US-AriaNeural",
            rate="+5%",
            pitch="+0Hz"
        )

        await communicate.save(str(VOICE_PATH))

        if VOICE_PATH.exists() and VOICE_PATH.stat().st_size > 1000:
            print("AI narration generated successfully.")
            return True

    except Exception as error:
        print("Narration unavailable:", error)

    return False


# ------------------------------------------------------------
# VIDEO ENCODING
# ------------------------------------------------------------

def make_video():
    ffmpeg = shutil.which("ffmpeg")

    if not ffmpeg:
        raise RuntimeError(
            "FFmpeg is missing. Install FFmpeg in the workflow."
        )

    command = [
        ffmpeg,
        "-y",
        "-loglevel", "error",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-r", str(FPS),
        "-i", "-",
        "-an",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(TEMP_VIDEO)
    ]

    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE
    )

    try:
        for index in range(TOTAL_FRAMES):
            t = index / FPS
            frame = render_frame(t)

            process.stdin.write(frame.tobytes())

            if index % (FPS * 2) == 0:
                print(
                    f"Rendering: {index}/{TOTAL_FRAMES} frames"
                )

    except Exception:
        process.kill()
        raise

    finally:
        if process.stdin:
            process.stdin.close()

    result = process.wait()

    if result != 0 or not TEMP_VIDEO.exists():
        raise RuntimeError("FFmpeg failed to create the video.")


def add_audio():
    ffmpeg = shutil.which("ffmpeg")

    if VOICE_PATH.exists() and VOICE_PATH.stat().st_size > 1000:
        command = [
            ffmpeg, "-y", "-loglevel", "error",
            "-i", str(TEMP_VIDEO),
            "-i", str(VOICE_PATH),
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-af", "apad",
            "-t", str(DURATION),
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "160k",
            "-movflags", "+faststart",
            str(VIDEO_PATH)
        ]
    else:
        # Always create a valid video, even if online TTS fails.
        command = [
            ffmpeg, "-y", "-loglevel", "error",
            "-i", str(TEMP_VIDEO),
            "-t", str(DURATION),
            "-c:v", "copy",
            "-an",
            "-movflags", "+faststart",
            str(VIDEO_PATH)
        ]

    subprocess.run(command, check=True)


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():
    print("=" * 55)
    print("PREMIUM SCIENCE SHORTS GENERATOR")
    print("Topic:", TITLE)
    print("Resolution:", f"{WIDTH}x{HEIGHT}")
    print("Duration:", f"{DURATION} seconds")
    print("=" * 55)

    # Generate narration if edge-tts is installed.
    try:
        asyncio.run(generate_voice())
    except Exception as error:
        print("Continuing without narration:", error)

    make_video()
    add_audio()

    print("=" * 55)
    print("VIDEO CREATED SUCCESSFULLY!")
    print("Output:", VIDEO_PATH)
    print("=" * 55)


if __name__ == "__main__":
    main()
        
