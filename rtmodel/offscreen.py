from OpenGL.GL import *
from OpenGL.GL.framebufferobjects import *
import numpy as np
import cv
import camera
from contextlib import contextmanager


if not 'initialized' in globals():
    initialized = False


def initialize():
    global initialized
    if initialized:
        return

    global fbo
    global rb, rbc, rbs

    fbo = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, fbo)

    rb,rbc = glGenRenderbuffers(2)
    glBindRenderbuffer(GL_RENDERBUFFER, rb)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, 640, 480)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER,
                              GL_DEPTH_ATTACHMENT,
                              GL_RENDERBUFFER, rb)

    glBindRenderbuffer(GL_RENDERBUFFER, rbc)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_RGB8, 640, 480)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER,
                              GL_COLOR_ATTACHMENT0,
                              GL_RENDERBUFFER, rbc)

    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    initialized = True


@contextmanager
def render(rect=((0,0),(640,480))):
    initialize()
    glBindFramebuffer(GL_FRAMEBUFFER, fbo);

    (L,T),(R,B) = rect
    glViewport(0, 0, 640, 480)
    glClearColor(0,0,0,0)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def read():
        readpixels = glReadPixels(L, T, R-L, B-T, GL_DEPTH_COMPONENT, GL_FLOAT)
        readpixelsA = glReadPixels(L, T, R-L, B-T, GL_RGBA, GL_UNSIGNED_BYTE,
                                   outputType='array')
        depth = np.empty((480,640),dtype='f')
        depth = .1 / np.nan_to_num(readpixels.reshape((480,640)))
        color = readpixelsA.reshape((480,640,4))
        return depth, color

    try:
        yield read

    finally:
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
