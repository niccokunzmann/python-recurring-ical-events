"""Check that we are fast when computing."""

import cProfile
import pstats
import sys
from pathlib import Path

import icalendar

import recurring_ical_events

HERE = Path(__file__).parent
CALENDAR_FILE = HERE / "CLN-007.ics"

def profile(name, fn):
    # see https://stackoverflow.com/a/17259420
    pr = cProfile.Profile()
    print(f"profiling {name}")
    pr.enable()
    try:
        result = fn()
    finally:
        pr.disable()
        print(f"writing {name}")
        with Path(HERE/(name+ ".txt")).open("w") as f:
            ps = pstats.Stats(pr, stream=f)
            ps.print_stats()
    return result

calendar = profile("01-calendar", lambda: icalendar.Calendar.from_ical(CALENDAR_FILE.read_bytes()))
query = profile("02-query", lambda: recurring_ical_events.of(calendar))

# profile("03-at-20190304", lambda: query.at("20190304"))
#profile("03-page-20190304", lambda: query.paginate(100, "20190304").generate_next_page())
profile("03-first", lambda: query.first)



# # generate N events
# N = 100
# events = query.paginate(N).generate_next_page()


# print(len(events))
