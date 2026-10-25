import sys

from glfw.GLFW import *
from OpenGL.GL import *
from OpenGL.GLU import *

BACKGROUND_COLOR = (0.5, 0.5, 0.5)
CARPET_COLOR = (1.0, 0.8, 0.2)

depth = 3


def startup():
    update_viewport(None, 400, 400)
    glClearColor(BACKGROUND_COLOR[0], BACKGROUND_COLOR[1], BACKGROUND_COLOR[2], 1.0)


def shutdown():
    pass


def rectangle(
    x: float, y: float, a: float, b: float, color: tuple[float, float, float]
):
    left_x = x - a / 2.0
    right_x = x + a / 2.0
    bottom_y = y + b / 2.0
    top_y = y - b / 2.0

    glBegin(GL_TRIANGLES)
    glColor3f(color[0], color[1], color[2])
    glVertex2f(left_x, top_y)
    glColor3f(color[1], color[2], color[0])
    glVertex2f(left_x, bottom_y)
    glColor3f(color[2], color[0], color[1])
    glVertex2f(right_x, bottom_y)
    glEnd()

    glBegin(GL_TRIANGLES)
    glColor3f(color[0], color[1], color[2])
    glVertex2f(left_x, top_y)
    glColor3f(color[1], color[2], color[0])
    glVertex2f(right_x, top_y)
    glColor3f(color[2], color[0], color[1])
    glVertex2f(right_x, bottom_y)
    glEnd()


def carpet_cutouts(x: float, y: float, a: float, b: float, level: int):
    if level <= 0:
        return

    # Cut out the middle cell of a 3x3 grid
    sub_a = a / 3.0
    sub_b = b / 3.0
    rectangle(x, y, sub_a, sub_b, BACKGROUND_COLOR)

    # Repeat for the 8 surrounding cells with smaller sides
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            if i == 0 and j == 0:
                continue
            carpet_cutouts(x + i * sub_a, y + j * sub_b, sub_a, sub_b, level - 1)


def sierpinski_carpet(x: float, y: float, a: float, b: float, level: int):
    rectangle(x, y, a, b, CARPET_COLOR)
    carpet_cutouts(x, y, a, b, level)


def render(time):
    glClear(GL_COLOR_BUFFER_BIT)

    sierpinski_carpet(0.0, 0.0, 180.0, 120.0, depth)

    glFlush()


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
    global depth
    if len(sys.argv) > 1:
        depth = int(sys.argv[1])

    if not glfwInit():
        sys.exit(-1)

    window = glfwCreateWindow(400, 400, __file__, None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)

    glfwMakeContextCurrent(window)
    glfwSetFramebufferSizeCallback(window, update_viewport)
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
