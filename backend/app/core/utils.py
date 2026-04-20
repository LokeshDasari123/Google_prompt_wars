def format_meetups(meetups):
    return [f"{m.title}: {m.description}" for m in meetups]