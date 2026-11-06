#!/usr/bin/env python3
import sys

import numpy
from glfw.GLFW import *
from OpenGL.GL import *
from OpenGL.GLU import *

N = 30


def egg_vertices(n: int) -> numpy.ndarray:
    u = numpy.linspace(0.0, 1.0, n)
    v = numpy.linspace(0.0, 1.0, n)
    tab = numpy.zeros((n, n, 3))

    for i in range(n):
        profile = -90 * u[i] ** 5 + 225 * u[i] ** 4 - 270 * u[i] ** 3 + 180 * u[i] ** 2 - 45 * u[i]
        y = 160 * u[i] ** 4 - 320 * u[i] ** 3 + 160 * u[i] ** 2 - 5
        for j in range(n):
            tab[i][j][0] = profile * numpy.cos(numpy.pi * v[j])
            tab[i][j][1] = y
            tab[i][j][2] = profile * numpy.sin(numpy.pi * v[j])

    return tab


vertices = egg_vertices(N)
colors = numpy.random.default_rng().random((N, N, 3))

# Vertices that coincide in 3D must share a colour, otherwise seams show up.
# Rows u = 0 and u = 1 collapse into the bottom pole (and u = 0.5 into the top one for odd N).
colors[0, :] = colors[0][0]
colors[N - 1, :] = colors[0][0]
if N % 2:
    colors[N // 2, :] = colors[N // 2][0]
# Edge v = 1 lies on edge v = 0, mirrored in u.
for i in range(N):
    colors[i][N - 1] = colors[N - 1 - i][0]


def startup():
    update_viewport(None, 400, 400)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)


def shutdown():
    pass


def axes():
    glBegin(GL_LINES)

    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-5.0, 0.0, 0.0)
    glVertex3f(5.0, 0.0, 0.0)

    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, -5.0, 0.0)
    glVertex3f(0.0, 5.0, 0.0)

    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, -5.0)
    glVertex3f(0.0, 0.0, 5.0)

    glEnd()


def spin(angle):
    glRotatef(angle, 1.0, 0.0, 0.0)
    glRotatef(angle, 0.0, 1.0, 0.0)
    glRotatef(angle, 0.0, 0.0, 1.0)


def egg():
    for i in range(N - 1):
        glBegin(GL_TRIANGLE_STRIP)
        for j in range(N):
            glColor3fv(colors[i][j])
            glVertex3fv(vertices[i][j])
            glColor3fv(colors[i + 1][j])
            glVertex3fv(vertices[i + 1][j])
        glEnd()


def render(time):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    axes()
    spin(time * 180 / numpy.pi)
    egg()

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
        glOrtho(-7.5, 7.5, -7.5 / aspect_ratio, 7.5 / aspect_ratio, 7.5, -7.5)
    else:
        glOrtho(-7.5 * aspect_ratio, 7.5 * aspect_ratio, -7.5, 7.5, 7.5, -7.5)

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
