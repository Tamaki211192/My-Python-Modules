A = {"zhang", "li", "wang"}
B = {"li", "wang", "zhao"}
# 交集
print(A & B)   # {'li', 'wang'}
# intersection是&的等价写法
course_a = {"Tom", "Amy", "Jack"}
course_b = {"Amy", "Bob", "Jack"}
print(course_a.intersection(course_b))  # {'Amy', 'Jack'}
print(course_a & course_b)              # {'Amy', 'Jack'}

# 并集
print(A | B)   # {'zhang','li','wang','zhao'}
# update用法也类似于并集，但是会改变原集合
course_a.update(course_b)

# 差集
print(A - B)   # {'zhang'}
print(B - A)   # {'zhao'}
