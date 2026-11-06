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
    glBegin(GL_TRIANGLES)
    for i in range(N - 1):
        for j in range(N - 1):
            for a, b in ((i, j), (i + 1, j), (i, j + 1)):
                glColor3fv(colors[a][b])
                glVertex3fv(vertices[a][b])

            for a, b in ((i + 1, j), (i + 1, j + 1), (i, j + 1)):
                glColor3fv(colors[a][b])
                glVertex3fv(vertices[a][b])
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
