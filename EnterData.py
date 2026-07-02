import tkinter as tk
import copy

#only first experiments

def enterResults(games,gamesFT=[25,25,15],force=False):
    newgames=copy.deepcopy(games)
    
    for g in newgames:
        if not g[1]:
            for i in range(len(gamesFT)):
                final=gamesFT[i]
                def data_entry():
                    def submit():
                        s1=score1.get()
                        s2=score2.get()
                        valid=False
                        if s1>=i:
                            if (s1==i and 0<=s2<=i-2) or (s1>i and s2==s1-2):
                                valid=True
                        elif s2>=i:
                            if (s2==i and 0<=s1<=i-2) or (s2>i and s1==s2-2):
                                valid=True
                        else:
                            valid=False
                        if valid:
                            g[1].append([score1.get(),score2.get()])
                            root.destroy()
                        else:
                            root.destroy()
                            data_entry()
                    root = tk.Tk()
                    root.geometry("800x600")
                    root.title(g[0][0] + "vs" + g[0][1] + ", Game " + str(i+1)) 
                    score1=tk.IntVar()
                    score2=tk.IntVar()
                    tk.Label(root, text=g[0][0]).pack(padx=20,pady=20)
                    tk.Entry(root, textvariable=score1).pack()

                    tk.Label(root, text=g[0][1]).pack(padx=20,pady=20)
                    tk.Entry(root, textvariable=score2).pack()

                    tk.Button(root, text="Submit", command=submit).pack()
                    
                    root.mainloop()
                data_entry()
    return newgames

print(enterResults([[["A","B"],[]]],gamesFT=[25]))