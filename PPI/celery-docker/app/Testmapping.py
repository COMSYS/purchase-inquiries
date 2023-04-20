from functools import reduce
max_4 = 5
max_3 = 3
max_2 = 2
max_1 = 2
max = [5,3,2,2]


def calculation(inputstring):
    liste = list(inputstring)
    res = 0
    count = 0
    while liste:
        first = liste[0]
        liste.remove(first)
        print("first is ", first)
        intermed_list = max[count+1:]
        if(len(intermed_list)>=2):
            intermed_res = reduce(lambda x,y: x*y, intermed_list)
        elif len(intermed_list) == 1:
            intermed_res = intermed_list[0]
        else:
            intermed_res = 1
        res = res + (int(first)-1) * intermed_res
        count = count +1
    print(res)


if __name__ == '__main__':

    liste = list()
    for f in range(max_4):
        for l in range(max_3):
            for m in range(max_2):
                for r in range(max_1):
                    liste.append(str(f+1)+str(l+1)+str(m+1)+ str(r+1))

    d = dict([(y,x+1) for x,y in enumerate(sorted(set(liste)))])
    print(d)
    inputS = "4112"
    calculation(inputS)
    print("control")
    print(d[inputS])