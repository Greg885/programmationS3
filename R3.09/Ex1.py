def divEntier(x: int, y: int) -> int:
    if x < y:
        return 0
    else:
        x = x - y
    return divEntier(x, y) + 1


if __name__ == '__main__':
    try:
        x = int(input("valeur de x: "))
        y = int(input("valeur de y: "))
        print(divEntier(x, y))
    except ValueError as err:
        print("ERR n'est pas un chiffre")
        print(err)
    except RecursionError:
        print("ERR y ne peut pas etre égal à 0")
    finally:
        print("END")
