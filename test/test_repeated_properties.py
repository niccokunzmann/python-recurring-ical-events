def test_duplicated_rrule(calendars):
    # Test that a repetition of the same `RRULE` property should be ignored
    assert len(calendars.duplicated_rrule.at(2023)) == 20
