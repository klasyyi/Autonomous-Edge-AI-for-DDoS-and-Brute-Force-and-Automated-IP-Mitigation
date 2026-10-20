import os
import sys
import time
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Models")))
import pure_rf_multi

class TestPureRFModel(unittest.TestCase):
    def test_zero_external_dependencies(self):
        loaded_modules = sys.modules.keys()
        self.assertNotIn("sklearn", loaded_modules)
        self.assertNotIn("scipy", loaded_modules)

    def test_output_vector_structure(self):
        sample_input = [443.0, 695.62, 0.0, 21124.67, 9.0, 316870.0, 56.22, 8192.0]
        output = pure_rf_multi.score(sample_input)
        self.assertIsInstance(output, list)
        self.assertEqual(len(output), 3)
        self.assertAlmostEqual(sum(output), 1.0, places=4)
        for prob in output:
            self.assertGreaterEqual(prob, 0.0)
            self.assertLessEqual(prob, 1.0)

    def test_benign_traffic_detection(self):
        benign_vector = [443.0, 695.62, 0.0, 21124.67, 9.0, 316870.0, 56.22, 8192.0]
        output = pure_rf_multi.score(benign_vector)
        predicted_class = output.index(max(output))
        self.assertEqual(predicted_class, 0)
        self.assertGreater(output[0], 0.90)

    def test_ddos_syn_flood_detection(self):
        ddos_vector = [53058.0, 0.0, 0.0, 5789965.45, 19.0, 115799309.0, 0.0, 5840.0]
        output = pure_rf_multi.score(ddos_vector)
        predicted_class = output.index(max(output))
        self.assertEqual(predicted_class, 1)
        self.assertGreater(output[1], 0.90)

    def test_brute_force_detection(self):
        brute_vector = [21.0, 0.0, 0.0, 24190.0, 1.0, 24190.0, 0.0, 26883.0]
        output = pure_rf_multi.score(brute_vector)
        predicted_class = output.index(max(output))
        self.assertEqual(predicted_class, 2)
        self.assertGreater(output[2], 0.35)

    def test_microsecond_latency_constraint(self):
        sample_input = [443.0, 12.0, 0.0, 50.0, 3.0, 15000.0, 45.0, 29200.0]
        iterations = 5000
        start = time.perf_counter()
        for _ in range(iterations):
            _ = pure_rf_multi.score(sample_input)
        elapsed_sec = time.perf_counter() - start
        avg_latency_ms = (elapsed_sec / iterations) * 1000.0
        self.assertLess(avg_latency_ms, 0.10, f"Latency {avg_latency_ms:.4f} ms exceeded 0.10 ms limit")

if __name__ == "__main__":
    unittest.main()
