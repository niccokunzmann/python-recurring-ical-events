
def test_date_events_can_be_used(calendars):
    events = calendars.Germany.between("20140511T000000Z", "20140511T000000Z")
    assert len(events) == 1
    assert events[0]["SUMMARY"] == "Germany: Mother's Day [Not a public holiday]"
