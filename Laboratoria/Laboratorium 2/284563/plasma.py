import argparse
import colorsys
import math
import random
import sys

from glfw.GLFW import *
from OpenGL.GL import *
from OpenGL.GLU import *

COLOR_MODES = ("mono", "rgb", "palette")
WEIGHT_FUNCTIONS = ("power", "gauss", "linear", "constant")
DISTRIBUTIONS = ("uniform", "triangular")

# Reference size of the square used as the x axis of the weighting functions
# (matches the 0..256 range of the plots in the assignment).
REFERENCE_SIZE = 256.0

params = None
display_list = None


def parse_args():
    parser = argparse.ArgumentParser(description="Plasma fractal (OpenGL)")
    parser.add_argument("-n", type=int, default=7, help="grid is (2^n + 1) x (2^n + 1)")
    parser.add_argument("--mode", choices=COLOR_MODES, default="mono")
    parser.add_argument("--weight", choices=WEIGHT_FUNCTIONS, default="power")
    parser.add_argument(
        "--sigma", type=float, default=100.0, help="width of the gauss/linear weighting"
    )
    parser.add_argument(
        "--roughness",
        type=float,
        default=0.75,
        help="exponent H of the power weighting (smaller = rougher)",
    )
    parser.add_argument("--distribution", choices=DISTRIBUTIONS, default="uniform")
    parser.add_argument(
        "--levels", type=int, default=16, help="number of discrete color levels"
    )
    parser.add_argument("--size", type=float, default=180.0, help="image side length")
    parser.add_argument("--seed", type=int, default=None)
    return parser.parse_args()


# --- random color generation ------------------------------------------------


def random_level():
    """Draw a value in [0, 1] from a discrete distribution with `levels` values."""
    k = params.levels - 1
    if params.distribution == "uniform":
        i = random.randint(0, k)
    else:
        # Sum of two uniform variables -> discrete triangular distribution
        i = (random.randint(0, k) + random.randint(0, k)) // 2
    return i / k


def random_color():
    if params.mode == "rgb":
        return (random_level(), random_level(), random_level())
    v = random_level()
    return (v, v, v)


# --- weighting functions ----------------------------------------------------


def weight(x: float) -> float:
    """W(x): 0.5 for small squares, falling towards 0 for big ones."""
    if params.weight == "power":
        # Random part shrinks like (x/256)^H - detail on every scale
        return 0.5 * (1.0 - min(x / REFERENCE_SIZE, 1.0) ** params.roughness)
    if params.weight == "gauss":
        return 0.5 * math.exp(-((x / params.sigma) ** 2))
    if params.weight == "linear":
        return 0.5 * max(0.0, 1.0 - x / (2.0 * params.sigma))
    # Same weight on every scale - noisy, no smooth transitions
    return 0.4


def weight_center(x: float) -> float:
    """Wc(x): same shape as W(x) but with maximum 0.25."""
    return weight(x) / 2.0


def mix_edge(c_rand, c1, c2, w):
    return tuple((1.0 - 2.0 * w) * r + w * a + w * b for r, a, b in zip(c_rand, c1, c2))


def mix_center(c_rand, corners, w):
    return tuple(
        (1.0 - 4.0 * w) * c_rand[i] + w * sum(c[i] for c in corners) for i in range(3)
    )


# --- plasma generation ------------------------------------------------------


def generate_plasma(n: int):
    side = 2**n
    grid = [[None] * (side + 1) for _ in range(side + 1)]

    # Step 1: random colors in the corners
    for i, j in ((0, 0), (0, side), (side, 0), (side, side)):
        grid[i][j] = random_color()

    pixel = REFERENCE_SIZE / side

    def edge_point(i, j, a, b, w):
        # Points on shared edges are computed only once to avoid seams
        if grid[i][j] is None:
            grid[i][j] = mix_edge(random_color(), a, b, w)

    def subdivide(i0, j0, size):
        # Step 2: five new points - edge midpoints and the center
        if size < 2:
            return
        half = size // 2
        i1, j1 = i0 + size, j0 + size
        im, jm = i0 + half, j0 + half
        c1, c2 = grid[i0][j0], grid[i0][j1]
        c3, c4 = grid[i1][j0], grid[i1][j1]

        x = size * pixel
        w = weight(x)
        edge_point(i0, jm, c1, c2, w)  # c12
        edge_point(i1, jm, c3, c4, w)  # c34
        edge_point(im, j0, c1, c3, w)  # c13
        edge_point(im, j1, c2, c4, w)  # c24
        grid[im][jm] = mix_center(random_color(), (c1, c2, c3, c4), weight_center(x))

        # Step 3: repeat for the four new squares
        subdivide(i0, j0, half)
        subdivide(i0, jm, half)
        subdivide(im, j0, half)
        subdivide(im, jm, half)

    subdivide(0, 0, side)
    return normalize(grid)


def normalize(grid, clip=0.02):
    """Stretch every channel to [0, 1] (averaging kills contrast).

    The range is taken between percentiles, so a few extreme points
    (e.g. the random corners) do not keep the rest of the image gray.
    """
    lows, spans = [], []
    for k in range(3):
        values = sorted(c[k] for row in grid for c in row)
        low = values[int(clip * (len(values) - 1))]
        high = values[int((1.0 - clip) * (len(values) - 1))]
        lows.append(low)
        spans.append(max(high - low, 1e-9))
    return [
        [
            tuple(min(max((c[k] - lows[k]) / spans[k], 0.0), 1.0) for k in range(3))
            for c in row
        ]
        for row in grid
    ]


def to_display_color(c):
    if params.mode == "palette":
        # Map gray level to a hue gradient
        v = c[0]
        return colorsys.hsv_to_rgb(0.75 * (1.0 - v), 0.85, 0.35 + 0.65 * v)
    return c


# --- OpenGL -----------------------------------------------------------------


def build_display_list():
    global display_list
    if display_list is None:
        display_list = glGenLists(1)

    grid = generate_plasma(params.n)
    side = len(grid) - 1
    cell = params.size / side
    left = -params.size / 2.0
    top = params.size / 2.0

    colors = [[to_display_color(c) for c in row] for row in grid]

    glNewList(display_list, GL_COMPILE)
    for i in range(side):
        y0 = top - i * cell
        y1 = y0 - cell
        # One strip per grid row, colors interpolated between grid points
        glBegin(GL_TRIANGLE_STRIP)
        for j in range(side + 1):
            x = left + j * cell
            glColor3f(*colors[i][j])
            glVertex2f(x, y0)
            glColor3f(*colors[i + 1][j])
            glVertex2f(x, y1)
        glEnd()
    glEndList()

    print(
        f"n={params.n} mode={params.mode} weight={params.weight} "
        f"roughness={params.roughness:.2f} sigma={params.sigma:.0f} "
        f"distribution={params.distribution} "
        f"levels={params.levels}"
    )


def startup():
    update_viewport(None, 400, 400)
    glClearColor(0.5, 0.5, 0.5, 1.0)
    build_display_list()


def shutdown():
    if display_list is not None:
        glDeleteLists(display_list, 1)


def render(time):
    glClear(GL_COLOR_BUFFER_BIT)
    glCallList(display_list)
    glFlush()


def cycle(options, current):
    return options[(options.index(current) + 1) % len(options)]


def keyboard_key_callback(window, key, scancode, action, mods):
    if action != GLFW_PRESS:
        return

    if key == GLFW_KEY_ESCAPE:
        glfwSetWindowShouldClose(window, GLFW_TRUE)
        return
    elif key in (GLFW_KEY_SPACE, GLFW_KEY_R):
        pass
    elif key == GLFW_KEY_C:
        params.mode = cycle(COLOR_MODES, params.mode)
    elif key == GLFW_KEY_W:
        params.weight = cycle(WEIGHT_FUNCTIONS, params.weight)
    elif key == GLFW_KEY_D:
        params.distribution = cycle(DISTRIBUTIONS, params.distribution)
    elif key == GLFW_KEY_UP:
        params.n = min(params.n + 1, 10)
    elif key == GLFW_KEY_DOWN:
        params.n = max(params.n - 1, 1)
    elif key == GLFW_KEY_RIGHT_BRACKET:
        if params.weight == "power":
            params.roughness = min(params.roughness + 0.05, 2.0)
        else:
            params.sigma += 20.0
    elif key == GLFW_KEY_LEFT_BRACKET:
        if params.weight == "power":
            params.roughness = max(params.roughness - 0.05, 0.05)
        else:
            params.sigma = max(params.sigma - 20.0, 10.0)
    elif key == GLFW_KEY_EQUAL:
        params.levels = min(params.levels * 2, 256)
    elif key == GLFW_KEY_MINUS:
        params.levels = max(params.levels // 2, 2)
    else:
        return

    build_display_list()


def update_viewport(window, width, height):
    if width == 0:
        width = 1
    if height == 0:
        height = 1
    aspect_ratio = width / height

    glMatrixMode(GL_PROJECTION)
    glViewport(0, 0, width, height)
    glLoadIdentity()

    if width <= height:
        glOrtho(-100.0, 100.0, -100.0 / aspect_ratio, 100.0 / aspect_ratio, 1.0, -1.0)
    else:
        glOrtho(-100.0 * aspect_ratio, 100.0 * aspect_ratio, -100.0, 100.0, 1.0, -1.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def main():
    global params
    params = parse_args()
    params.levels = max(params.levels, 2)
    if params.seed is not None:
        random.seed(params.seed)

    print(
        "Keys: SPACE/R regenerate, C color mode, W weight function, "
        "D distribution, UP/DOWN n, [ ] roughness/sigma, -/= levels, ESC quit"
    )

    if not glfwInit():
        sys.exit(-1)

    window = glfwCreateWindow(400, 400, __file__, None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)

    glfwMakeContextCurrent(window)
    glfwSetFramebufferSizeCallback(window, update_viewport)
    glfwSetKeyCallback(window, keyboard_key_callback)
    glfwSwapInterval(1)

    startup()
    while not glfwWindowShouldClose(window):
        render(glfwGetTime())
        glfwSwapBuffers(window)
        glfwPollEvents()
    shutdown()

    glfwTerminate()


if __name__ == "__main__":
    main()
