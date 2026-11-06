#!/usr/bin/env python3
import sys

import numpy
from glfw.GLFW import *
from OpenGL.GL import *
from OpenGL.GLU import *

N = 30
R = 4.0
r = 1.5


def torus_vertices(n: int) -> numpy.ndarray:
    u = numpy.linspace(0.0, 1.0, n)
    v = numpy.linspace(0.0, 1.0, n)
    tab = numpy.zeros((n, n, 3))

    for i in range(n):
        for j in range(n):
            ring = R + r * numpy.cos(2 * numpy.pi * v[j])
            tab[i][j][0] = ring * numpy.cos(2 * numpy.pi * u[i])
            tab[i][j][1] = r * numpy.sin(2 * numpy.pi * v[j])
            tab[i][j][2] = ring * numpy.sin(2 * numpy.pi * u[i])

    return tab


vertices = torus_vertices(N)
colors = numpy.random.default_rng().random((N, N, 3))

# Both parameters wrap around: u = 1 lies on u = 0 and v = 1 lies on v = 0.
colors[N - 1, :] = colors[0, :]
colors[:, N - 1] = colors[:, 0]


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


def torus():
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
    torus()

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
