def backmovie(triple_set,movielist):
    t = triple_set
    m = movielist
    for i,name in enumerate(t[1]):
        if name in m.keys():
            t[1][i] = m[name]
    for i,name in enumerate(t[3]):
        if name in m.keys():
            t[3][i] = m[name]

    return t


def getmovie(question):
    mnum = 0
    ml = {}
    qstr = question
    temp = qstr.split("\"")
    #print(temp)

    ansq = ""
    for i,ch in enumerate(temp):
        if i % 2 == 1:
            mnum +=1
            m = 'mmmmm' + str(mnum)
            ansq = ansq + m
            ml[m] = ch
        else:
            ansq = ansq + ch
    
    return ansq, ml, mnum


if __name__=="__main__":
    
    questions = ['Who is actor of "Who is" and director of "The actor" and writer of "She"?']

    for q in questions:
        print(q)
        question,movielist,num = getmovie(q)
        print(question)
        print(num)
        print(movielist)
        #print()
        triplet_set = ([],['m1','p2'],[],['p1','m2'],[])
        triplet_new = backmovie(triplet_set,movielist)
        print(triplet_new)

