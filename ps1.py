#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import curses
import locale
import random

locale.setlocale(locale.LC_ALL, 'ja_JP.UTF-8')
random.seed()

stdscr = None

class RobotSimulator:
    class Maze:
        '''Maze Class'''
        def __init__ (self, mazeStr):
            '''Initializing Maze'''
            self.mazeStr = mazeStr
            mazeStrl = mazeStr.splitlines();
            self.mazeMatrix = map(lambda l: map(lambda c: c, l), mazeStrl)
            self.robotDirec = u'↑'
            self.direcDict = {u'←':(0,-1), u'↑':(-1,0), u'→':(0,1), u'↓':(1,0)}
            self.turnDict = {u'←':(u'↓',u'↑'), u'↑':(u'←',u'→'),
                             u'→':(u'↑',u'↓'), u'↓':(u'→',u'←')}
            for x,l in enumerate(mazeStrl) :
                if l.count(u'S'): self.robotPos = (x, l.index(u'S'))

        def turnLeft (self):
            self.robotDirec = self.turnDict[self.robotDirec][0]

        def turnRight (self):
            self.robotDirec = self.turnDict[self.robotDirec][1]

        def moveAhead (self):
            y,x = self.direcDict[self.robotDirec]
            cy,cx = self.robotPos
            frontItem = self.mazeMatrix[cy + y][cx + x]
            if frontItem == u'█':
                return(u'B', u'U')
            elif frontItem == u'G':
                self.robotPos = (cy + y, cx + x)
                return(u'G', u'G')
            else:
                self.robotPos = (cy + y, cx + x)

        def lookAhead (self):
            y,x = self.direcDict[self.robotDirec]
            cy,cx = self.robotPos
            frontItem = self.mazeMatrix[cy + y][cx + x]
            if frontItem == u'█':
                return (u'█', u'█')
            elif frontItem == u'G':
                return (u'G', u'█')
            else:
                secondItem = self.mazeMatrix[cy + y*2][cx + x*2]
                return (frontItem, secondItem)

        def randomlyReorient (self):
            for i in range(0,random.randrange(4)):
                self.turnLeft()

        def lookAndMoveAhead (self):
            self.lookAhead()
            self.moveAhead()

    def __init__ (self, mazeStr):
        '''Initializing Simulator'''
        self.maze = self.Maze(mazeStr)
        self.window = curses.newwin(3,stdscr.getmaxyx()[1])
        self.pad = curses.newpad(100, 5000)
        self.padPos = (0, 0)

    def execute (self, commands):
        '''Execute Commands to move robot'''
        print '\x1b[%d;%dH' % (1,1)
        for c in commands:
            print str(c)
            print '\x1b[%d;%dH' % (1,5)
            print '\x1b[0J'

    def printMaze (self):
        '''Print maze and robot'''
        maxy,maxx = stdscr.getmaxyx()
        self.pad.clear()
        self.pad.addstr(0, 0, self.maze.mazeStr.encode('utf-8'))
        self.pad.addstr(self.maze.robotPos[0],self.maze.robotPos[1],
                           self.maze.robotDirec.encode('utf-8'))
        self.pad.refresh(0, 0, 3, 0, maxy - 3, maxx - 1)

    def commandMode (self):
        while True:
            self.printMaze()
            self.window.addstr(0, 0, '> ')
            cmd = self.window.getstr()
            self.window.clear()
            if cmd == 'quit':
                curses.endwin()
                break
            if cmd == 'd':
                self.directMode()

    def directMode (self):
        curses.noecho()
        curses.cbreak()
        self.window.keypad(1)
        while True:
            c = self.window.getch()
            if c == curses.KEY_LEFT: self.maze.turnLeft()
            elif c == curses.KEY_RIGHT: self.maze.turnRight()
            elif c == curses.KEY_UP:
                signal = self.maze.moveAhead()
                if (signal == None):
                    self.window.addstr(2, 0, '               ')
                else:
                    signal1, signal2 = signal
                    self.window.addstr(2, 0, 'Signal: (%s,%s)' % (signal1.encode('utf-8'),
                                                                  signal2.encode('utf-8')))
            elif c == curses.KEY_DOWN:
                obj1,obj2 = self.maze.lookAhead()
                self.window.addstr(1, 0, 'Ahead: (%s,%s)' % (obj1.encode('utf-8'),
                                                             obj2.encode('utf-8')))
            elif c == ord('r'): self.maze.randomlyReorient()
            elif c == ord('c'): break
            self.printMaze()
            self.window.move(0, 0)
        self.window.keypad(0)
        curses.echo()
        curses.nocbreak()

if __name__ == '__main__':
    '''Main Routine'''
    if len(sys.argv) < 2:
        print 'usage: %s mazefile' % sys.argv[0]
        exit()
    stdscr = curses.initscr()
    mazeFile = open(sys.argv[1], 'r')
    mazeStr = unicode(mazeFile.read(), 'utf-8')
    mazeFile.close()
    robotSimulator = RobotSimulator(mazeStr)
    robotSimulator.commandMode()
    curses.endwin()
