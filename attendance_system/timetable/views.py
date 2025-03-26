from django.shortcuts import render
import csv
import io
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import TimeTable, AttendanceSession
from .forms import TimeTableUploadForm
from django.conf import settings
import random
import firebase_admin
from firebase_admin import credentials, db
from firebase_admin.exceptions import FirebaseError
from django.http import JsonResponse
from django.utils import timezone



def upload_timetable(request):

    if request.method == "POST":
        form = TimeTableUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES["csv_file"]

            # Make sure to handle the file properly
            try:
                # Read the file content and decode it
                file_content = csv_file.read().decode("utf-8")

                # Create a CSV reader from the content
                reader = csv.reader(file_content.splitlines())

                # Convert to list to safely access rows
                rows = list(reader)

                # Check if there are enough rows
                if len(rows) < 1:
                    form.add_error("file", "The CSV file does not contain enough data.")
                    return render(request, "timetable/upload.html", {"form": form})

                # Now we can safely get the first row
                time_slots = rows[0][
                    1:
                ]  # First row should be time slots (8am-9am, etc.)

                # Process the rest of the rows (days of the week)
                timetable_data = {}
                for row in rows[1:]:
                    if (
                        row and len(row) > 1
                    ):  # Make sure the row is not empty and has enough columns
                        day = row[0]
                        classes = row[
                            1 : len(time_slots) + 1
                        ]  # Ensure we only take as many classes as we have time slots
                        # Pad with empty strings if needed
                        while len(classes) < len(time_slots):
                            classes.append("")
                        timetable_data[day] = dict(zip(time_slots, classes))

                # Store the timetable data in the session
                request.session["timetable_data"] = timetable_data
                request.session["time_slots"] = time_slots

                print("Storing in session - timetable_data:", timetable_data)
                print("Storing in session - time_slots:", time_slots)

                # Redirect to the next step or display the timetable
                return redirect("display_timetable")

            except Exception as e:
                form.add_error(None, f"Error processing CSV file: {str(e)}")
                return render(request, "timetable/upload.html", {"form": form})
    else:
        form = TimeTableUploadForm()

    return render(request, "timetable/upload.html", {"form": form})


def display_timetable(request):
    timetable_data = request.session.get("timetable_data", {})
    time_slots = request.session.get("time_slots", [])

    print("Raw timetable_data:", timetable_data)
    print("Time slots:", time_slots)

    # Transform the data to match the template's expected format
    formatted_data = []
    for day, classes_dict in timetable_data.items():
        classes_list = [classes_dict.get(slot, "") for slot in time_slots]
        formatted_data.append({"day": day, "classes": classes_list})

    print("Formatted data for template:", formatted_data)

    return render(
        request,
        "timetable/display.html",
        {"timetable_data": formatted_data, "time_slots": time_slots},
    )


def select_class(request, day, time_slot_index):
    timetable_data = request.session.get("timetable_data", {})
    time_slots = request.session.get("time_slots", [])

    # Check if the day exists in the timetable data
    if day in timetable_data and 0 <= time_slot_index < len(time_slots):
        time_slot = time_slots[time_slot_index]
        class_name = timetable_data[day].get(time_slot, "")

        return render(
            request,
            "timetable/select_duration.html",
            {"day": day, "time_slot": time_slot, "class_name": class_name},
        )

    messages.error(request, "Invalid class selection")
    return redirect("display_timetable")


# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred, {"databaseURL": settings.FIREBASE_DATABASE_URL})


def start_attendance(request, day, time_slot, class_name, duration):
    # Generate a random number for display
    display_number = random.randint(1000, 9999)

    # Generate 5 other random numbers
    other_numbers = []
    while len(other_numbers) < 5:
        num = random.randint(1000, 9999)
        if num != display_number and num not in other_numbers:
            other_numbers.append(num)

    # Create a timestamp for the session
    timestamp = timezone.now().strftime("%Y%m%d%H%M")

    # Create a reference in Firebase
    session_ref = db.reference(f"attendance_sessions/{timestamp}")

    print(f"Firebase Database URL: {settings.FIREBASE_DATABASE_URL}")
    print(f"Attempting to access Firebase path: attendance_sessions/{timestamp}")

    try:
        # Test if we can access the root reference first
        root_ref = db.reference("/")
        print("Root reference accessible:", root_ref.get())

        # Push data to Firebase
        session_data = {
            "teacher_number": display_number,
            "other_numbers": other_numbers,
            "day": day,
            "time_slot": time_slot,
            "class_name": class_name,
            "duration": duration,
            "timestamp": timestamp,
            "status": "active",
        }
        print("Attempting to set data:", session_data)

        session_ref.set(session_data)
        print("Firebase data set successfully")

        # Save attendance session in database
        attendance_session = AttendanceSession.objects.create(
            day=day,
            time_slot=time_slot,
            class_name=class_name,
            display_number=display_number,
            duration=duration,
        )
        print("Attendance session saved to local database")

        return render(
            request,
            "timetable/display_number.html",
            {
                "display_number": display_number,
                "timestamp": timestamp,
                "duration": duration,
            },
        )
    except FirebaseError as e:
        print(f"Firebase error details: {str(e)}")
        messages.error(request, f"Error connecting to Firebase: {str(e)}")
        return redirect("display_timetable")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        messages.error(request, f"Unexpected error: {str(e)}")
        return redirect("display_timetable")


def end_attendance(request, timestamp):
    # Update status in Firebase
    session_ref = db.reference(f"attendance_sessions/{timestamp}")

    try:
        session_ref.update({"status": "completed"})

        return render(request, "timetable/attendance_complete.html")
    except FirebaseError as e:
        messages.error(request, f"Error connecting to Firebase: {str(e)}")
        return redirect("display_timetable")


def attendance_archives(request):
    try:
        # Get all attendance sessions from Firebase
        attendance_ref = db.reference("attendance_records")
        attendance_data = attendance_ref.get()

        if not attendance_data:
            attendance_data = {}

        # Organize data for display
        organized_data = []
        for session_id, session_data in attendance_data.items():
            session_info = db.reference(f"attendance_sessions/{session_id}").get()
            if session_info:
                present_count = sum(
                    1
                    for status in session_data.values()
                    if status.get("status") == "present"
                )
                total_count = len(session_data)

                organized_data.append(
                    {
                        "day": session_info.get("day", "Unknown"),
                        "time_slot": session_info.get("time_slot", "Unknown"),
                        "class_name": session_info.get("class_name", "Unknown"),
                        "date": session_info.get("timestamp", "").split("T")[0],
                        "present_count": present_count,
                        # "section": session_info.get("section", "Unknown"),
                        "total_count": total_count,
                        "attendance_percentage": (
                            round(present_count / total_count * 100, 2)
                            if total_count > 0
                            else 0
                        ),
                    }
                )

        return render(
            request, "timetable/archives.html", {"attendance_data": organized_data}
        )
    except FirebaseError as e:
        messages.error(request, f"Error connecting to Firebase: {str(e)}")
        return redirect("display_timetable")


def test_firebase(request):
    try:
        # Try to write to a test location
        test_ref = db.reference("/test")
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        test_ref.set({"timestamp": timestamp, "test": "data"})

        # Try to read it back
        result = test_ref.get()

        return JsonResponse(
            {
                "success": True,
                "message": "Firebase connection successful",
                "wrote": {"timestamp": timestamp, "test": "data"},
                "read": result,
            }
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "error": str(e), "error_type": type(e).__name__}
        )
