# Constraints for the scheduler engine

def is_timeslot_available(lecturer, timeslot, current_schedule):
    """
    Returns False if the lecturer is already booked at that timeslot in the current_schedule.
    current_schedule: list of dicts or objects with keys: lecturer, timeslot
    """
    for assignment in current_schedule:
        if assignment['lecturer']['id'] == lecturer['id'] and assignment['timeslot']['id'] == timeslot['id']:
            return False
    return True

def is_room_available(room, timeslot, current_schedule):
    """
    Returns False if the room is already booked at that timeslot in the current_schedule.
    current_schedule: list of dicts or objects with keys: room, timeslot
    """
    for assignment in current_schedule:
        if assignment['room']['id'] == room['id'] and assignment['timeslot']['id'] == timeslot['id']:
            return False
    return True

def is_valid_assignment(lecturer, module, room, timeslot, current_schedule):
    """
    Returns True only if both the lecturer and room are available at the timeslot.
    """
    return is_timeslot_available(lecturer, timeslot, current_schedule) and is_room_available(room, timeslot, current_schedule)
