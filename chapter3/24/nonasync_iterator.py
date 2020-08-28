# Example 3-24. A traditional, nonasync iterator
class A:
    # An iterator must implement the __iter__() special method.
    def __iter__(self):
        # Initialize some state to the “starting” state.
        self.x = 0
        # The __iter__() special method must return an iterable; i.e., an
        # object that implements the __next__() special method. In this case,
        # it’s the same instance, because A itself also implements the
        # __next__() special method.
        return self

    # The __next__() method is defined. This will be called for every step in
    # the iteration sequence until...
    def __next__(self):
        if self.x > 2:
            # ...StopIteration is raised.
            raise StopIteration
        else:
            self.x += 1
        # The returned values for each iteration are generated.
        return self.x


for i in A():
    print(i)
