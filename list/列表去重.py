def unique_list1():
    list1 = [int(x) for x in input('输入的列表内容请用空格隔开').split()]
    set1 = set(list1)
    print(set1)
# 以上是不转换成列表的，输出的结果是集合


def unique_list2():
    list1 = [int(x) for x in input('输入的列表内容请用空格隔开').split()]
    set1 = set(list1)
    unique_list = list(set1)
    print(unique_list)
