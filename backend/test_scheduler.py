from app import create_app, db
from app.models.lecturer import Lecturer
from app.models.module import Module
from app.models.room import Room
from app.models.timeslot import Timeslot
from app.models.program_level import ProgramLevel
from scheduler_engine.generator import generate_schedule

def main():
    app = create_app()
    with app.app_context():
        # --- RESET DATABASE ---
        db.drop_all()
        db.create_all()

        # --- SEED DATA ---
        # Program Level
        program_level = ProgramLevel(name="Undergraduate")
        db.session.add(program_level)
        db.session.commit()  # Commit to get the ID

        # Lecturer with availability on Monday and Tuesday mornings
        lecturer = Lecturer(
            name="Lecturer One",
            email="lect1@soloclass.com",
            specialty="Python",
        )
        lecturer.availability = {
            "Monday": ["09:00", "10:00"],
            "Tuesday": ["09:00", "10:00"]
        }
        db.session.add(lecturer)

        # Module (2 weekly hours, linked to program_level)
        module = Module(
            code="PY101",
            name="Intro to Python",
            description="Basics of Python programming.",
            program_level=program_level.name,  # Use the name if that's the field, or program_level.id if it's an FK
            weekly_hours=2
        )
        db.session.add(module)

        # Room
        room = Room(
            name="Room 101",
            capacity=40
        )
        db.session.add(room)

        # Timeslots (Monday 09:00–10:00, 10:00–11:00)
        t1 = Timeslot(day="Monday", start_time="09:00", end_time="10:00", is_weekend=False)
        t2 = Timeslot(day="Monday", start_time="10:00", end_time="11:00", is_weekend=False)
        db.session.add_all([t1, t2])

        db.session.commit()

        # --- RUN SCHEDULER ---
        schedule = generate_schedule()

        # --- PRINT SCHEDULE ---
        print("\nGenerated Schedule:")
        for assignment in schedule:
            print(f"Module: {assignment['module']['name']} | Lecturer: {assignment['lecturer']['name']} | Room: {assignment['room']['name']} | Day: {assignment['timeslot']['day']} | Time: {assignment['timeslot']['start_time']}-{assignment['timeslot']['end_time']}")

if __name__ == "__main__":
    main()
