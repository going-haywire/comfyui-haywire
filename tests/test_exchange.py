# SPDX-License-Identifier: GPL-3.0-or-later
import pytest

from exchange import Exchange

WF = {"1": {"class_type": "HaywireOutput", "inputs": {"name": "Image"}}}


def test_publish_reaches_current_subscribers():
    ex = Exchange()
    ex.subscribe("h1")
    sent = ex.publish("page", "portrait.json", WF)
    assert sent == [("h1", {"publisher": {"name": "portrait.json", "id": "page"}, "workflow": WF})]


def test_new_subscriber_gets_current_workflows():
    ex = Exchange()
    ex.publish("page-a", "a.json", WF)
    ex.publish("page-b", "b.json", WF)
    ex.publish("page-a", "a.json", {})  # replaces page-a's
    sent = ex.subscribe("h1")
    assert [(sid, m["publisher"]["id"], m["workflow"]) for sid, m in sent] == [
        ("h1", "page-a", {}),
        ("h1", "page-b", WF),
    ]


def test_unsubscribe_and_withdraw():
    ex = Exchange()
    ex.subscribe("h1")
    ex.unsubscribe("h1")
    assert ex.publish("page", "x", WF) == []
    ex.withdraw("page")
    assert ex.listing() == []


def test_workflow_must_be_an_object():
    with pytest.raises(ValueError, match="API-format"):
        Exchange().publish("page", "x", ["not", "a", "dict"])
