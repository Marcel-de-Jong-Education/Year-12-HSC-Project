# Year 12 HSC Project
## Description
This is an interactive CLI (Command Line Interface) tool for generating [visual noise](https://w.wiki/HpbU). 
It can generate 3 types of noise:
### White Noise
White Noise is a type of noise where the image consists of random, chaotic greyscale values from white to black.
### Blobby Noise
Blobby Noise is an algorithm of my own devising which produces randomly distributed blobs of noise. 
The algorithm works by:
1. Randomly selecting a handful of points and setting them to be white (RGB(0xFF, 0xFF, 0xFF))
2. Expanding the white points into parallelogrammes several pixels across.
3. Repeatedly applying a 3x3 [box-blur](https://w.wiki/Hpci).

It is very conceptually simple, but produces decent results.
### Perlin Noise
Not implemented yet.
## Usage
From your terminal or terminal-emulator, enter the src directory.
```bash
cd year-12-second-term-project/src
```
Then, run 
`uv run main.py`.

Use Up and Down arrow keys to select options as they appear.
