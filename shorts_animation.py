
import os
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont

W, H = 720, 1280
FPS = 24
DURATION = 15
TOTAL = FPS * DURATION

os.makedirs("output", exist_ok=True)

title = "WHY IS THE SKY BLUE?"
captions = [
    "Sunlight contains many colours.",
    "Air scatters blue light",
    "more than most other colours.",
    "That's why the sky looks blue!"
]

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
title_font = ImageFont.truetype(font_path, 42)
caption_font = ImageFont.truetype(font_path, 34)
small_font = ImageFont.truetype(font_path, 23)

cmd = [
    "ffmpeg", "-y",
    "-f", "rawvideo",
    "-pix_fmt", "rgb24",
    "-s", f"{W}x{H}",
    "-r", str(FPS),
    "-i", "-",
    "-an", "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-movflags", "+faststart",
    "output/short.mp4"
]

process = subprocess.Popen(
    cmd, stdin=subprocess.PIPE
)

try:
    for frame in range(TOTAL):
        t = frame / FPS

        img = Image.new("RGB", (W, H))
        pixels = img.load()

        # Animated blue gradient
        for y in range(H):
            for x in range(W):
                glow = int(12 * math.sin(t + x / 180))
                pixels[x, y] = (
                    8,
                    max(0, 25 + y // 35 + glow),
                    min(255, 90 + y // 9 + glow)
                )

        draw = ImageDraw.Draw(img)

        # Floating animated circles
        for i in range(12):
            x = int((i * 83 + t * (25 + i)) % W)
            y = int((i * 137 - t * (30 + i)) % H)
            r = 12 + int(5 * math.sin(t * 2 + i))
            draw.ellipse(
                (x-r, y-r, x+r, y+r),
                outline=(70, 190, 255),
                width=3
            )

        # Moving, bouncing ball
        bx = int(W / 2 + 220 * math.sin(t * 1.5))
        by = int(230 + 35 * math.sin(t * 3))
        draw.ellipse(
            (bx-30, by-30, bx+30, by+30),
            fill=(255, 220, 70)
        )

        # Title with entrance animation
        title_y = 340 + int(20 * math.sin(t * 2))
        draw.text(
            (W//2, title_y),
            title,
            font=title_font,
            fill="white",
            anchor="mm",
            stroke_width=2,
            stroke_fill=(0, 35, 90)
        )

        # Reveal a new caption every 3 seconds
        index = min(int(t // 3), 3)
        caption = captions[index]

        draw.rounded_rectangle(
            (45, 535, 675, 760),
            radius=30,
            fill=(10, 45, 105),
            outline=(80, 200, 255),
            width=3
        )

        draw.multiline_text(
            (W//2, 645),
            caption,
            font=caption_font,
            fill="white",
            anchor="mm",
            align="center",
            spacing=15
        )

        # Animated progress bar
        progress = int((frame / (TOTAL - 1)) * 620)
        draw.rounded_rectangle(
            (50, 1120, 670, 1135),
            radius=7,
            fill=(50, 90, 140)
        )
        draw.rounded_rectangle(
            (50, 1120, 50 + progress, 1135),
            radius=7,
            fill=(70, 230, 255)
        )

        draw.text(
            (W//2, 1190),
            "SCIENCE IN 30 SECONDS",
            font=small_font,
            fill=(190, 235, 255),
            anchor="mm"
        )

        process.stdin.write(img.tobytes())

finally:
    process.stdin.close()
    process.wait()

if process.returncode != 0:
    raise RuntimeError("FFmpeg failed to create the video")

print("Animated video created: output/short.mp4")
        
