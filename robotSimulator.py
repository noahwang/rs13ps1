#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import curses
import locale
import random
import time
import itertools
import math

locale.setlocale(locale.LC_ALL, 'ja_JP.UTF-8')
random.seed()

class Maze:
    '''Maze Class'''
    primActionCount = 0
    robotDirec = u'↑'
    robotSignal = None
    direcDict = {u'←':(0,-1), u'↑':(-1,0), u'→':(0,1), u'↓':(1,0)}
    turnDict = {u'←':(u'↓',u'↑'), u'↑':(u'←',u'→'),
                u'→':(u'↑',u'↓'), u'↓':(u'→',u'←')}
    def __init__ (self, mazeStr):
        '''Initializing Maze'''
        self.mazeStr = mazeStr
        mazeStrl = mazeStr.splitlines();
        self.mazeMatrix = map(lambda l: map(lambda c: c, l), mazeStrl)
        self.primActionList = [self.turnLeft, self.turnRight,
                               self.moveAhead, self.lookAhead][:3] #define primActions
        for x,l in enumerate(mazeStrl) :
            if l.count(u'S'):
                self.robotPos = self.startPos = (x, l.index(u'S'))
                self.mazeMatrix[x][l.index(u'S')] = u' '
            elif l.count(u'G'):
                self.goalPos = (x, l.index(u'G'))

    def getMDistFromGoal (self):
        return (abs(self.robotPos[0] - self.goalPos[0]) + \
                abs(self.robotPos[1] - self.goalPos[1]))

    def resetRobot (self):
        self.robotPos = self.startPos
        self.robotDirec = u'↑'
        self.robotSignal = None

    def turnLeft (self):
        '''Action turnLeft'''
        self.primActionCount += 1
        self.robotDirec = self.turnDict[self.robotDirec][0]
        self.robotSignal = None

    def turnRight (self):
        '''Action turnRight'''
        self.primActionCount += 1
        self.robotDirec = self.turnDict[self.robotDirec][1]
        self.robotSignal = None

    def moveAhead (self):
        '''Action moveAhead'''
        self.primActionCount += 1
        y,x = self.direcDict[self.robotDirec]
        cy,cx = self.robotPos
        frontItem = self.mazeMatrix[cy + y][cx + x]
        if frontItem == u'█':
            self.robotSignal = (u'B', u'U')
            return(u'B', u'U')
        elif frontItem == u'G':
            self.robotPos = (cy + y, cx + x)
            self.robotSignal = (u'G', u'G')
            return(u'G', u'G')
        else:
            self.robotPos = (cy + y, cx + x)
            self.robotSignal = None

    def lookAhead (self):
        '''Action lookAhead'''
        self.primActionCount += 1
        y,x = self.direcDict[self.robotDirec]
        cy,cx = self.robotPos
        frontItem = self.mazeMatrix[cy + y][cx + x]
        if frontItem == u'█':
            self.robotSignal = (u'█', u'█')
            return (u'█', u'█')
        elif frontItem == u'G':
            self.robotSignal = (u'G', u'█')
            return (u'G', u'█')
        else:
            secondItem = self.mazeMatrix[cy + y*2][cx + x*2]
            self.robotSignal = (frontItem, secondItem)
            return (frontItem, secondItem)

    def randomlyReorient (self):
        '''Combined action of multiple turnLeft'''
        for i in range(0,random.randrange(4)):
            self.turnLeft()

    def lookAndMoveAhead (self):
        '''Combined action of lookAhead with moveAhead'''
        self.lookAhead()
        self.moveAhead()

def randomControl (msecPerFrame, repeatCount):
    '''Random moving controller'''
    p = int(1000.0 / (30.0 * msecPerFrame))
    for repeat in range(repeatCount):
        while random.choice(maze.primActionList)() != (u'G', u'G'):
            time.sleep(msecPerFrame / 1000.0)
            if p == 0 or maze.primActionCount % p == 0:
                printStatus('Primitive Action Count: %d' % maze.primActionCount)
                printMaze()
        printStatus('Primitive Action Count: %d' % maze.primActionCount)
        printMaze()
        addCount(maze.primActionCount)
        printCount()
        maze.resetRobot()
        maze.primActionCount = 0

def initQ (qValue = 0.0):
    global qStatus, qStatActionPair, Q, qAlpha, qGamma, qEpsilon
    qStatus = itertools.product(range(len(maze.mazeMatrix)), # y
                                range(len(maze.mazeMatrix[0])), # x
                                maze.direcDict.keys(), # direc
                                [None,
                                 (u'B', u'U'), (u'G', u'G'),
                                 (u' ', u' '), (u' ', u'█'),
                                 (u'█', u'█'), (u'G', u'█')]) #signals
    qStatActionPair = itertools.product(qStatus, maze.primActionList)
    Q = dict([(s_a, qValue) for s_a in qStatActionPair])
    qAlpha = 0.1
    qGamma = 0.9
    qEpsilon = 0.1

def qReward (status, newStatus):
    signal = newStatus[3]
    if signal == None:
        if status[:2] == newStatus[:2]: return 0.0
        else: return 1.0
    elif signal == (u'B', u'U'): return -10.0
    elif signal == (u'G', u'G'): return 10000.0
    elif signal == (u' ', u' '): return 3.0
    elif signal == (u' ', u'█'): return 0.5
    elif signal == (u'█', u'█'): return 0.0
    elif signal == (u'G', u'█'): return 8000.0

def actorEpsilonGreedy (status):
    if random.random() > qEpsilon:
        actions = [(status, a) for a in maze.primActionList]
        actionValues = [Q[(status, a)] for a in maze.primActionList]
        actionIndex = max([(y, x) for x,y in enumerate(actionValues)])[1]
        action = maze.primActionList[actionIndex]
        n = len(maze.primActionList)
        return action
    else:
        return random.choice(maze.primActionList)

def actorSoftmax (status):
    T = 1000.0
    actorValList = [math.exp(Q[(status, a)] / T) for a in maze.primActionList]
    actorSum = sum(actorValList)
    actorVal = random.uniform(0.0, actorSum)
    action = maze.primActionList[0]
    roulette = 0.0
    for i,a in enumerate(maze.primActionList):
        roulette += actorValList[i]
        if roulette <= actorVal: action = maze.primActionList[i + 1]
        else: break
    return action

def qLearningControl (controllerName ,msecPerFrame, repeatCount):
    '''Q-Learning enhanced controller'''
    p = int(1000.0 / (20.0 * msecPerFrame))
    if controllerName == 'eps': # selecting action
        actor = actorEpsilonGreedy
    elif controllerName == 'sm':
        actor = actorSoftmax
    for repeat in range(repeatCount):
        while True:
            time.sleep(msecPerFrame / 1000.0)
            status = (maze.robotPos[0], maze.robotPos[1],
                      maze.robotDirec, maze.robotSignal)
            action = actor(status)
            action() # commit action
            newStatus = (maze.robotPos[0], maze.robotPos[1],
                         maze.robotDirec, maze.robotSignal)
            newMaxActionValue = max([Q[(newStatus, a)] for a in maze.primActionList])
            delta = qReward(status, newStatus) + \
                    qGamma * newMaxActionValue - \
                    Q[(status, action)]
            refreshValue = Q[(status, action)] + qAlpha * delta
            Q[(status, action)] = refreshValue
            if newStatus[3] == (u'G', u'G'): break
            if p == 0 or maze.primActionCount % p == 0:
                printStatus('Q Value: %s, Count: %d' %
                            (refreshValue, maze.primActionCount))
                printMaze()
        printStatus('Primitive Action Count: %d' % maze.primActionCount)
        printMaze()
        addCount(maze.primActionCount)
        printCount()
        maze.resetRobot()
        maze.primActionCount = 0
        
def executeQResult (msecPerFrame, maxlimit):
    '''Q-Learning result executer'''
    p = int(1000.0 / (20.0 * msecPerFrame))
    for i in range(maxlimit):
        time.sleep(msecPerFrame / 1000.0)
        status = (maze.robotPos[0], maze.robotPos[1],
                  maze.robotDirec, maze.robotSignal)
        actions = [(status, a) for a in maze.primActionList]
        actionValues = [Q[(status, a)] for a in maze.primActionList]
        actionValue, actionIndex = max([(y, x) for x,y in enumerate(actionValues)])
        action = maze.primActionList[actionIndex]
        if action() == (u'G', u'G'): break # commit action
        if p == 0 or maze.primActionCount % p == 0:
            printStatus('Q Value: %s, Count: %d' %
                        (actionValue, maze.primActionCount))
            printMaze()
    printStatus('Primitive Action Count: %d' % maze.primActionCount)
    printMaze()
    maze.resetRobot()
    maze.primActionCount = 0


### Under this line is codes for IO

def printMaze ():
    '''Print maze and robot'''
    maxy,maxx = stdscr.getmaxyx()
    pad.clear()
    pad.addstr(0, 0, maze.mazeStr.encode('utf-8'))
    pad.addstr(maze.robotPos[0],maze.robotPos[1],
                    maze.robotDirec.encode('utf-8'))
    pad.refresh(0, 0, 3, 0, maxy - 3, maxx - 1)

def printStatus (s):
    window.addstr(1, 0, s)
    window.clrtoeol()
    window.refresh()

def printCount ():
    window.addstr(2, 0, str(counts).strip('[]')[-(window.getmaxyx()[1]) + 1:])
    window.clrtoeol()
    window.refresh()

def addCount (n):
    counts.append(n)

def clearCount ():
    global counts
    counts = []

def commandMode ():
    while True:
        printMaze()
        window.addstr(0, 0, '> ')
        cmd = window.getstr().split()
        window.clear()
        if cmd == []: continue
        elif cmd[0] == 'random':
            if len(cmd) < 3: pass
            else: randomControl(int(cmd[1]), int(cmd[2]))
        elif cmd[0] == 'qlearn':
            if len(cmd) < 4: pass
            else: qLearningControl(cmd[1], int(cmd[2]), int(cmd[3]))
        elif cmd[0] == 'qexec':
            if len(cmd) < 3: pass
            else: executeQResult(int(cmd[1]), int(cmd[2]))
        elif cmd[0] == 'reset':
            if len(cmd) == 1: pass
            elif cmd[1] == 'robot': maze.resetRobot()
            elif cmd[1] == 'count':
                clearCount()
                printCount()
            elif cmd[1] == 'pcount': maze.primActionCount = 0
            elif cmd[1] == 'rpc':
                maze.resetRobot()
                maze.primActionCount = 0
            elif cmd[1] == 'Q':
                if len(cmd) == 2: initQ()
                else: initQ(float(cmd[2]))
            elif cmd[1] == 'all':
                maze.resetRobot()
                maze.primActionCount = 0
                clearCount()
                printCount()
                initQ()
        elif cmd[0] == 'set':
            if len(cmd) < 3: pass
            elif cmd[1] == 'eps':
                global qEpsilon
                qEpsilon = float(cmd[2])
        elif cmd[0] == 'print':
            if len(cmd) == 1: pass
            elif cmd[1] == 'pcount':
                printStatus('Primitive Action Count: %d' % maze.primActionCount)
            elif cmd[1] == 'count':
                printCount()
            elif cmd[1] == 'eps':
                printStatus('epsilon: %f' % qEpsilon)
            elif cmd[1] == 'dist':
                printStatus('Distance to Goal: %d' % maze.getMDistFromGoal())
        elif cmd[0] == 'save':
            if len(cmd) < 3: pass
            elif cmd[1] == 'count':
                targetFile = open(cmd[2], 'w')
                targetFile.write(str(counts).strip('[]') + '\n')
                targetFile.close()
        elif cmd[0] == 'quit':
            curses.endwin()
            break
        elif cmd[0] == 'd':
            directMode()

def directMode ():
    curses.noecho()
    curses.cbreak()
    window.keypad(1)
    while True:
        c = window.getch()
        if c == curses.KEY_LEFT: maze.turnLeft()
        elif c == curses.KEY_RIGHT: maze.turnRight()
        elif c == curses.KEY_UP:
            signal = maze.moveAhead()
            if (signal == None):
                printStatus('')
            else:
                signal1, signal2 = signal
                printStatus('Signal: (%s,%s)' % (signal1.encode('utf-8'),
                                                signal2.encode('utf-8')))
        elif c == curses.KEY_DOWN:
            obj1,obj2 = maze.lookAhead()
            printStatus('Signal: Ahead(%s,%s)' % (obj1.encode('utf-8'),
                                           obj2.encode('utf-8')))
        elif c == ord('r'): maze.randomlyReorient()
        elif c == ord('c'): break
        printMaze()
        window.move(0, 0)
    window.keypad(0)
    curses.echo()
    curses.nocbreak()

def printStdErr(s):
    sys.stderr.write(s + '\n')

if __name__ == '__main__':
    '''Main Routine'''
    if len(sys.argv) < 2:
        print 'usage: %s mazefile' % sys.argv[0]
        exit()
    stdscr = curses.initscr()
    mazeFile = open(sys.argv[1], 'r')
    mazeStr = unicode(mazeFile.read(), 'utf-8')
    mazeFile.close()
    '''Initializing Simulator'''
    maze = Maze(mazeStr)
    counts = []
    initQ()
    window = curses.newwin(3,stdscr.getmaxyx()[1])
    pad = curses.newpad(100, 5000)
    padPos = (0, 0)
    try:
        commandMode()
    finally:
        curses.endwin()
