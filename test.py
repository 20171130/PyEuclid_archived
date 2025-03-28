import unittest

from pyeuclid.formalization.translation import translate_from_ddar, translate_from_file
from pyeuclid.formalization.diagram import Diagram
# from pyeuclid.formalization.state import State

class JGEX_AG_231(unittest.TestCase):
    def test(self):
        texts = translate_from_file('data/jgex_ag_231.txt')
        for idx, text in enumerate(texts):
            constructions_list = translate_from_ddar(text)
            try:
                diagram = Diagram(constructions_list)
            except:
                print(idx)
                input()
            print(diagram.points)
    
    # def test_single(self):
    #     text = "a b = segment a b; c = s_angle b a c 60; d = foot d a b c; e = foot e b a c; g = circumcenter g b c a; f = on_line f a d, on_line f b e ? cong a f a g"
    #     constructions_list = translate_from_ddar(text)
    #     try:
    #         diagram = Diagram(constructions_list)
    #     except:
    #         assert False

if __name__ == '__main__':
    unittest.main()