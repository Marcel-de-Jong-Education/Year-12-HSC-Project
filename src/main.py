"""CLI tool for generating noise"""

# ----------------Dependencies---------------- #

import sys
from random import randint
from enum import StrEnum

import inquirer
from time import time
from PIL import Image
from math import log
from numpy import (
    array,
    zeros,
    zeros_like,
    stack,
    uint8
    )

# ----------------Definitions---------------- #


class Noise(StrEnum): # Not a typical python class, enums are special
    """Enumerates noise types to ensure type-safety."""
    WHITE = "WHITE"
    BLOBBY = "BLOBBY"
    PERLIN = "PERLIN"




def box_blur(value_matrix: list, repetitions: int = 1, total: int = 1) -> list: # Total is just for UX and technically unnecessary. Total should always == repetitions except in recursions.
    """A recursive blurring function that averages a 3x3 kernel around each point."""
    # Border pixels have seperate handling!
    # This is more optimised than try;catch, though significantly more tedious
    blur = []

    row = []
    # Handle top-left corner
    # - - -
    # - x x
    # - x x
    value = int(value_matrix[0][0]) # centre
    value += value_matrix[1][0] # down
    value += value_matrix[0][1] # right
    value += value_matrix[1][1] # down-right
    value /= 4
    row.append(value)
    # handle first row
    # - - -
    # x x x
    # x x x
    for x in range(1, len(value_matrix[0])-1): # skip the first and stop before the last, hence -1
            value = int(value_matrix[0][x]) # centre
            value += value_matrix[0][x-1] # left
            value += value_matrix[1][x] # down
            value += value_matrix[0][x+1] # right
            value += value_matrix[1][x-1] # down-left
            value += value_matrix[1][x+1] # down-right
            value /= 6
            row.append(value)

    # handle top-right corner
    # - - -
    # x x -
    # x x -

    value = int(value_matrix[0][-1]) # centre
    value += value_matrix[1][-1] # down
    value += value_matrix[0][-2] # left
    value += value_matrix[1][-2] # down-left
    value /= 4
    row.append(value)

    blur.append(row)

    for y in range(1, len(value_matrix)-1): # subtract 1, because seperate handling for first and final rows
        line = []

        # handle left border pixel
        # - x x
        # - x x
        # - x x
        value = int(value_matrix[y][0]) # centre
        value += value_matrix[y-1][0] # up
        value += value_matrix[y+1][0] # down
        value += value_matrix[y][1] # right
        value += value_matrix[y-1][1] # up-right
        value += value_matrix[y+1][1] # down-right
        value /= 6

        line.append(value)

        # Loop beginning from proceeding right border (index 1); end preceeding left border
        for x in range(1, len(value_matrix[y]) - 1):
            # handle non-border
            # x x x
            # x x x
            # x x x
            value = int(value_matrix[y][x]) # centre

            value += value_matrix[y-1][x] # up

            value += value_matrix[y][x-1] # left

            value += value_matrix[y+1][x] # down

            value += value_matrix[y][x+1] # right

            value += value_matrix[y-1][x-1] # up-left

            value += value_matrix[y+1][x-1] # down-left

            value += value_matrix[y+1][x+1] # down-right

            value += value_matrix[y-1][x+1] # up-right


            value /= 9

            line.append(value)

        # handle right border pixel
        # x x -
        # x x -
        # x x -
        value = int(value_matrix[y][-1]) # centre
        value += value_matrix[y-1][-1] # up
        value += value_matrix[y+1][-1] # down
        value += value_matrix[y][-2] # left
        value += value_matrix[y-1][-2] # up-left
        value += value_matrix[y+1][-2] # down-left
        value /= 6

        line.append(value)

        blur.append(line) # end of loop

    row = []
    # Handle bottom-left corner
    # - x x
    # - x x
    # - - -
    value = int(value_matrix[-1][0]) # centre
    value += value_matrix[-2][0] # up
    value += value_matrix[-1][1] # right
    value += value_matrix[-2][1] # up-right
    value /= 4
    row.append(value)
    # Handle final row
    # x x x
    # x x x
    # - - -
    for x in range(1, len(value_matrix[0])-1): # skip the first and stop before the last, hence -1
            value = int(value_matrix[-1][x]) # centre
            value += value_matrix[-1][x-1] # left
            value += value_matrix[-2][x] # up
            value += value_matrix[-1][x+1] # right
            value += value_matrix[-2][x-1] # up-left
            value += value_matrix[-2][x+1] # up-right
            value /= 6
            row.append(value)

    # Handle bottom-right corner
    # x x -
    # x x -
    # - - -

    value = int(value_matrix[-1][-1]) # centre
    value += value_matrix[-2][-1] # up
    value += value_matrix[-1][-2] # left
    value += value_matrix[-2][-2] # up-left
    value /= 4
    row.append(value)

    blur.append(row)
    # Recursion
    if repetitions <= 1:
        return blur
    else:
        repetitions -= 1
        if not repetitions % 0x10: print(f'{total - repetitions}/{total}')
        return box_blur(blur, repetitions, total)



def gaussian_blur(value_matrix: list) -> list: # TODO
    """Applies a gaussian blur."""
    result = []
    return result





def generate_noise(width: int, height: int, noise_type: StrEnum = Noise.WHITE, density_percent: float = 2.0, spread_distance: int = 2,) -> list:
    """Generates a 2D matrix of noise of a given type."""
    matrix = []

    match noise_type:
        case Noise.WHITE:
            for y in range(height):
                line = []

                for x in range(width):
                    line.append(randint(0x00, 0xFF))

                matrix.append(line)

            matrix = box_blur(matrix, 64, 64)
            return matrix


        case Noise.BLOBBY:

            origins = []

            for y in range(height):
                line = []

                for x in range(width):
                    if float(randint(1,100000))/1000 <= density_percent:
                        line.append(0xFF)
                        origins.append([x,y])
                    else:
                        line.append(0)

                matrix.append(line)

            # Spread noise

            for i in range(spread_distance):
                current_origins = list(origins) # Avoid TOCTOU
                origins = [] # prevent re-running on old points, massive optimisation
                for point in current_origins:
                    try:
                        matrix[point[1]-1][point[0]] = 0xFF # up
                        origins.append([point[0], point[1]-1])
                    except:
                        pass

                    try:
                        matrix[point[1]][point[0]-1] = 0xFF # left
                        origins.append([point[0]-1, point[1]])
                    except:
                        pass

                    try:
                        matrix[point[1]+1][point[0]] = 0xFF # down
                        origins.append([point[0], point[1]+1])
                    except:
                        pass

                    try:
                        matrix[point[1]][point[0]+1] = 0xFF # right
                        origins.append([point[0]+1, point[1]])
                    except:
                        pass

            # blur (log_2(256^2)-2)^2 times
            blur_count = int((log(width*height, 2)-2)**2)
            matrix = box_blur(value_matrix=matrix, repetitions=blur_count, total=blur_count) # ~1 second per 20 repetitions at 256x256

            return matrix

        case Noise.PERLIN:
            print('Perlin!')
            return matrix

        case _: # This should REALLY never run.
            print(f'Invalid type {noise_type}!')
            raise ValueError
            return matrix



def noise_octaves(noise: list, octaves: list = [8.0], strength: float = [1]) -> list: # TODO: fix
    """Adds octaves to noise."""

    # octaves should be number loosely based on what grid size they would standalone suit
    # e.g. 256x256 => [d=0.8, s=3], octave = log_2(256) = 8
    # therefore d(ensity) = octave / 10
    # s(pread) = log_2(octave)
    for octave in octaves:
        density = 1/octave/10
        print(f'd = {density}')
        spread = int(log(octave, 2))
        print(f's = {spread}')

        noise = array(noise, dtype=uint8)
        img = Image.fromarray(noise)
        img.show()

        noise = noise + array(generate_noise(
            len(noise), # width
            len(noise[0]), # height
            noise_type=Noise.BLOBBY,
            density_percent=density,
            spread_distance=spread
            ), dtype=uint8)



    return noise




def noise_to_text(value_matrix: list) -> str:
    """Converts a 2D matrix of integers into a text map with intensity-reflective colouring."""
    gradient_characters = ["██", "▓▓", "▒▒", "░░", "  "]
    output = "\n"

    for y in range(len(value_matrix)):

        for x in range(len(value_matrix[y])):
            if value_matrix[y][x] > 205:
                output += gradient_characters[0]
            elif value_matrix[y][x] > 155:
                output += gradient_characters[1]
            elif value_matrix[y][x] > 105:
                output += gradient_characters[2]
            elif value_matrix[y][x] > 55:
                output += gradient_characters[3]
            else:
                output += gradient_characters[4]

        output += '\n'

    return output


def noise_to_terrain(noise_matrix: list, sea_level: int = 196): # this made me hate myself so much why is documentation so painful to readddddd
    """Colours noise to look like terrain"""
    noise = array(noise_matrix, dtype=uint8)

    height, width = noise.shape
    terrain = zeros((height, width, 3), dtype=uint8)

    # masks
    deep_water = noise < sea_level - 8
    shallow_water = (noise >= sea_level - 8) & (noise < sea_level)
    beach = (noise >= sea_level) & (noise < sea_level + 4)
    grassland = (noise >= sea_level + 4) & (noise < sea_level + 13)
    forest = (noise >= sea_level + 13) #& (noise < sea_level + 23)
    #snow = noise >= sea_level + 23

    # actual colouring
    terrain[deep_water] = [0, 15, 127] # abyss
    terrain[shallow_water] = [0, 63, 127] # shallows
    terrain[beach] = [255, 191, 191] # beach
    terrain[grassland] = [31, 127, 31] # grass
    terrain[forest] = [15, 63, 15] # forest
    #terrain[snow] = [191, 191, 255] # snow

    return terrain



def interactive_selection() -> Noise:
    """Uses the inquirer module and user input to select an mode via the CLI"""
    question = [
        inquirer.List(
            "Noise Type",
            message="Select a noise type",
            choices=["White Noise", "Blobby Noise", "Perlin Noise"],
        )
    ]
    answer = inquirer.prompt(question)["Noise Type"]
    print(f"Selection: {answer}")
    match answer:
        case "White Noise":
            return Noise.WHITE

        case "Blobby Noise":
            return Noise.BLOBBY

        case "Perlin Noise":
            return Noise.PERLIN

        case _:
            raise ValueError("Script malfunction: Prompt returned an unexpected value.") # This line *should* never run



# ----------------Script---------------- #

def main() -> int:
    """Runs the script."""
    if 'y' in input('Developer mode?\n').lower():
        try:
            noise_selection = interactive_selection()
        except ValueError:
            return 1

        start = time()
        noise_map = generate_noise(
            width=0xFF,
            height=0xFF,
            noise_type=noise_selection,
            density_percent=0.8,
            spread_distance=3
            )
        end = time()
        print(f'Time to generate noise: {end-start}\n')

        if noise_selection == Noise.BLOBBY:
            #noise_map = noise_octaves(noise_map, [32.0, 1.2])

            if 'y' in input('Colourise to terrain? [y/N]\n').lower():
                terrain = noise_to_terrain(noise_matrix=noise_map, sea_level=24) # 0 <= sea_level <= 255
                img = Image.fromarray(terrain, mode="RGB")
            else:
                noise_map = array(noise_map, dtype=uint8)
                img = Image.fromarray(noise_map)

            img.show()
            return 0

        noise_map = array(noise_map, dtype=uint8)
        img = Image.fromarray(noise_map)
        img.show()

        return 0

    else: # Not developer mode
        questions = [
            inquirer.List(
                "Login or Genesis New User",
                choices = [
                    'New User',
                    ]

                )]



if __name__ == "__main__":
    sys.exit(main())


# benchmark: 11.52"
