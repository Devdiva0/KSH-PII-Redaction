import unittest
from pathlib import Path
import redact_pii

class TestPIIDetection(unittest.TestCase):
    def setUp(self):
        self.factory = redact_pii.FakeFactory()

    def test_structured_pii_email(self):
        text = "Please reach out to contact.user@example.com for queries."
        spans = redact_pii.detect_pii(text)
        types = [s.pii_type for s in spans]
        self.assertIn("EMAIL", types)
        redacted, reps = redact_pii.redact_text(text, self.factory)
        self.assertNotIn("contact.user@example.com", redacted)
        self.assertIn("[EMAIL_", redacted)

    def test_structured_pii_phone(self):
        text = "Call us at +91 9876543210 or tel: +1-800-555-0199."
        spans = redact_pii.detect_pii(text)
        types = [s.pii_type for s in spans]
        self.assertIn("PHONE", types)

    def test_structured_pii_ssn(self):
        text = "Social security record: 000-12-3456."
        spans = redact_pii.detect_pii(text)
        types = [s.pii_type for s in spans]
        self.assertIn("SSN", types)

    def test_structured_pii_ip(self):
        text = "Server IP address logged as 192.168.1.100."
        spans = redact_pii.detect_pii(text)
        types = [s.pii_type for s in spans]
        self.assertIn("IP_ADDRESS", types)

    def test_credit_card_luhn_validation(self):
        # Valid Luhn visa test number
        valid_card = "4111 1111 1111 1111"
        self.assertTrue(redact_pii.luhn_ok(valid_card))
        text = f"Payment card used: {valid_card}"
        spans = redact_pii.detect_pii(text)
        types = [s.pii_type for s in spans]
        self.assertIn("CREDIT_CARD", types)

        # Invalid checksum
        invalid_card = "4111 1111 1111 1112"
        self.assertFalse(redact_pii.luhn_ok(invalid_card))

    def test_negative_controls(self):
        # Numeric sequences that are NOT PII
        text = "Order 123456789012, Invoice 2025-12-10, amount 19,282.93, page 417, and ratio 53.97%."
        spans = redact_pii.detect_pii(text)
        # None of these numbers should trigger credit card or SSN
        detected_types = {s.pii_type for s in spans}
        self.assertNotIn("CREDIT_CARD", detected_types)
        self.assertNotIn("SSN", detected_types)

    def test_fake_factory_consistency_and_uniqueness(self):
        factory = redact_pii.FakeFactory()
        fake1 = factory.fake("PERSON", "John Doe")
        fake2 = factory.fake("PERSON", "John Doe")
        fake3 = factory.fake("PERSON", "Jane Smith")
        # Same entity must get identical token
        self.assertEqual(fake1, fake2)
        # Distinct entities must get distinct tokens
        self.assertNotEqual(fake1, fake3)

    def test_company_detection(self):
        text = "Partnered with Tata Consultancy Services Limited and Acme Technologies Private Limited."
        spans = redact_pii.detect_pii(text)
        companies = [text[s.start:s.end] for s in spans if s.pii_type == "COMPANY"]
        self.assertTrue(any("Limited" in c for c in companies))

    def test_normalize_zero_width_space(self):
        text = "Hello\u200bWorld"
        self.assertEqual(redact_pii.normalize(text), "HelloWorld")

    def test_honorific_rule_and_spacy_fallback(self):
        text = "Signed by Mr. Natarajan Chandrasekaran and Ms. Savitha Balachandran."
        spans = redact_pii.detect_pii(text)
        persons = [text[s.start:s.end] for s in spans if s.pii_type == "PERSON"]
        self.assertTrue(any("Natarajan Chandrasekaran" in p for p in persons))
        self.assertTrue(any("Savitha Balachandran" in p for p in persons))

    def test_standalone_first_name_not_overmatched(self):
        # A standalone word like Rohit without honorific or full surname should not trigger PII
        # unless part of full name or honorific
        text = "The system analyzed rohit parameters and performance."
        spans = redact_pii.detect_pii(text)
        self.assertEqual(len(spans), 0)

if __name__ == "__main__":
    unittest.main()
