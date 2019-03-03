
def test_one_deleted_event(calendars):
    events = calendars.each_week_but_one_deleted.all()
    assert len(events) == 7

def test_one_deleted_event(calendars):
    events = calendars.each_week_but_two_deleted.all()
    assert len(events) == 6
