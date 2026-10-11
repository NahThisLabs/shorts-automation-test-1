
import os
import random
import subprocess

OUTPUT = "output"
os.makedirs(OUTPUT, exist_ok=True)

facts = [
    ("Why is space dark?",
     "Space looks dark because it contains very little matter to scatter sunlight into our eyes."),
    ("Why is the sky blue?",
     "Air molecules scatter blue sunlight more than most other visible colours."),
    ("Why does ice float?",
     "Ice is less dense than liquid water, so it floats."),
]

title, fact = random.choice(facts)

script = f"{title} {fact}"

with open(f"{OUTPUT}/script.txt", "w") as file:
    file.write(script)

print("Video script created!")
print("Title:", title)
print("Script:", script)
