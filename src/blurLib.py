def box_blur(
    value_matrix: list, repetitions: int = 1, total: int = 1
) -> list:  # Total is just for UX and technically unnecessary. Total should always == repetitions except in recursions.
    """A recursive blurring function that averages a 3x3 kernel around each point."""
    # Border pixels have seperate handling!
    # This is more optimised than try;catch, though significantly more tedious
    blur = []

    row = []
    # Handle top-left corner
    # - - -
    # - x x
    # - x x
    value = int(value_matrix[0][0])  # centre
    value += value_matrix[1][0]  # down
    value += value_matrix[0][1]  # right
    value += value_matrix[1][1]  # down-right
    value /= 4
    row.append(value)
    # handle first row
    # - - -
    # x x x
    # x x x
    for x in range(
        1, len(value_matrix[0]) - 1
    ):  # skip the first and stop before the last, hence -1
        value = int(value_matrix[0][x])  # centre
        value += value_matrix[0][x - 1]  # left
        value += value_matrix[1][x]  # down
        value += value_matrix[0][x + 1]  # right
        value += value_matrix[1][x - 1]  # down-left
        value += value_matrix[1][x + 1]  # down-right
        value /= 6
        row.append(value)

    # handle top-right corner
    # - - -
    # x x -
    # x x -

    value = int(value_matrix[0][-1])  # centre
    value += value_matrix[1][-1]  # down
    value += value_matrix[0][-2]  # left
    value += value_matrix[1][-2]  # down-left
    value /= 4
    row.append(value)

    blur.append(row)

    for y in range(
        1, len(value_matrix) - 1
    ):  # subtract 1, because seperate handling for first and final rows
        line = []

        # handle left border pixel
        # - x x
        # - x x
        # - x x
        value = int(value_matrix[y][0])  # centre
        value += value_matrix[y - 1][0]  # up
        value += value_matrix[y + 1][0]  # down
        value += value_matrix[y][1]  # right
        value += value_matrix[y - 1][1]  # up-right
        value += value_matrix[y + 1][1]  # down-right
        value /= 6

        line.append(value)

        # Loop beginning from proceeding right border (index 1); end preceeding left border
        for x in range(1, len(value_matrix[y]) - 1):
            # handle non-border
            # x x x
            # x x x
            # x x x
            value = int(value_matrix[y][x])  # centre

            value += value_matrix[y - 1][x]  # up

            value += value_matrix[y][x - 1]  # left

            value += value_matrix[y + 1][x]  # down

            value += value_matrix[y][x + 1]  # right

            value += value_matrix[y - 1][x - 1]  # up-left

            value += value_matrix[y + 1][x - 1]  # down-left

            value += value_matrix[y + 1][x + 1]  # down-right

            value += value_matrix[y - 1][x + 1]  # up-right

            value /= 9

            line.append(value)

        # handle right border pixel
        # x x -
        # x x -
        # x x -
        value = int(value_matrix[y][-1])  # centre
        value += value_matrix[y - 1][-1]  # up
        value += value_matrix[y + 1][-1]  # down
        value += value_matrix[y][-2]  # left
        value += value_matrix[y - 1][-2]  # up-left
        value += value_matrix[y + 1][-2]  # down-left
        value /= 6

        line.append(value)

        blur.append(line)  # end of loop

    row = []
    # Handle bottom-left corner
    # - x x
    # - x x
    # - - -
    value = int(value_matrix[-1][0])  # centre
    value += value_matrix[-2][0]  # up
    value += value_matrix[-1][1]  # right
    value += value_matrix[-2][1]  # up-right
    value /= 4
    row.append(value)
    # Handle final row
    # x x x
    # x x x
    # - - -
    for x in range(
        1, len(value_matrix[0]) - 1
    ):  # skip the first and stop before the last, hence -1
        value = int(value_matrix[-1][x])  # centre
        value += value_matrix[-1][x - 1]  # left
        value += value_matrix[-2][x]  # up
        value += value_matrix[-1][x + 1]  # right
        value += value_matrix[-2][x - 1]  # up-left
        value += value_matrix[-2][x + 1]  # up-right
        value /= 6
        row.append(value)

    # Handle bottom-right corner
    # x x -
    # x x -
    # - - -

    value = int(value_matrix[-1][-1])  # centre
    value += value_matrix[-2][-1]  # up
    value += value_matrix[-1][-2]  # left
    value += value_matrix[-2][-2]  # up-left
    value /= 4
    row.append(value)

    blur.append(row)
    # Recursion logic
    if repetitions <= 1:
        return blur
    else:
        repetitions -= 1
        if not repetitions % 0x10:
            print(f"{total - repetitions}/{total}")
        return box_blur(blur, repetitions, total)
