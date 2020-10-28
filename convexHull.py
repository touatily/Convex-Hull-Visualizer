import time
import math

class ConvexHullSolver:
    pass
        
    
    @classmethod
    def algoGiftwrapping(cls, canvas=None, speed=None):
        if canvas is None: return
        if speed is None: return
        canvas.delete("convex")
        S = [(canvas.coords(e)[0]+3, canvas.coords(e)[1]+3, e) 
                for e in canvas.find_withtag("point")]
                
        if len(S)==0:
            return

        pointOnHull = min(S, key=lambda x: x[0])
        P = []
        while True:
            P.append(pointOnHull)
            if len(P) > 1: S.remove(P[-1])
            
            endpoint = S[0]
            # draw temporary line 
            canvas.create_line(P[-1][0], P[-1][1], endpoint[0], endpoint[1], width=2, fill="grey", dash=(3, 1), tag="convex temp")
            for j in range(0, len(S)):
                # check position of S[j]: P[-1] ---> endpoint
                pos = ((S[j][0] - P[-1][0]) * (endpoint[1] - P[-1][1]) - 
                    (S[j][1] - P[-1][1]) * (endpoint[0] - P[-1][0]))
                canvas.create_line(P[-1][0], P[-1][1], S[j][0], S[j][1], fill="green", dash=(10, 10), tag="convex dashed")
                canvas.update()
                time.sleep(1/speed.get())
                if (endpoint == pointOnHull) or (pos > 0):
                    canvas.delete("temp")
                    canvas.delete("dashed")
                    endpoint = S[j]
                    canvas.create_line(P[-1][0], P[-1][1], endpoint[0], endpoint[1], width=2, fill="grey", dash=(3, 1), tag="convex temp")
                    canvas.update()
                    time.sleep(1/speed.get())
                canvas.delete("dashed")
            pointOnHull = endpoint
            # draw line !
            canvas.delete("dashed")
            canvas.create_line(P[-1][0], P[-1][1], endpoint[0], endpoint[1], width=3, fill="red", tag="convex")
            if endpoint == P[0]:
                break
        # create polygone
        p = [(e[0], e[1]) for e in P]
        canvas.delete("convex")
        canvas.create_polygon(*p, width=4, outline="red", fill="green", stipple="gray50", tag="convex")
        
    
    def next_to_top(stack):
        return stack[-2]
    
    def ccw(p1, p2, p3):
        pos = ((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0]))
        return -pos
        
    @classmethod
    def algoGrahamScan(cls, canvas=None, speed=None):
        if canvas is None: return
        if speed is None: return
        canvas.delete("convex")
        
        S = [[canvas.coords(e)[0]+3, canvas.coords(e)[1]+3, e]
                for e in canvas.find_withtag("point")]
        P0 = max(S, key = lambda x: (x[1], -x[0]))
        SS = [ [*e, math.atan2(e[1]-P0[1], e[0]-P0[0]), 
                    math.sqrt((e[0]-P0[0])**2 + (e[1]-P0[1])**2)] 
                    for e in S]
        d = {}
        for e in SS:
            if e[3] in d.keys():
                d[e[3]] = max(d[e[3]], e, key=lambda x: x[4])
            else:
                d[e[3]] = e
                
        S = sorted(d.values(), key=lambda x: x[3], reverse=True)  
        stack = []    
        for p in S:
            if len(stack) >= 1 :
                canvas.delete("temp")
                for i in range(len(stack)-1):
                    canvas.create_line(stack[i][0], stack[i][1], stack[i+1][0], stack[i+1][1], width=3, fill="red", tag="temp")
                canvas.create_line(stack[-1][0], stack[-1][1], p[0], p[1], width=3, fill="blue", tag="temp")
                canvas.update()
                time.sleep(1/speed.get())
                
            while len(stack) > 1 and cls.ccw(cls.next_to_top(stack), stack[-1], p) <= 0:
                del stack[-1]
                # draw lines
                canvas.delete("temp")
                for i in range(len(stack)-1):
                    canvas.create_line(stack[i][0], stack[i][1], stack[i+1][0], stack[i+1][1], width=3, fill="red", tag="temp")
                canvas.create_line(stack[-1][0], stack[-1][1], p[0], p[1], width=3, fill="blue", tag="temp")
                canvas.update()
                time.sleep(1/speed.get())
            stack.append(p)

        p = [(e[0], e[1]) for e in stack]
        canvas.delete("temp")
        canvas.create_polygon(*p, fill="green", outline="red", width=4, stipple="gray50", tag="convex")
        
        
    def findHull(S, P, Q, canvas, speed):
        if len(S)==0: return []
        mid = ((P[0]+Q[0])//2, (P[1]+Q[1])//2)
        
        
        
        C = max(S, key= lambda e: math.fabs(ConvexHullSolver.ccw(P, e, Q)))
        
        canvas.delete(f"{P[0]}_{P[1]}_{Q[0]}_{Q[1]}")
        canvas.create_line(P[0], P[1], C[0], C[1], width = 3, tag=f"convex {P[0]}_{P[1]}_{C[0]}_{C[1]}")
        canvas.create_line(C[0], C[1], Q[0], Q[1], width = 3, tag=f"convex {C[0]}_{C[1]}_{Q[0]}_{Q[1]}")
        canvas.update()
        time.sleep(1/speed.get())
        
        S1 = [e for e in S if ConvexHullSolver.ccw(P, e, C) * ConvexHullSolver.ccw(P, mid, C) < 0]
        S2 = [e for e in S if ConvexHullSolver.ccw(Q, e, C) * ConvexHullSolver.ccw(Q, mid, C) < 0]
        
        l1 = ConvexHullSolver.findHull(S1, P, C, canvas, speed)
        l2 = ConvexHullSolver.findHull(S2, C, Q, canvas, speed)
        
        return l1 + [C] + l2
        
        
        
        
    @classmethod
    def algoQuickhull(cls, canvas=None, speed=None):
        if canvas is None: return
        if speed is None: return
        canvas.delete("convex")
        
        convex_hull = []
        S = [(canvas.coords(e)[0]+3, canvas.coords(e)[1]+3, e)
                for e in canvas.find_withtag("point")]
        if len(S) == 0: return
                
        A = min(S, key=lambda x: x[0])
        S.remove(A)
        B = max(S, key=lambda x: x[0])
        S.remove(B)
        
        canvas.create_line(A[0], A[1], B[0], B[1], width = 3, tag=f"convex {A[0]}_{A[1]}_{B[0]}_{B[1]}")
        canvas.create_line(A[0], A[1], B[0], B[1], width = 3, tag=f"convex {B[0]}_{B[1]}_{A[0]}_{A[1]}")
        canvas.update()
        time.sleep(1/speed.get())
        
        S1 = [e for e in S if cls.ccw(A, e, B) > 0]
        S2 = [e for e in S if cls.ccw(A, e, B) < 0]
                
        l1 = cls.findHull(S1, A, B, canvas, speed)
        l2 = cls.findHull(S2, B, A, canvas, speed)
        
        convex_hull = [A] + l1 + [B] + l2
        
        p = [(e[0], e[1]) for e in convex_hull]
        canvas.create_polygon(*p, fill="green", outline="red", width=4, stipple="gray50", tag="convex")


    @classmethod
    def algoDivideConquer(cls, canvas=None, speed=None):
        pass
        
    @classmethod
    def algoMonotoneChain(cls, canvas=None, speed=None):
        if canvas is None: return
        if speed is None: return
        canvas.delete("convex")
        
        S = [(canvas.coords(e)[0]+3, canvas.coords(e)[1]+3, e)
                for e in canvas.find_withtag("point")]
        if len(S) <= 1: return
        if len(S) == 2:
            p = [(e[0], e[1]) for e in S]
            canvas.create_polygon(*p, fill="green", outline="red", width=3, stipple="gray50", tag="convex")
            return 
        
        S.sort(key=lambda x : (x[0], x[1]))
        U = []
        L = []
        
        for i in range(len(S)):
            while len(L) > 1 and cls.ccw(L[-2], L[-1], S[i]) <= 0:
                del L[-1]
            canvas.delete("low")
            if len(L) >= 1:
                for j in range(len(L)-1):
                    canvas.create_line(L[j][0], L[j][1], L[j+1][0], L[j+1][1], width=3, fill="green", tag="low temp")
                canvas.create_line(L[-1][0], L[-1][1], S[i][0], S[i][1], width=3, fill= "blue", tag="low temp")
                canvas.update()
                time.sleep(1/speed.get()) 
            L.append(S[i])
        time.sleep(1/speed.get()) 
        canvas.delete("low")
        for i in range(len(L)-1):
            canvas.create_line(L[i][0], L[i][1], L[i+1][0], L[i+1][1], width=3, fill="red", tag="low temp")
            
            
        for i in range(len(S)-1, -1, -1):
            while len(U) > 1 and cls.ccw(U[-2], U[-1], S[i]) <= 0:
                del U[-1]
            canvas.delete("up")
            
            if len(U) >= 1:
                for j in range(len(U)-1):
                    canvas.create_line(U[j][0], U[j][1], U[j+1][0], U[j+1][1], width=3, fill="green", tag="up temp")
                canvas.create_line(U[-1][0], U[-1][1], S[i][0], S[i][1], width=3, fill= "blue", tag="up temp")
                canvas.update()
                time.sleep(1/speed.get()) 
            U.append(S[i])
        time.sleep(1/speed.get()) 
        canvas.delete("up")
        for j in range(len(U)-1):
            canvas.create_line(U[j][0], U[j][1], U[j+1][0], U[j+1][1], width=3, fill="red", tag="up temp")
        canvas.update()
        time.sleep(0.1) 
                
        del L[-1]
        del U[-1]
        canvas.delete("temp")
        p = [(e[0], e[1]) for e in L+U]
        canvas.create_polygon(*p, fill="green", outline="red", width=4, stipple="gray50", tag="convex")
        
