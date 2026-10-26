# Do not change this function!
def divide(n, d):
    if d == 0:
        raise ZeroDivisionError

    return n / d

# Do not change this function!
def get_element(a, i):
    if i < 0 or i >= len(a):
        return -1

    return a[i]

def wrapped_divide(n, d):
    try:
        return divide(n,d)
    except ZeroDivisionError:
        return -1 
        

def wrapped_get_element(a, i):
    if get_element(a,i)==-1:
        raise(IndexError)
    else: return get_element(a,i)

print(wrapped_get_element([1,2],-1))



