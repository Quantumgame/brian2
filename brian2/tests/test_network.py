from brian2 import (Clock, Network, ms, second, BrianObject, defaultclock,
                    run, stop, NetworkOperation, network_operation)
from numpy.testing import assert_equal, assert_raises

def test_empty_network():
    defaultclock.t = 0*second
    # Check that an empty network functions correctly
    net = Network()
    net.run(1*second)

class Counter(BrianObject):
    def __init__(self, **kwds):
        super(Counter, self).__init__(**kwds)
        self.count = 0        
    def update(self):
        self.count += 1

def test_network_single_object():
    defaultclock.t = 0*second
    # Check that a network with a single object functions correctly
    x = Counter()
    net = Network(x)
    net.run(1*ms)
    assert_equal(x.count, 10)

def test_network_two_objects():
    defaultclock.t = 0*second
    # Check that a network with two objects and the same clock function correctly
    x = Counter()
    y = Counter()
    net = Network()
    net.add([x, [y]]) # check that a funky way of adding objects work correctly
    assert net.objects[0] is x
    assert net.objects[1] is y
    assert_equal(len(net.objects), 2)
    net.run(1*ms)
    assert_equal(x.count, 10)
    assert_equal(y.count, 10)

updates = []
class Updater(BrianObject):
    def __init__(self, name, **kwds):
        super(Updater, self).__init__(**kwds)
        self.name = name
    def update(self):
        updates.append(self.name)

def test_network_different_clocks():
    defaultclock.t = 0*second
    # Check that a network with two different clocks functions correctly
    clock1 = Clock(dt=1*ms, order=0)
    clock3 = Clock(dt=3*ms, order=1)
    x = Updater('x', clock=clock1)
    y = Updater('y', clock=clock3)
    net = Network(x, y)
    net.run(10*ms)
    assert_equal(''.join(updates), 'xyxxxyxxxyxxx')

def test_network_different_when():
    defaultclock.t = 0*second
    # Check that a network with different when attributes functions correctly
    updates[:] = []
    x = Updater('x', when='start')
    y = Updater('y', when='end')
    net = Network(x, y)
    net.run(0.3*ms)
    assert_equal(''.join(updates), 'xyxy')

class Preparer(BrianObject):
    def __init__(self, **kwds):
        super(Preparer, self).__init__(**kwds)
        self.did_reinit = False
        self.did_prepare = False
    def reinit(self):
        self.did_reinit = True
    def prepare(self):
        self.did_prepare = True
    def update(self):
        pass

def test_network_reinit_prepare():
    defaultclock.t = 0*second
    # Check that reinit and prepare work        
    x = Preparer()
    net = Network(x)
    assert_equal(x.did_reinit, False)
    assert_equal(x.did_prepare, False)
    net.run(1*ms)
    assert_equal(x.did_reinit, False)
    assert_equal(x.did_prepare, True)
    net.reinit()
    assert_equal(x.did_reinit, True)

def test_magic_network():
    defaultclock.t = 0*second
    # test that magic network functions correctly
    x = Counter()
    y = Counter()
    run(10*ms)
    assert_equal(x.count, 100)
    assert_equal(y.count, 100)

class Stopper(BrianObject):
    def __init__(self, stoptime, stopfunc, **kwds):
        super(Stopper, self).__init__(**kwds)
        self.stoptime = stoptime
        self.stopfunc = stopfunc
    
    def update(self):
        self.stoptime -= 1
        if self.stoptime<=0:
            self.stopfunc()

def test_network_stop():
    defaultclock.t = 0*second
    # test that Network.stop and global stop() work correctly
    net = Network()
    x = Stopper(10, net.stop)
    net.add(x)
    net.run(10*ms)
    assert_equal(defaultclock.t, 1*ms)
    
    del net
    defaultclock.t = 0*second
    
    x = Stopper(10, stop)
    net = Network(x)
    net.run(10*ms)
    assert_equal(defaultclock.t, 1*ms)

def test_network_operations():
    defaultclock.t = 0*second
    # test NetworkOperation and network_operation
    seq = []
    def f1():
        seq.append('a')
    op1 = NetworkOperation(f1, when='start')
    @network_operation
    def f2():
        seq.append('b')
    @network_operation(when='end', order=1)
    def f3():
        seq.append('c')
    run(1*ms)
    assert_equal(''.join(seq), 'abc'*10)


if __name__=='__main__':
    test_empty_network()
    test_network_single_object()
    test_network_two_objects()
    test_network_different_clocks()
    test_network_different_when()
    test_network_reinit_prepare()
    test_magic_network()
    test_network_stop()
    test_network_operations()
    