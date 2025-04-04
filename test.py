import unittest
import time

from pyeuclid.formalization.translation import parse_texts_from_file
from pyeuclid.formalization.state import State
from pyeuclid.engine.engine import Engine

class JGEX_AG_231(unittest.TestCase):
    def test(self):
        texts = parse_texts_from_file('data/JGEX-AG-231.txt')
        for idx, text in enumerate(texts):
            state = State()
            state.load_problem_from_text(text, f'diagrams/JGEX-AG-231/{idx+1}.jpg')
            engine = Engine(state)
            print(state.goal)
            t = time.time()
            engine.search()
            t = time.time() - t
            if state.complete() is not None:
                print(state.complete())
                print(f"Solved in {t} seconds")
            else:
                print(f"Not solved in {t} seconds")
            engine.proof_generartion()
            # results = state.backward(state.goal)
    # def test_single(self):
    #     text = "a b = segment a b; c = s_angle b a c 60; d = foot d a b c; e = foot e b a c; g = circumcenter g b c a; f = on_line f a d, on_line f b e ? cong a f a g"
    #     state = State()
    #     state.load_problem_from_text(text, 'diagrams/JGEX-AG-231/1.jpg')
        

if __name__ == '__main__':
    unittest.main()