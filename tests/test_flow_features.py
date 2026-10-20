import unittest
import math

FEATURE_NAMES = [
    "Destination Port",
    "Bwd Packet Length Std",
    "SYN Flag Count",
    "Flow IAT Mean",
    "Total Fwd Packets",
    "Flow Duration",
    "Fwd Packet Length Mean",
    "Init_Win_bytes_forward"
]

def build_feature_vector(flow, current_time):
    flow_duration = (current_time - flow['start_time']) * 1000000.0
    iat_mean = (flow['iat_sum'] / flow['iat_count']) * 1000000.0 if flow['iat_count'] > 0 else 0.0
    fwd_len_mean = flow['fwd_length_sum'] / flow['fwd_packets'] if flow['fwd_packets'] > 0 else 0.0

    if len(flow['bwd_lengths']) > 1:
        mean = sum(flow['bwd_lengths']) / len(flow['bwd_lengths'])
        variance = sum((x - mean) ** 2 for x in flow['bwd_lengths']) / len(flow['bwd_lengths'])
        bwd_len_std = math.sqrt(variance)
    else:
        bwd_len_std = 0.0

    return [
        float(flow['destination_port']),
        float(bwd_len_std),
        float(flow['syn_count']),
        float(iat_mean),
        float(flow['fwd_packets']),
        float(flow_duration),
        float(fwd_len_mean),
        float(flow['init_win_bytes_fwd'])
    ]

class TestFlowFeatures(unittest.TestCase):
    def test_feature_vector_dimension(self):
        flow = {
            'destination_port': 80,
            'start_time': 100.0,
            'iat_sum': 0.05,
            'iat_count': 5,
            'fwd_packets': 5,
            'fwd_length_sum': 250,
            'bwd_lengths': [40, 60, 80],
            'syn_count': 1,
            'init_win_bytes_fwd': 8192
        }
        vec = build_feature_vector(flow, current_time=100.1)
        self.assertEqual(len(vec), 8)
        self.assertEqual(len(vec), len(FEATURE_NAMES))
        for val in vec:
            self.assertIsInstance(val, float)

    def test_zero_packets_safe_division(self):
        flow = {
            'destination_port': 22,
            'start_time': 500.0,
            'iat_sum': 0.0,
            'iat_count': 0,
            'fwd_packets': 0,
            'fwd_length_sum': 0,
            'bwd_lengths': [],
            'syn_count': 0,
            'init_win_bytes_fwd': 0
        }
        vec = build_feature_vector(flow, current_time=500.0)
        self.assertEqual(vec[3], 0.0)
        self.assertEqual(vec[6], 0.0)
        self.assertEqual(vec[1], 0.0)

    def test_bwd_packet_length_std_calculation(self):
        flow = {
            'destination_port': 443,
            'start_time': 10.0,
            'iat_sum': 0.01,
            'iat_count': 1,
            'fwd_packets': 1,
            'fwd_length_sum': 100,
            'bwd_lengths': [100, 100, 100],
            'syn_count': 0,
            'init_win_bytes_fwd': 65535
        }
        vec = build_feature_vector(flow, current_time=10.05)
        self.assertAlmostEqual(vec[1], 0.0, places=4)

if __name__ == "__main__":
    unittest.main()
