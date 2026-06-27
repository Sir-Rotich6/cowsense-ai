"""
CowSense AI — Unit Tests
tests/test_agent.py

Tests all 3 features in demo mode (no API keys needed).
Run: pytest tests/test_agent.py -v
"""

import pytest
from app.agent import (
    graphrag_disease_query,
    get_market_price,
    calculate_credit_score,
    get_prioritized_farmers,
    _urgency_label,
)


# ── Health Triage Tests ───────────────────────────────────────────

class TestHealthTriage:

    def test_ecf_from_classic_symptoms(self):
        result = graphrag_disease_query(["high fever", "swollen lymph nodes"])
        assert result["matched"] is True
        assert "East Coast Fever" in result["top_disease"]
        assert result["severity"] == "HIGH"
        assert result["vet_required"] is True
        assert "Buparvaquone" in result["medicine"]

    def test_mastitis_from_udder_symptoms(self):
        result = graphrag_disease_query(["swollen udder", "blood in milk"])
        assert result["matched"] is True
        assert "Mastitis" in result["top_disease"]
        assert result["severity"] == "MEDIUM"
        assert result["vet_required"] is False

    def test_bloat_from_flank_symptom(self):
        result = graphrag_disease_query(["bloated left flank", "grunting"])
        assert result["matched"] is True
        assert "Bloat" in result["top_disease"]
        assert result["severity"] == "HIGH"

    def test_milk_fever_from_postcalving(self):
        result = graphrag_disease_query(["sudden collapse post-calving", "cold ears"])
        assert result["matched"] is True
        assert "Milk Fever" in result["top_disease"]
        assert result["vet_required"] is True

    def test_unknown_symptom_returns_unmatched(self):
        result = graphrag_disease_query(["cow is purple"])
        assert result["matched"] is False

    def test_response_has_required_fields(self):
        result = graphrag_disease_query(["high fever"])
        for field in ["matched", "top_disease", "severity", "vet_required", "medicine", "dosage"]:
            assert field in result


# ── Market Price Tests ────────────────────────────────────────────

class TestMarketPrice:

    def test_nakuru_returns_price(self):
        result = get_market_price("nakuru", 18.0)
        assert result["found"] is True
        assert result["price_kes"] == 52
        assert result["trend"] == "RISING"
        assert result["estimated_revenue_kes"] == 52 * 18.0

    def test_eldoret_returns_price(self):
        result = get_market_price("eldoret", 30.0)
        assert result["found"] is True
        assert result["price_kes"] == 46
        assert result["estimated_revenue_kes"] == 46 * 30.0

    def test_nairobi_highest_price(self):
        nairobi = get_market_price("nairobi", 10.0)
        nakuru  = get_market_price("nakuru", 10.0)
        assert nairobi["price_kes"] >= nakuru["price_kes"]

    def test_best_region_always_returned(self):
        result = get_market_price("embu", 10.0)
        assert result["best_region"] is not None
        assert result["best_price_kes"] is not None

    def test_revenue_calculation_correct(self):
        result = get_market_price("nakuru", 25.0)
        assert result["estimated_revenue_kes"] == result["price_kes"] * 25.0

    def test_case_insensitive_region(self):
        r1 = get_market_price("NAKURU", 10.0)
        r2 = get_market_price("nakuru", 10.0)
        assert r1["price_kes"] == r2["price_kes"]


# ── Credit Profile Tests ──────────────────────────────────────────

class TestCreditProfile:

    def test_f002_is_band_a(self):
        result = calculate_credit_score("F002")
        assert result["found"] is True
        assert result["band"] == "A"
        assert result["max_loan_kes"] == 150_000
        assert result["score"] >= 80

    def test_f003_is_low_score(self):
        result = calculate_credit_score("F003")
        assert result["found"] is True
        assert result["band"] == "D"
        assert result["max_loan_kes"] == 0

    def test_f001_band_a(self):
        result = calculate_credit_score("F001")
        assert result["found"] is True
        assert result["band"] in ["A", "B"]

    def test_unknown_farmer_not_found(self):
        result = calculate_credit_score("F999")
        assert result["found"] is False

    def test_response_has_required_fields(self):
        result = calculate_credit_score("F002")
        for field in ["found", "farmer_name", "score", "band", "max_loan_kes", "breakdown"]:
            assert field in result

    def test_score_within_range(self):
        result = calculate_credit_score("F002")
        assert 0 <= result["score"] <= 100

    def test_band_is_valid(self):
        result = calculate_credit_score("F001")
        assert result["band"] in ["A", "B", "C", "D"]


# ── Prioritization Tests ──────────────────────────────────────────

class TestPrioritization:

    def test_returns_farmers(self):
        result = get_prioritized_farmers("A001")
        assert "farmers" in result
        assert len(result["farmers"]) > 0

    def test_farmers_have_urgency(self):
        result = get_prioritized_farmers("A001")
        for f in result["farmers"]:
            assert f["urgency"] in ["HIGH", "MEDIUM", "LOW"]

    def test_sorted_by_priority_score(self):
        result = get_prioritized_farmers("A001")
        scores = [f["priority_score"] for f in result["farmers"]]
        assert scores == sorted(scores, reverse=True)


# ── Urgency Label Tests ───────────────────────────────────────────

class TestUrgencyLabel:

    def test_high_severity(self):
        label = _urgency_label({"severity": "HIGH"})
        assert "URGENT" in label

    def test_medium_severity(self):
        label = _urgency_label({"severity": "MEDIUM"})
        assert "Act today" in label

    def test_rising_trend(self):
        label = _urgency_label({"trend": "RISING"})
        assert "Sell now" in label

    def test_band_a(self):
        label = _urgency_label({"band": "A"})
        assert "Band A" in label

    def test_none_returns_default(self):
        label = _urgency_label(None)
        assert label != ""
