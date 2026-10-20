import unittest
import time

WHITELIST_IPS = {"192.168.137.1", "192.168.10.1", "127.0.0.1", "8.8.8.8", "1.1.1.1", "255.255.255.255"}
BLOCK_TTL_SECONDS = 300
MAX_BLOCKED_RULES = 500
FLOW_TTL_SECONDS = 60

class MitigationEngine:
    def __init__(self):
        self.blocked_ips = set()
        self.blocked_ip_timestamps = {}
        self.active_flows = {}

    def apply_mitigation(self, target_ip, threat_type, reason_text):
        if target_ip in WHITELIST_IPS or target_ip in self.blocked_ips:
            return False

        current_time = time.time()
        if len(self.blocked_ips) >= MAX_BLOCKED_RULES:
            oldest_ip = min(self.blocked_ip_timestamps, key=self.blocked_ip_timestamps.get)
            self.blocked_ips.discard(oldest_ip)
            del self.blocked_ip_timestamps[oldest_ip]

        self.blocked_ips.add(target_ip)
        self.blocked_ip_timestamps[target_ip] = current_time
        return True

    def evict_expired_blocks(self, current_time=None):
        if current_time is None:
            current_time = time.time()
        expired = [ip for ip, btime in self.blocked_ip_timestamps.items() if current_time - btime > BLOCK_TTL_SECONDS]
        for ip in expired:
            self.blocked_ips.discard(ip)
            del self.blocked_ip_timestamps[ip]
        return len(expired)

    def evict_stale_flows(self, current_time=None):
        if current_time is None:
            current_time = time.time()
        stale = [k for k, v in self.active_flows.items() if current_time - v['last_time'] > FLOW_TTL_SECONDS]
        for k in stale:
            del self.active_flows[k]
        return len(stale)


class TestMitigationSafety(unittest.TestCase):
    def setUp(self):
        self.engine = MitigationEngine()

    def test_whitelist_protection(self):
        for protected_ip in ["192.168.137.1", "127.0.0.1", "8.8.8.8", "1.1.1.1"]:
            blocked = self.engine.apply_mitigation(protected_ip, "DDoS", "Test Attack")
            self.assertFalse(blocked, f"Whitelisted IP {protected_ip} was blocked!")
            self.assertNotIn(protected_ip, self.engine.blocked_ips)

    def test_malicious_ip_blocked(self):
        attacker_ip = "10.0.0.99"
        blocked = self.engine.apply_mitigation(attacker_ip, "DDoS", "SYN Flood")
        self.assertTrue(blocked)
        self.assertIn(attacker_ip, self.engine.blocked_ips)

    def test_maximum_rule_ceiling(self):
        for i in range(MAX_BLOCKED_RULES + 50):
            ip = f"172.16.0.{i % 250}_{i}"
            self.engine.apply_mitigation(ip, "DDoS", "Volumetric Flood")
            self.assertLessEqual(len(self.engine.blocked_ips), MAX_BLOCKED_RULES)

    def test_block_ttl_auto_unblock(self):
        attacker_ip = "198.51.100.42"
        t0 = 1000.0
        self.engine.blocked_ips.add(attacker_ip)
        self.engine.blocked_ip_timestamps[attacker_ip] = t0

        unblocked_count = self.engine.evict_expired_blocks(current_time=t0 + 299)
        self.assertEqual(unblocked_count, 0)
        self.assertIn(attacker_ip, self.engine.blocked_ips)

        unblocked_count = self.engine.evict_expired_blocks(current_time=t0 + 301)
        self.assertEqual(unblocked_count, 1)
        self.assertNotIn(attacker_ip, self.engine.blocked_ips)

    def test_flow_table_ttl_eviction(self):
        t0 = 2000.0
        self.engine.active_flows["flow1"] = {"last_time": t0}
        self.engine.active_flows["flow2"] = {"last_time": t0 + 50}

        evicted = self.engine.evict_stale_flows(current_time=t0 + 55)
        self.assertEqual(evicted, 0)
        self.assertEqual(len(self.engine.active_flows), 2)

        evicted = self.engine.evict_stale_flows(current_time=t0 + 61)
        self.assertEqual(evicted, 1)
        self.assertNotIn("flow1", self.engine.active_flows)
        self.assertIn("flow2", self.engine.active_flows)

if __name__ == "__main__":
    unittest.main()
