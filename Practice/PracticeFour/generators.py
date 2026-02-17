# task one

# def sq_generator(n):
#   counter = 1;
#   while counter <= n:
#     yield counter**2
#     counter += 1

# ctr = sq_generator(3)
# for n in ctr:
#   print(n)


# task two

# def even_generator(n):
#   for i in range(n+1):
#     if i % 2 == 0:
#       yield i

# n = int(input())

# result = ",".join(str(num) for num in even_generator(n))
# print(result)


# task three

# def ThreeFour_generator(n):
#   for i in range(n+1):
#     if i % 3 == 0 or i % 4 == 0:
#       yield i

# for el in ThreeFour_generator(10):
#   print(el)


# task four

# def AtoBSquares_generator(a,b):
#   for i in range(a,b+1):
#     yield i**2
  

# for el in AtoBSquares_generator(3,5):
#   print(el)


# task five

# def reverse_generator(n):
#   for i in range(n , -1 , -1):
#     yield i
    
# for el in reverse_generator(10):
#   print(el)