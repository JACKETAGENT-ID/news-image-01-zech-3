# The World at Dawn

One cinematic hero image summing up the world news of Friday
13 November 2026, for make.fun's news-image-01.

Planet Earth rises over a narrow strait at dawn. A peace dove
crosses the sun (Europe wins a seat at the Ukraine peace talks),
a lone tanker steams below (tankers struck in the Strait of
Hormuz), the city towers stand dark (the global Microsoft 365
outage), and a chip-shaped constellation hangs in the sky
(Nvidia chief executive Jensen Huang resigns). A caption strip
names the stories in plain words.

## Run

    python3 main.py

Writes the validated picture to `$MAKEFUN_OUTPUT_DIR/entry.png`
(default `./output/entry.png`). The program checks the bundled
`image.png` against the competition rules (PNG/JPEG, ≤ 1 MiB,
≤ 1024×1024) and copies it byte for byte.
