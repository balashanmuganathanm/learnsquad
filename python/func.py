x=20
print("dgf  ")
def myfunc(*,name,age=0):
    print(__name__)
    return(f"Hello, {name} you are {age} years old")

if __name__ == "__main__":
    print(myfunc(name="John", age=30))