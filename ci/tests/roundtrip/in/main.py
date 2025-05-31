from lib1 import greeter1
import lib2
from another_lib import another_greeter as ag

def main ():
    greeter1 ()
    lib2.greeter2 ()
    ag ()

main ()
