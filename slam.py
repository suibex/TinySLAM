

"""
    Zero Knowledge SLAM implementation in Python3
        Ok i'm really bad at this and idk if this is right thing to do.
        @author: nitrodegen
        @date: 9 July 2022.
"""
import cv2
import numpy as np
import os,io,sys
import sdl2
from multiprocessing import Process,Manager,Value,Array,Queue,Pipe
from math import * 
import pygame
from pygame.locals import *
import math
import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from threading import Thread
import random


"""
What is SLAM used for?

We use slam to find where we are in the enviorment , what move did we make , etc..
Show all coordinates 

so what is my goal?

get orbs with orbsdetector or something like that , get those orbs and place them into 3d enviorment (window)
my car will be mapped as a green box , and boom we move.
So my biggest challenge is converting those orbs (circles) into 3D 


"""
class SLAM(object):
    def __init__(self):
        self.running=True
        self.slamorbs =[]
        #CAR FRAME COORS
        self.xlox = -5
        self.parconn=None
        self.CarLines = []
        self.ShwLines=[]

        q = Queue()
        p = Process(target =self.SLAMWindow,args=(q,),daemon=True)
        p1 = Process(target= self.cv2window,args=(q,),daemon=True)
        p.start()
        p1.start()
        p.join()
        p1.join()
        #self.q.join()
       
    def cv2window(self,q):
       
        jop=0
        self.cap = cv2.VideoCapture("./video.mp4")
        while True:
            
            stat,img = self.cap.read()
            img = cv2.resize(img,(1280,720))
            oper= cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            orb = cv2.ORB_create()
            keypoints =[]
            feat = cv2.goodFeaturesToTrack(oper,3000,qualityLevel=0.001,minDistance=3) 
            for f in feat:
                for z in f:
                    x,y = z

                    if(x in range(400,650) and y in range(350,650)):
                        self.CarLines=[[x,y]]
                    else:
                        cv2.circle(img,(round(z[0]),round(z[1])),color=(0,255,0),radius=1)
                        self.slamorbs.append([round(z[0]),round(z[1])])

            q.put([self.CarLines,self.slamorbs])
            cv2.imshow("Video Feed",img)
            if(cv2.waitKey(60 ) == ord('q')):
                break
    
    def AvgLines(self,lines):
        xs =[]
        ys=[]
        
        for l in lines:
            x,y = l

            x/=1000
            y/=1000
            xs.append(x)
            ys.append(y)
        
        return [np.average(xs),np.average(ys)]
    def CarFrame(self):
        glColor3f(0,255,0)
        glBegin(GL_LINES)
        """
        xlox = -5 
        for l,i in zip(self.CarLines,range(len(self.CarLines))):
            x,y = l
            print(x/1000)
            x=(x/1000)*-1
            y = xlox
            glVertex3f(x,y,1)
            glVertex3f(x,y+0.1,1)
            xlox+=0.1            
        """
        
        #ITS ALWAYS GOING TO DO IT FOR EVERY MOVE !
        print(self.CarLines)
        x,y = self.AvgLines(self.CarLines)
        xlox = -3
        if(not isnan(x)):
            x=round(x)
            y=round(y)
            self.ShwLines.append([x,y])
            self.CarLines.clear()
        
        if(len(self.ShwLines)>0):
            for l in self.ShwLines:
                x,y = l
                y+=xlox
                if(x != 1):
                    glVertex3f(x,y,1)
                    glVertex3f(x,y+0.15,1)

                    glVertex3f(x,y,1)
                    glVertex3f(x+0.1,y,1)

                    glVertex3f(x,y+0.15,1)
                    glVertex3f(x+0.1,y+0.15,1)
                    
                    glVertex3f(x+0.1,y,1)
                    glVertex3f(x+0.1,y+0.15,1)

                xlox+=0.3
        glEnd()
    def ORBS(self):
       
        glBegin(GL_LINES)

        for orb in self.slamorbs:
            
            glColor3f(255,0,0)
            x,y = orb
            x=sin(x)*cos(x)+np.tan(x)
            y=(y/1000)+(np.tan(y)//12)
            glVertex3f(y,x,y)
            glVertex3f(y+0.001,x,y)
            
        glEnd()
       

    def SLAMWindow(self,q):

        self.parconn = q
        pygame.init()
        display = (1280,720)
        pygame.display.set_mode(display, DOUBLEBUF|OPENGL, RESIZABLE)
        gluPerspective(45, (1.0*display[0]/display[1]), 0.01, 1280.0)
        glTranslatef(0.0,0.0, -5)
        while True:

            for event in pygame.event.get():
                if(event.type == pygame.MOUSEBUTTONDOWN):
                    if(event.button == 4):
                        print("Zoom")
                        glTranslatef(0,0,1)
                    if(event.button == 3):
                        mouseMove = pygame.mouse.get_rel()
                        glRotatef(mouseMove[0]*0.1, mouseMove[0], 1.0, 0.0)
                    if(event.button == 1):
                        mouseMove = pygame.mouse.get_rel()
                        glRotatef(mouseMove[0]*0.1, 0, 1.0, 0.0)
                    if(event.button == 2):
                        mouseMove = pygame.mouse.get_rel()
                        glRotatef(mouseMove[0]*0.1, 0, mouseMove[1], 0.0)
                  
                    if(event.button == 5):
                        print("Unzoom")
                        glTranslatef(0,0,-1)
                if(event.type == pygame.KEYDOWN):
                    if(event.key == pygame.K_UP):
                        print("top")
                        glTranslatef(0,-1,0)
                    if(event.key == pygame.K_DOWN):
                        print("DOWN")
                        glTranslatef(0,1,0)
                    if(event.key == pygame.K_LEFT):
                        print("left")
                        glTranslatef(1,0,0)
                     
                    if(event.key == pygame.K_RIGHT):
                        print("left")
                        glTranslatef(-1,0,0)

                if event.type == pygame.QUIT:
                    
                    pygame.quit()
                    quit()


            if(not self.parconn.empty()):
                self.CarLines,self.slamorbs= self.parconn.get()
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
            self.CarFrame()
            self.ORBS() 
            pygame.display.flip()


if __name__ == '__main__':
    slam= SLAM()
