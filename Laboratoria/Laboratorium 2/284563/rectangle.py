import sys

from glfw.GLFW import *
from OpenGL.GL import *
from OpenGL.GLU import *


def startup():
    update_viewport(None, 400, 400)
    glClearColor(0.5, 0.5, 0.5, 1.0)


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


def center_indicator(size: float):
    x = 0.0
    y = 0.0
    ratio = 10.0
    color = (1.0, 0.1, 0.0)
    rectangle(x, y, size * ratio, size, color)
    rectangle(x, y, size, size * ratio, color)


def render(time):
    glClear(GL_COLOR_BUFFER_BIT)

    rectangle(0.0, 0.0, 200.0, 100.0, (1.0, 0.0, 0.0))
    rectangle(-100.0, -50.0, 200.0, 100.0, (0.0, 1.0, 0.0))
    rectangle(100.0, 50.0, 200.0, 100.0, (0.0, 0.0, 1.0))
    center_indicator(2.0)

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
