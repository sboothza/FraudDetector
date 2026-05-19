import json

import pytest

from exceptions import BadRequestError
from models.rule import Rule


def test_get_rule_raises_bad_request_for_invalid_json_parameters():
    rule = Rule()
    rule.id = 3
    rule.type_name = "rules.value_rule.ValueRule"
    rule.parameters = "not-json"

    with pytest.raises(BadRequestError) as exc_info:
        rule.get_rule()

    assert exc_info.value.code == 400
    assert exc_info.value.data["rule_id"] == 3


def test_get_rule_raises_bad_request_for_non_object_parameters():
    rule = Rule()
    rule.id = 4
    rule.type_name = "rules.value_rule.ValueRule"
    rule.parameters = json.dumps(["not", "a", "dict"])

    with pytest.raises(BadRequestError) as exc_info:
        rule.get_rule()

    assert exc_info.value.code == 400
    assert "JSON object" in exc_info.value.message
