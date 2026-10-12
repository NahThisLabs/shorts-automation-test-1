
import os
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont

W, H = 720, 1280
FPS = 24
DURATION = 20
TOTAL = FPS * DURATION

os.makedirs("output", exist_ok=True)

scenes = [
    ("WHY ISN'T THE SKY PURPLE?",
     "Sunlight contains every colour."),
    ("AIR SCATTERS BLUE LIGHT",
     "Tiny air molecules scatter blue light."),
    ("BLUE REACHES YOUR EYES",
     "Blue light scatters across the sky."),
    ("THAT'S WHY IT LOOKS BLUE!",
     "Our eyes see more scattered blue light.")
]

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
title_font = ImageFont.truetype(font_path, 39)
body_font = ImageFont.truetype(font_path, 31)
small_font = ImageFont.truetype(font_path, 22)

# Create narration with free offline speech if available.
narration = (
    "Why isn't the sky purple? Sunlight contains every colour. "
    "Air molecules scatter blue light more than most other colours. "
    "That scattered blue light reaches your eyes from across the sky. "
    "That's why the sky looks blue!"
)

with open("output/narration.txt", "w") as f:
    f.write(narration)

# Generate a silent animated video first.
cmd = [
    "ffmpeg", "-y",
    "-f", "rawvideo", "-pix_fmt", "rgb24",
    "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
    "output/silent.mp4"
]

p = subprocess.Popen(cmd, stdin=subprocess.PIPE)

try:
    for frame in range(TOTAL):
        t = frame / FPS
        scene = min(int(t // 5), 3)
        title, caption = scenes[scene]

        img = Image.new("RGB", (W, H), (8, 24, 65))
        draw = ImageDraw.Draw(img)

        # Animated atmospheric rings
        for i in range(5):
            r = int(75 + i * 30 + 12 * math.sin(t * 2 + i))
            cx, cy = W // 2, 390
            draw.ellipse(
                (cx-r, cy-r, cx+r, cy+r),
                outline=(40, 130 + i * 20, 255),
                width=3
            )

        # Animated light particles
        for i in range(18):
            x = int((i * 47 + t * (40 + i)) % W)
            y = int(250 + (i * 71) % 330)
            draw.ellipse((x-5, y-5, x+5, y+5),
                         fill=(100, 220, 255))

        draw.text((W//2, 720), title, font=title_font,
                  fill="white", anchor="mm", align="center")

        draw.rounded_rectangle((40, 790, 680, 960),
                                radius=25, fill=(15, 50, 110),
                                outline=(60, 180, 255), width=3)

        draw.multiline_text((W//2, 875), caption, font=body_font,
                            fill="white", anchor="mm",
                            align="center", spacing=12)

        progress = int(620 * frame / (TOTAL - 1))
        draw.rounded_rectangle((50, 1110, 670, 1125),
                               radius=7, fill=(40, 70, 120))
        draw.rounded_rectangle((50, 1110, 50 + progress, 1125),
                               radius=7, fill=(70, 230, 255))

        p.stdin.write(img.tobytes())
finally:
    p.stdin.close()

if p.wait() != 0:
    raise RuntimeError("Video creation failed")

print("Animated video created successfully.")
print("Narration text saved to output/narration.txt")
            
