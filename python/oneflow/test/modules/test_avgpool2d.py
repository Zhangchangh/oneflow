"""
Copyright 2020 The OneFlow Authors. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import unittest

import numpy as np

import oneflow as flow
from oneflow.nn.modules.utils import _pair, _reverse_repeat_tuple, _single, _triple

g_samples = [
    {
        "kernel": (3, 2),
        "padding": 0,
        "stride": (2, 1),
        "in": np.array(
            [
                [
                    [
                        [
                            -0.1953,
                            1.3992,
                            -0.7464,
                            0.691,
                            -1.5484,
                            0.497,
                            1.4963,
                            0.308,
                            -1.473,
                            -0.1238,
                        ],
                        [
                            -0.3532,
                            1.2078,
                            -0.3796,
                            0.7326,
                            -1.5795,
                            0.2128,
                            0.6501,
                            -0.1266,
                            -1.3121,
                            0.1483,
                        ],
                        [
                            -0.3412,
                            -1.6446,
                            -1.0039,
                            -0.5594,
                            0.745,
                            -0.5323,
                            -1.6887,
                            0.2399,
                            1.9422,
                            0.4214,
                        ],
                        [
                            -1.6362,
                            -1.2234,
                            -1.2531,
                            0.6109,
                            0.2228,
                            -0.208,
                            0.6359,
                            0.2451,
                            0.3864,
                            0.4263,
                        ],
                        [
                            0.7053,
                            0.3413,
                            0.909,
                            -0.4057,
                            -0.283,
                            1.0444,
                            -0.2884,
                            0.7638,
                            -1.4793,
                            0.2079,
                        ],
                        [
                            -0.1207,
                            0.8458,
                            -0.9521,
                            0.363,
                            0.1772,
                            0.3945,
                            0.4056,
                            -0.7822,
                            0.6166,
                            1.3343,
                        ],
                        [
                            -0.4115,
                            0.5802,
                            1.2909,
                            1.6508,
                            -0.0561,
                            -0.7964,
                            0.9786,
                            0.4265,
                            0.7262,
                            0.2819,
                        ],
                        [
                            -0.2667,
                            -0.0792,
                            0.4771,
                            0.3248,
                            -0.1313,
                            -0.3325,
                            -0.9973,
                            0.3128,
                            -0.5151,
                            -0.1225,
                        ],
                        [
                            -1.4983,
                            0.2604,
                            -0.9127,
                            0.0822,
                            0.3708,
                            -2.6024,
                            0.2249,
                            -0.75,
                            0.3152,
                            0.1931,
                        ],
                        [
                            -0.2171,
                            -0.2602,
                            0.9051,
                            -0.0933,
                            -0.0902,
                            -1.3837,
                            -1.2519,
                            -1.3091,
                            0.7155,
                            2.3376,
                        ],
                    ]
                ]
            ]
        ),
        "out": np.array(
            [
                [
                    [
                        [
                            0.0121,
                            -0.1946,
                            -0.211,
                            -0.2531,
                            -0.3675,
                            0.1059,
                            0.1465,
                            -0.0703,
                            -0.0662,
                        ],
                        [
                            -0.6331,
                            -0.6458,
                            -0.2837,
                            0.0551,
                            0.1648,
                            -0.1729,
                            -0.0154,
                            0.3497,
                            0.3175,
                        ],
                        [
                            0.3234,
                            0.5025,
                            0.476,
                            0.241,
                            0.0801,
                            0.2897,
                            0.2506,
                            0.0453,
                            0.2813,
                        ],
                        [
                            -0.2359,
                            0.2694,
                            0.4855,
                            0.3735,
                            -0.5913,
                            -0.5875,
                            0.0326,
                            0.0859,
                            0.1465,
                        ],
                    ]
                ]
            ]
        ),
        "ceil_mode": False,
    },
    {
        "in": np.array(
            [
                [
                    [
                        [
                            -0.25874418,
                            -0.735277,
                            0.7187668,
                            0.4317905,
                            -0.15865013,
                            0.32455945,
                            0.91029733,
                            -0.42489085,
                            0.13257249,
                            -0.7680078,
                        ],
                        [
                            -0.48924643,
                            0.41322532,
                            -0.24956563,
                            0.39011025,
                            1.1571697,
                            1.1312183,
                            1.3140937,
                            -0.88671404,
                            -0.73976123,
                            0.09273718,
                        ],
                        [
                            -1.5684161,
                            0.94065344,
                            0.39506504,
                            -0.698693,
                            -0.9967914,
                            -2.0290415,
                            0.98462844,
                            0.7358801,
                            1.1113276,
                            0.6782418,
                        ],
                        [
                            1.4970111,
                            -0.10413595,
                            1.4999448,
                            1.3459393,
                            -0.7604277,
                            1.2852267,
                            0.01842104,
                            -1.2325357,
                            0.44910756,
                            -0.66622615,
                        ],
                        [
                            2.0804522,
                            -0.8352113,
                            -0.63586867,
                            0.16018416,
                            -0.08155673,
                            0.41048485,
                            -1.2774752,
                            -0.24625959,
                            0.06801426,
                            -0.36709896,
                        ],
                        [
                            -2.2077172,
                            0.72850853,
                            0.48929325,
                            0.7826485,
                            1.3427622,
                            -1.1062458,
                            1.2447584,
                            1.87407,
                            1.0484176,
                            -1.321674,
                        ],
                        [
                            1.0160061,
                            0.12091469,
                            -0.80043447,
                            1.3699176,
                            0.83278096,
                            -0.02582553,
                            -0.08430449,
                            -2.1967752,
                            -0.02168749,
                            -2.374834,
                        ],
                        [
                            -0.6146652,
                            -1.5595887,
                            0.10382211,
                            -0.43930522,
                            0.11752917,
                            -0.03595898,
                            -1.216878,
                            2.0072885,
                            0.8048424,
                            2.2326653,
                        ],
                        [
                            0.02489181,
                            0.01249131,
                            0.5591928,
                            0.20447306,
                            1.4736984,
                            0.76396596,
                            -0.90115523,
                            1.0401802,
                            0.22212219,
                            0.15565436,
                        ],
                        [
                            -2.0538027,
                            -1.0389869,
                            -0.94865525,
                            -0.6091378,
                            -0.19524679,
                            -0.50839746,
                            0.4246262,
                            0.0206702,
                            0.62251437,
                            -1.7211599,
                        ],
                    ]
                ]
            ]
        ),
        "out": np.array(
            [
                [
                    [
                        [
                            -0.28296748,
                            0.24714465,
                            0.164579,
                            0.02082263,
                            -0.09525593,
                            0.43929258,
                            0.43888247,
                            -0.01193098,
                            0.08451834,
                        ],
                        [
                            0.3350589,
                            0.21007456,
                            0.34442863,
                            -0.1718909,
                            -0.36201763,
                            -0.10129262,
                            -0.16955681,
                            0.14758904,
                            0.2122277,
                        ],
                        [
                            0.15049218,
                            -0.15546632,
                            0.2276234,
                            0.7344561,
                            0.22873335,
                            -0.13976796,
                            -0.11433101,
                            0.08762991,
                            -0.49481043,
                        ],
                        [
                            -0.16665831,
                            -0.2606004,
                            0.16627766,
                            0.5931824,
                            0.5210317,
                            -0.25002605,
                            -0.22527404,
                            0.30932844,
                            0.16979378,
                        ],
                        [
                            -0.76385164,
                            -0.35398954,
                            -0.19853179,
                            0.2184467,
                            0.38350502,
                            -0.05524013,
                            0.14608034,
                            0.47637174,
                            -0.18021727,
                        ],
                    ]
                ]
            ]
        ),
        "kernel": (3, 2),
        "stride": (2, 1),
        "padding": 0,
        "ceil_mode": True,
    },
]


@flow.unittest.skip_unless_1n1d()
class TestModule(flow.unittest.TestCase):
    def test_AvgPool2d(test_case):
        global g_samples
        for sample in g_samples:
            of_avgpool2d = flow.nn.AvgPool2d(
                kernel_size=sample["kernel"],
                padding=sample["padding"],
                stride=sample["stride"],
                ceil_mode=sample["ceil_mode"],
            )
            x = flow.Tensor(sample["in"])
            of_y = of_avgpool2d(x)
            test_case.assertTrue(of_y.numpy().shape == sample["out"].shape)
            test_case.assertTrue(np.allclose(of_y.numpy(), sample["out"], 0.001, 0.001))


if __name__ == "__main__":
    unittest.main()
