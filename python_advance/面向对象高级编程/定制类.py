# 1.__slots__用于限制向实例绑定属性
# 2.__len__是为了能让class作用于len()函数,如'123456'.__len__()，结果为6
'''
3.__str__
print(Student('Michael'))
<__main__.Student object at 0x109afb190>
打印出一堆<__main__.Student object at 0x109afb190>，不好看。
怎么才能打印得好看呢？只需要定义好__str__()方法，返回一个好看的字符串就可以了：
'''
class Student():
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return 'Student object (name: %s)' % self.name

s = Student('new')
print(s)
'''
直接敲变量不用print，打印出来的实例还是不好看:<__main__.Student object at 0x109afb310>
这是因为直接显示变量调用的不是__str__()，而是__repr__()，两者的区别是__str__()返回用户看到的字符串，而__repr__()返回程序开发者看到的字符串，也就是说，__repr__()是为调试服务的。
解决办法是再定义一个__repr__()。但是通常__str__()和__repr__()代码都是一样的，所以，有个偷懒的写法：
__repr__ = __str__
'''
#4.__iter__
# 如果一个类想被用于for ... in循环，类似list或tuple那样，就必须实现一个__iter__()方法，
# 该方法返回一个迭代对象，然后，Python的for循环就会不断调用该迭代对象的__next__()方法拿到循环的下一个值，直到遇到StopIteration错误时退出循环。
class Fib():
    def __init__(self):
        self.a, self.b = 0, 1
    def __iter__(self):
        return self
    def __next__(self):
        self.a, self.b = self.b, self.a + self.b
        if self.a > 100:
            raise StopIteration
        return self.a
f = Fib()
for i in f:
    print(i)

# 5.要表现得像list那样按照下标取出元素，需要实现__getitem__()方法：
class Fib():
    def __init__(self):
        self.a, self.b = 0, 1
    def __iter__(self):
        return self
    def __next__(self):
        self.a, self.b = self.b, self.a + self.b
        if self.a > 100:
            raise StopIteration
        return self.a
    def __getitem__(self, item):
        self.a, self.b = 1, 1
        for i in range(item):
            self.a, self.b = self.b, self.a + self.b
        return self.a

print(Fib()[100])
# 但是list有个神奇的切片方法,对于Fib却报错。原因是__getitem__()传入的参数可能是一个int，也可能是一个切片对象slice，所以要做判断：
class Fib():
    def __init__(self):
        self.a, self.b = 0, 1
    def __iter__(self):
        return self
    def __next__(self):
        self.a, self.b = self.b, self.a + self.b
        if self.a > 100:
            raise StopIteration
        return self.a
    def __getitem__(self, n):
        if isinstance(n, int):  # n是索引
            a, b = 1, 1
            for x in range(n):
                a, b = b, a + b
            return a
        if isinstance(n, slice):  # n是切片
            start = n.start
            stop = n.stop
            if start is None:
                start = 0
            a, b = 1, 1
            L = []
            for x in range(stop):
                if x >= start:
                    L.append(a)
                a, b = b, a + b
            return L

print(Fib()[:10])
# 需要注意，以上没有对step参数作处理：也没有对负数作处理，所以，要正确实现一个__getitem__()还是有很多工作要做的。
# 此外，如果把对象看成dict，__getitem__()的参数也可能是一个可以作key的object，例如str。
# 与之对应的是__setitem__()方法，把对象视作list或dict来对集合赋值。最后，还有一个__delitem__()方法，用于删除某个元素。
# 总之，通过上面的方法，我们自己定义的类表现得和Python自带的list、tuple、dict没什么区别，这完全归功于动态语言的“鸭子类型”，不需要强制继承某个接口。
#6.__getattr__
'''
正常情况下，当我们调用类的方法或属性时，如果不存在，就会报错。
要避免这个错误，除了可以加上一个score属性外，Python还有另一个机制，那就是写一个__getattr__()方法，动态返回一个属性。
当调用不存在的属性时，比如score，Python解释器会试图调用__getattr__(self, 'score')来尝试获得属性，这样，我们就有机会返回score的值：
'''
class Student(object):

    def __init__(self):
        self.name = 'Michael'

    def __getattr__(self, attr):
        if attr=='score':
            return 99

print(Student().score)
# 返回函数也是完全可以的：
class Student(object):

    def __getattr__(self, attr):
        if attr=='age':
            return lambda: 25
# 只是调用方式要变为：
print(Student().age())

'''
注意，只有在没有找到属性的情况下，才调用__getattr__，已有的属性，比如name，不会在__getattr__中查找。
此外，注意到任意调用如s.abc都会返回None，这是因为我们定义的__getattr__默认返回就是None。
要让class只响应特定的几个属性，我们就要按照约定，抛出AttributeError的错误：
'''
class Student(object):
    def __getattr__(self, attr):
        if attr=='age':
            return lambda: 25
        raise AttributeError('\'Student\' object has no attribute \'%s\'' % attr)

# 如果要写SDK，给每个URL对应的API都写一个方法，那得累死，而且，API一旦改动，SDK也要改。
# 利用完全动态的__getattr__，我们可以写出一个链式调用：

class Chain(object):

    def __init__(self, path=''):
        self._path = path

    def __getattr__(self, path):
        return Chain('%s/%s' % (self._path, path))

    def __str__(self):
        return self._path

    __repr__ = __str__

print(Chain().status.user.timeline.list)
# '/status/user/timeline/list'
# 这样，无论API怎么变，SDK都可以根据URL实现完全动态的调用，而且，不随API的增加而改变！
# 7.__call__
# 任何类，只需要定义一个__call__()方法，就可以直接对实例进行调用。
class Student(object):
    def __init__(self, name):
        self.name = name

    def __call__(self):
        print('My name is %s.' % self.name)
# 调用方式如下：
s = Student('Michael')
s() # self参数不要传入，也可写成Student()()
# My name is Michael.
'''
那么，怎么判断一个变量是对象还是函数呢？
其实，更多的时候，我们需要判断一个对象是否能被调用，能被调用的对象就是一个Callable对象，比如函数和我们上面定义的带有__call__()的类实例：
>>> callable(Student())   # 即上述的s对象，它本身可调用
True
>>> callable(max)
True
>>> callable([1, 2, 3])
False
>>> callable(None)
False
>>> callable('str')
False
通过callable()函数，我们就可以判断一个对象是否是“可调用”对象。
'''