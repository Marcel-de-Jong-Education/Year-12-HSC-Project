"""CLI tool for generating noise textures"""

# ----------------Dependencies---------------- #

# System modules
import sys
from random import randint
from enum import StrEnum
import json

# Third-party modules
import inquirer
from time import time
from PIL import Image
from math import log
from numpy import array, zeros, uint8
from pathlib import Path

# Modules by this project
from blurLib import box_blur

# ----------------Definitions---------------- #

# Identify the working directory
script_dir = Path(__file__).resolve().parent
# Determine the path to account data
accounts_file = script_dir / "accounts.json"
try:
    with accounts_file.open("r") as f:
        ACCOUNTS = json.load(f)
except (
    FileNotFoundError,
    json.JSONDecodeError,
):  # in case the file is missing or malformed
    print("Account data missing or corrupted!")
    ACCOUNTS = {}


def save_accounts() -> None:
    """Saves user data to accounts.json."""
    with open(accounts_file, "w") as f:
        json.dump(ACCOUNTS, f, indent=4)


class Noise(StrEnum):  # Not a typical python class; enums are special
    """Enumerates noise types to ensure type-safety."""

    WHITE = "WHITE"
    BLOBBY = "BLOBBY"


def generate_noise(
    width: int,
    height: int,
    noise_type: StrEnum = Noise.WHITE,
    density_percent: float = 2.0,
    spread_distance: int = 2,
) -> list:
    """Generates a 2D matrix of noise of a given type."""
    matrix = []

    match noise_type:
        case Noise.WHITE:
            for y in range(height):
                line = []

                for x in range(width):
                    line.append(randint(0x00, 0xFF))

                matrix.append(line)

            return matrix

        case Noise.BLOBBY:
            origins = []

            for y in range(height):
                line = []

                for x in range(width):
                    if float(randint(1, 100000)) / 1000 <= density_percent:
                        line.append(0xFF)
                        origins.append([x, y])
                    else:
                        line.append(0)

                matrix.append(line)

            # Spread noise

            for i in range(spread_distance):
                current_origins = list(origins)  # Avoid TOCTOU
                origins = []  # prevent re-running on old points; massive optimisation
                for point in current_origins:
                    try:
                        matrix[point[1] - 1][point[0]] = 0xFF  # up
                        origins.append([point[0], point[1] - 1])
                    except IndexError:
                        pass

                    try:
                        matrix[point[1]][point[0] - 1] = 0xFF  # left
                        origins.append([point[0] - 1, point[1]])
                    except IndexError:
                        pass

                    try:
                        matrix[point[1] + 1][point[0]] = 0xFF  # down
                        origins.append([point[0], point[1] + 1])
                    except IndexError:
                        pass

                    try:
                        matrix[point[1]][point[0] + 1] = 0xFF  # right
                        origins.append([point[0] + 1, point[1]])
                    except IndexError:
                        pass

            # blur (log_2(256^2)-2)^2 times
            # CODE REVIEWERS: If you have a LaTeX renderer on hand, paste the following into it:
            # \displaystyle\left[log_2\left(256^2\right)-2\right]^2
            # This formula automagically optimises the blur count for the desired resolution!
            blur_count = int((log(width * height, 2) - 2) ** 2)
            matrix = box_blur(
                value_matrix=matrix, repetitions=blur_count, total=blur_count
            )  # ~1 second per 20 repetitions at 256x256

            return matrix

        case _:  # This should REALLY never run.
            print(f"Invalid type {noise_type}!")
            raise ValueError
            return matrix


def noise_to_terrain(
    noise_matrix: list, sea_level: int = 196
):  # this made me hate myself so much why is documentation so painful to readddddd
    """Colours noise to look like terrain"""
    noise = array(noise_matrix, dtype=uint8)

    height, width = noise.shape
    terrain = zeros((height, width, 3), dtype=uint8)

    # masks
    deep_water = noise < sea_level - 8
    shallow_water = (noise >= sea_level - 8) & (noise < sea_level)
    beach = (noise >= sea_level) & (noise < sea_level + 4)
    grassland = (noise >= sea_level + 4) & (noise < sea_level + 13)
    forest = noise >= sea_level + 13  # & (noise < sea_level + 23)
    # snow = noise >= sea_level + 23

    # actual colouring
    terrain[deep_water] = [0, 15, 127]  # abyss
    terrain[shallow_water] = [0, 63, 127]  # shallows
    terrain[beach] = [255, 191, 191]  # beach
    terrain[grassland] = [31, 127, 31]  # grass
    terrain[forest] = [15, 63, 15]  # forest
    # terrain[snow] = [191, 191, 255] # snow

    return terrain


def interactive_selection() -> Noise:
    """Uses the inquirer module and user input to select an mode via the CLI"""
    question = [
        inquirer.List(
            "Noise Type",
            message="Select a noise type",
            choices=["White Noise", "Blobby Noise"],
        )
    ]
    answer = inquirer.prompt(question)["Noise Type"]
    print(f"Selection: {answer}")
    match answer:
        case "White Noise":
            return Noise.WHITE

        case "Blobby Noise":
            return Noise.BLOBBY

        case _:
            raise ValueError(
                "Script malfunction: Prompt returned an unexpected value."
            )  # This line *should* never run


def find_user_data(user: str) -> list:
    """Returns a list of all the files a user has."""
    global script_dir

    # Point to the user_data folder
    user_data_dir = script_dir / "user_data"

    # List of target folders you want to check
    target_dirs = list(ACCOUNTS)

    # Ensure all user account directories exist
    for directory in target_dirs:
        # Combine paths: script_dir / user_data / target_folder
        dir_path = user_data_dir / directory

        if dir_path.is_dir():
            # print(f"Detected user data directory for {directory}!")
            pass
        else:
            print(f"Missing: {directory} does not exist")
            print(f"Creating directory {directory}...")

            # parents=True also creates parent dir if missing
            # exist_ok=True prevents error in case of live tampering
            dir_path.mkdir(parents=True, exist_ok=True)
            print("Directory created!")

    user_path = user_data_dir / user
    # User data is just images
    # Safely return that specific user's files
    if user_path.is_dir():
        return [item.name for item in user_path.iterdir() if item.is_file()]

    return []  # Return empty list if the requested user doesn't exist


# ----------------Script---------------- #


def main() -> int:
    """Runs the script."""
    if "y" in input("Developer mode?\n").lower():
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
            spread_distance=3,
        )
        end = time()
        print(f"Time to generate noise: {end - start}\n")

        if noise_selection == Noise.BLOBBY:
            if "y" in input("Colourise to terrain? [y/N]\n").lower():
                terrain = noise_to_terrain(
                    noise_matrix=noise_map, sea_level=24
                )  # 0 <= sea_level <= 255

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

    else:  # Not developer mode
        # Initialise user variable in high scope
        user = None

        questions = [
            inquirer.List(
                "Login or Genesis New User",
                message="Select",
                choices=["New User"]
                + list(
                    ACCOUNTS
                ),  # did you know python is the best progamming language ever written?
            )
        ]
        answer = inquirer.prompt(questions)["Login or Genesis New User"]
        print(f"Selection: {answer}")
        if answer != "New User":
            while True:
                password_attempt = input("Please enter the password:\n❯ ")
                if password_attempt == ACCOUNTS[answer]:
                    user = answer
                    print("Logued in!")
                    break
                else:
                    print("Incorrect password.\n")
        else:
            while True:
                new_username = input("Create a username:\n❯ ")
                if new_username.isalnum():
                    break
                print("Alphanumeric names only.")
            while True:
                new_password = input("Create a password:\n❯ ")
                if new_password.isalnum():
                    break
                print("Alphanumeric passwords only.")
            ACCOUNTS[new_username] = new_password
            save_accounts()
            # set correct user for session
            user = new_username

        # check if user has images saved
        print(find_user_data(user))
        # check if user wants to create a new image, or work with an existing image
        questions = [
            inquirer.List(
                "Action",
                message="Select",
                choices=["Create New Image.", "Existing Image."],
            )
        ]
        answer0 = inquirer.prompt(questions)["Action"]
        print(f"Selection: {answer0}")

        if answer0 == "Create New Image.":
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
                spread_distance=3,
            )
            end = time()

            print(f"Time to generate noise: {end - start}\n")

            # define img in wider scope
            img = None
            if noise_selection == Noise.BLOBBY:
                if "y" in input("Colourise to terrain? [y/N]\n").lower():
                    terrain = noise_to_terrain(
                        noise_matrix=noise_map, sea_level=24
                    )  # 0 <= sea_level <= 255

                    img = Image.fromarray(terrain, mode="RGB")
                else:
                    noise_map = array(noise_map, dtype=uint8)
                    img = Image.fromarray(noise_map)

            elif noise_selection == Noise.WHITE:
                noise_map = array(noise_map, dtype=uint8)
                img = Image.fromarray(noise_map)

            else:
                raise ValueError

            img.show()

            # Check if user wants to save image
            questions = [
                inquirer.List(
                    "Save?",
                    message="Select",
                    choices=["Save image.", "Quit."],
                )
            ]
            answer1 = inquirer.prompt(questions)["Save?"]

            if answer1 == "Quit.":
                return 0
            elif answer1 == "Save image.":
                # save the image
                while True:
                    filename = input("Enter file name:\n❯ ") + ".png"
                    if filename.isalnum():
                        break
                    print("Alphanumeric names only.")

                save_dir = Path("user_data/" + user)
                try:
                    img.save(save_dir / filename)
                except OSError:
                    print(f"Failed to save {filename}.")

                print(f"Saved {filename} to {save_dir} successfully!")
            else:
                # malformed input
                raise ValueError

        elif answer0 == "Existing Image.":
            # make an inquirer selection where each option is a file in the user's dir
            user_files = find_user_data(user)
            # check user has files
            if len(user_files) < 1:
                print("Error 404: File not found.")
                return 0

            questions = [
                inquirer.List(
                    "userfiles",
                    message="Select a file.",
                    choices=user_files,
                )
            ]
            answer2 = inquirer.prompt(questions)["userfiles"]
            image_path = script_dir / "user_data" / user / answer2
            img = Image.open(image_path)
            img.show()

        else:
            # malformed input
            raise ValueError
            return 0

    #


if __name__ == "__main__":
    sys.exit(main())
