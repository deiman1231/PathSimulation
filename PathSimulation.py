'''
    File name: PathSimulation.py
    Author: Deimantas Valantiejus
    Date created: 03/02/2020
    Date last modified: 06/02/2020
    Python Version: 3.8
'''

import sys
import pygame
import time
import math
from pygame import event
from pygame.locals import *
from threading import Thread

bSize = 20
grey = (200, 200, 200)
red = (255, 0, 0)
green = (0, 150, 150)
delay = 20


class Panel:
    def __init__(self, sWidth, sHeight):
        self.delayCounter = 0
        pygame.init()
        self.sWidth = sWidth
        self.sHeight = sHeight
        self.display = pygame.display.set_mode((sWidth, sHeight))
        self.paintedButtons = []
        self.pointedButton = None
        self.mouseButtons = [False, False, False]
        self.trackingButtons = []                   # buttons that we want to find the shortest path between them
        self.pathFindButtons = []                   # buttons that we want to color all shortest paths
        self.shortestRoute = []                     # buttons that comprise the path between the 2 tracking buttons
        self.once = False
        self.thread = None
        self.buttons = [[Button(pygame.math.Vector2(x, y), grey, self.display, bSize) for x in range(sWidth // bSize)]
                        for y in range(sHeight // bSize)]

    def gameLoop(self):
        gameHertz = 64.0
        TBU = 1000000000 / gameHertz

        gameFPS = 1000.0
        TBR = 1000000000 / gameFPS

        MUBR = 3
        lastUpTime = time.time_ns()
        running = True
        while running:
            updateCount = 0
            thisTime = time.time_ns()

            while (thisTime - lastUpTime > TBU) and (updateCount < MUBR):
                self.update()
                lastUpTime += TBU
                updateCount += 1

            self.render()
            lastRenderTime = thisTime
            while thisTime - lastRenderTime < TBR and thisTime - lastUpTime < TBU:
                time.sleep(0)
                try:
                    time.sleep(0.000000001)
                except:
                    print("Error yealding thread")
                thisTime = time.time_ns()

    def update(self):
        self.fillPointedRect()
        self.fillColorRect()
        if self.thread is None:
            self.putTrackingButtons()
            self.removeFillColor()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouseButtons[event.button % 3] = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouseButtons[event.button % 3] = False

        key = pygame.key.get_pressed()
        if key[K_SPACE] and not self.once and len(self.trackingButtons) == 2:
            self.once = True
            self.thread = Thread(target=game.shortestPath, args=[game.getGrid()])
            self.thread.start()

    def render(self):
        self.display.fill((0, 0, 0))

        for y in range(self.sHeight // bSize):
            for x in range(self.sWidth // bSize):
                self.buttons[y][x].render()

        pygame.display.update()

    def fillPointedRect(self):
        x = pygame.mouse.get_pos()[0]
        y = pygame.mouse.get_pos()[1]

        if self.thread is None:
            if self.pointedButton:
                self.pointedButton.filled = False

            self.pointedButton = self.buttons[y // bSize][x // bSize]
            self.buttons[y // bSize][x // bSize].filled = True
        else:
            if self.pointedButton is not None:
                self.pointedButton.filled = False
            self.pointedButton = None


    def fillColorRect(self):
        x = pygame.mouse.get_pos()[0]
        y = pygame.mouse.get_pos()[1]

        if self.mouseButtons[1] and self.buttons[y // bSize][x // bSize] not in self.paintedButtons:
            self.paintedButtons.append(self.buttons[y // bSize][x // bSize])

        for button in self.paintedButtons:
            button.filled = True

        if self.thread is not None and self.thread.is_alive():
            for button in self.pathFindButtons:
                button.filled = True

        if self.thread is not None and not self.thread.is_alive():
            for button in self.pathFindButtons:
                if button not in self.shortestRoute:
                    button.filled = False
                    button.color = grey

        for button in self.shortestRoute:
            button.filled = True


    def putTrackingButtons(self):
        x = pygame.mouse.get_pos()[0]
        y = pygame.mouse.get_pos()[1]

        if not 1 < self.delayCounter <= delay and self.mouseButtons[1]:
            self.delayCounter = 1

        if not self.mouseButtons[1] and self.delayCounter != 0:
            self.delayCounter += 1

        if self.delayCounter > delay:
            self.delayCounter = 0

        if 1 < self.delayCounter <= delay and self.mouseButtons[1] and \
                self.buttons[y // bSize][x // bSize] not in self.trackingButtons:
            self.delayCounter = 0

            if len(self.trackingButtons) >= 2:
                self.trackingButtons[0].filled = False
                self.trackingButtons[0].color = grey
                del self.trackingButtons[0]

            if len(self.trackingButtons) < 2:
                self.buttons[y // bSize][x // bSize].filled = True
                self.buttons[y // bSize][x // bSize].color = red
                self.trackingButtons.append(self.buttons[y // bSize][x // bSize])

    def removeFillColor(self):
        x = pygame.mouse.get_pos()[0]
        y = pygame.mouse.get_pos()[1]

        if self.mouseButtons[0] and self.paintedButtons.__contains__(self.buttons[y // bSize][x // bSize]):
            self.buttons[y // bSize][x // bSize].filled = False
            self.buttons[y // bSize][x // bSize].color = grey
            self.paintedButtons.remove(self.buttons[y // bSize][x // bSize])

    def shortestPath(self, grid):
        diagDist = math.sqrt(2)
        normDist = 1
        next = None

        visited = [[False for _ in range(len(grid[y]))] for y in range(len(grid))]
        dist = [[float("inf") for _ in range(len(grid[y]))] for y in range(len(grid))]

        startX = int(self.trackingButtons[0].coord.x)
        startY = int(self.trackingButtons[0].coord.y)

        endX = int(self.trackingButtons[1].coord.x)
        endY = int(self.trackingButtons[1].coord.y)

        visited[startY][startX] = True
        queue = [[(startX, startY), 0, [(startX, startY)]]]
        routes = []

        while queue:
            next = queue.pop(0)
            nextY = int(next[0][1])
            nextX = int(next[0][0])
            prevDist = next[1]
            routes.append(next[2])

            if dist[nextY][nextX] > prevDist:
                dist[nextY][nextX] = prevDist

            if nextY == endY and nextX == endX:
                print(next[2])
                break

            if nextX != startX or nextY != startY:
                self.buttons[nextY][nextX].color = green

            self.pathFindButtons.append(self.buttons[nextY][nextX])

            if nextY + 1 < len(grid) and not visited[nextY + 1][nextX] and grid[nextY + 1][nextX] != 1:
                queue.append([(nextX, nextY + 1), prevDist + normDist, next[2]+[(nextX, nextY+1)]])
                visited[nextY + 1][nextX] = True
            if nextX + 1 < len(grid[0]) and not visited[nextY][nextX + 1] and grid[nextY][nextX + 1] != 1:
                queue.append([(nextX + 1, nextY), prevDist + normDist, next[2]+[(nextX+1, nextY)]])
                visited[nextY][nextX + 1] = True
            if nextY - 1 >= 0 and not visited[nextY - 1][nextX] and grid[nextY - 1][nextX] != 1:
                queue.append([(nextX, nextY - 1), prevDist + normDist, next[2]+[(nextX, nextY-1)]])
                visited[nextY - 1][nextX] = True
            if nextX - 1 >= 0 and not visited[nextY][nextX - 1] and grid[nextY][nextX - 1] != 1:
                queue.append([(nextX - 1, nextY), prevDist + normDist, next[2]+[(nextX - 1, nextY)]])
                visited[nextY][nextX - 1] = True
            if nextY + 1 < len(grid) and nextX + 1 < len(grid[0]) and not visited[nextY + 1][nextX + 1] and \
                    grid[nextY + 1][nextX + 1] != 1:
                queue.append([(nextX + 1, nextY + 1), prevDist + diagDist, next[2]+[(nextX+1, nextY+1)]])
                visited[nextY + 1][nextX + 1] = True
            if nextY - 1 >= 0 and nextX + 1 < len(grid[0]) and not visited[nextY - 1][nextX + 1] and grid[nextY - 1][
                nextX + 1] != 1:
                queue.append([(nextX + 1, nextY - 1), prevDist + diagDist, next[2]+[(nextX+1, nextY-1)]])
                visited[nextY - 1][nextX + 1] = True
            if nextY - 1 >= 0 and nextX - 1 >= 0 and not visited[nextY - 1][nextX - 1] and grid[nextY - 1][
                nextX - 1] != 1:
                queue.append([(nextX - 1, nextY - 1), prevDist + diagDist, next[2]+[(nextX-1, nextY-1)]])
                visited[nextY - 1][nextX - 1] = True
            if nextY + 1 < len(grid) and nextX - 1 >= 0 and not visited[nextY + 1][nextX - 1] and grid[nextY + 1][
                nextX - 1] != 1:
                queue.append([(nextX - 1, nextY + 1), prevDist + diagDist, next[2]+[(nextX-1, nextY+1)]])
                visited[nextY + 1][nextX - 1] = True

            k = pygame.key.get_pressed()
            if k[pygame.K_SPACE]:
                time.sleep(0.001)

        n = len(next[2])

        if endX != next[2][n-1][0] or endY != next[2][n-1][1]:
            self.shortestRoute.append(self.buttons[startY][startX])
            return

        for coord in next[2]:
            self.shortestRoute.append(self.buttons[coord[1]][coord[0]])

    def getGrid(self):
        grid = []
        for y in range(len(self.buttons)):
            grid.append([])
            for x in range(len(self.buttons[y])):
                if not self.buttons[y][x].filled:
                    grid[y].append(0)
                elif self.buttons[y][x].filled and self.buttons[y][x].color == grey:
                    grid[y].append(1)
                else:
                    grid[y].append(5)
        return grid


class Button:
    def __init__(self, coord, col, display, size, filled=False):
        self.coord = coord
        self.color = col
        self.display = display
        self.bSize = size
        self.filled = filled
        self.rect = pygame.Rect(int(coord.x) * size, int(coord.y) * size, bSize, bSize)

    def render(self):
        if not self.filled:
            pygame.draw.rect(self.display, self.color, self.rect, 1)
        else:
            pygame.draw.rect(self.display, self.color, self.rect, 0)


if __name__ == "__main__":
    game = Panel(800, 600)
    game.gameLoop()
