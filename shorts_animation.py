
import os
import subprocess
import textwrap
from PIL import Image, ImageDraw, ImageFont

os.makedirs("output", exist_ok=True)

title = "WHY IS THE SKY BLUE?"
lines = [
    "Sunlight contains many colours.",
    "Air molecules scatter blue light",
    "more than most other colours.",
    "That is why the sky looks blue!"
]

W, H = 1080, 1920
img = Image.new("RGB", (W, H), (12, 25, 60))
draw = ImageDraw.Draw(img)

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font = ImageFont.truetype(font_path, 64)
body_font = ImageFont.truetype(font_path, 48)

draw.text((70, 300), title, font=font, fill="white")

for i, line in enumerate(lines):
    draw.text((70, 600 + i * 100), line, font=body_font, fill=(130, 210, 255))

draw.text((70, 1500), "SCIENCE IN 30 SECONDS", font=body_font, fill="white")
img.save("output/short.png")

subprocess.run([
    "ffmpeg", "-y", "-loop", "1",
    "-i", "output/short.png",
    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
    "-t", "15", "-vf", "scale=720:1280",
    "-c:v", "libx264", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-shortest",
    "output/short.mp4"
], check=True)

print("Video created: output/short.mp4")
