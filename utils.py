
import sys
import time


# TBD - Fix output to handle overwriting of variable number of lines <<<
def print_over(s, backup: bool = True, delay: float = 0.2) -> None:
    if backup:
        print('', end='\r')
        print("\033[F" * (s.count('\n')+2))
    print(s)
    sys.stdout.flush()
    time.sleep(delay)
