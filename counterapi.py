def updateCounter(filename = "totalnumapi.txt"):
    try:
        with open(filename, "r") as file:
            countStr = file.read().strip()
            if countStr:
                count = int(countStr)
            else:
                count = 0
    except FileNotFoundError:
        count = 0
    
    count += 1

    with open(filename, "w") as file:
        file.write(str(count))

    return count