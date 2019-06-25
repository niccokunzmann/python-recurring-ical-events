'''
These are tests concerning issue 4
https://github.com/niccokunzmann/python-recurring-ical-events/issues/4
'''
start_date = (2019, 6, 13, 12, 00 ,00 , 00)
end_date = (2019, 6, 13)
a_date = (2019, 6, 13)

def test_between(calendars):
    events = calendars.issue_4.between(start_date, end_date)
    print(events)
    assert False

def test_at(calendars):
    events = calendars.issue_4.at(a_date)
    print(events)
    assert False
    
