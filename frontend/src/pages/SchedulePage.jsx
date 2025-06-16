import React, { useState, useEffect, useMemo } from 'react';
import GenerateButton from '../components/GenerateButton';
import ScheduleTable from '../components/ScheduleTable';
import CalendarView from '../components/CalendarView';
import ConflictsList from '../components/ConflictsList';
import LoadingIndicator from '../components/LoadingIndicator';
import ErrorMessage from '../components/ErrorMessage';
import FilterBar from '../components/FilterBar';
import DownloadCSVButton from '../components/DownloadCSVButton';

// Mock data for testing
const mockSchedule = [
  {
    id: 1,
    module_id: 101,
    module_name: "Introduction to Computer Science",
    module_code: "CS101",
    lecturer_id: 1,
    lecturer_name: "Dr. Jane Smith",
    room_id: 1,
    room_name: "Room 101",
    day: "Monday",
    start_time: "09:00",
    end_time: "11:00",
    expected_students: 45
  },
  {
    id: 2,
    module_id: 102,
    module_name: "Data Structures",
    module_code: "CS201",
    lecturer_id: 2,
    lecturer_name: "Prof. John Doe",
    room_id: 2,
    room_name: "Room 202",
    day: "Wednesday",
    start_time: "13:00",
    end_time: "15:00",
    expected_students: 35
  }
];

const mockConflicts = [
  {
    type: "room_over_capacity",
    message: "Room 101 is over capacity for CS101 (45 students, capacity: 30)",
    severity: "error",
    affected_entries: [1]
  },
  {
    type: "lecturer_unavailable",
    message: "Dr. Jane Smith is not available on Monday 09:00-11:00",
    severity: "warning",
    affected_entries: [1]
  }
];

const SchedulePage = () => {
  const [schedule, setSchedule] = useState([]);
  const [conflicts, setConflicts] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('calendar'); // 'calendar' or 'table'
  
  // Filter states
  const [selectedRoom, setSelectedRoom] = useState('');
  const [selectedLecturer, setSelectedLecturer] = useState('');
  const [selectedDay, setSelectedDay] = useState('');

  useEffect(() => {
    // Simulate loading state
    setIsLoading(true);
    
    // Simulate API delay
    setTimeout(() => {
      setSchedule(mockSchedule);
      setConflicts(mockConflicts);
      setIsLoading(false);
    }, 1000);
  }, []);

  // Extract unique values for filters
  const { rooms, lecturers, days } = useMemo(() => {
    const uniqueRooms = [...new Set(schedule.map(entry => entry.room_name))].sort();
    const uniqueLecturers = [...new Set(schedule.map(entry => entry.lecturer_name))].sort();
    const uniqueDays = [...new Set(schedule.map(entry => entry.day))].sort();
    
    return {
      rooms: uniqueRooms,
      lecturers: uniqueLecturers,
      days: uniqueDays
    };
  }, [schedule]);

  // Filter the schedule based on selected filters
  const filteredSchedule = useMemo(() => {
    return schedule.filter(entry => {
      const roomMatch = !selectedRoom || entry.room_name === selectedRoom;
      const lecturerMatch = !selectedLecturer || entry.lecturer_name === selectedLecturer;
      const dayMatch = !selectedDay || entry.day === selectedDay;
      
      return roomMatch && lecturerMatch && dayMatch;
    });
  }, [schedule, selectedRoom, selectedLecturer, selectedDay]);

  const handleGenerate = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/schedule/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        credentials: 'include'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to generate schedule');
      }

      const data = await response.json();
      setSchedule(data.schedule);
      setConflicts(data.conflicts);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto max-w-7xl py-8 px-4">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">Class Schedule</h1>
        <div className="flex items-center gap-4">
          <div className="flex rounded-md shadow-sm">
            <button
              onClick={() => setViewMode('calendar')}
              className={`px-4 py-2 text-sm font-medium rounded-l-md ${
                viewMode === 'calendar'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              Calendar
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`px-4 py-2 text-sm font-medium rounded-r-md ${
                viewMode === 'table'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              Table
            </button>
          </div>
          <DownloadCSVButton schedule={filteredSchedule} />
          <GenerateButton onClick={handleGenerate} isLoading={isLoading} disabled={true} />
        </div>
      </div>

      <ErrorMessage message={error} />

      {isLoading ? (
        <LoadingIndicator />
      ) : (
        <>
          <FilterBar
            rooms={rooms}
            lecturers={lecturers}
            days={days}
            selectedRoom={selectedRoom}
            selectedLecturer={selectedLecturer}
            selectedDay={selectedDay}
            onRoomChange={setSelectedRoom}
            onLecturerChange={setSelectedLecturer}
            onDayChange={setSelectedDay}
          />
          
          <section className="mb-8">
            {viewMode === 'calendar' ? (
              <CalendarView schedule={filteredSchedule} />
            ) : (
              <ScheduleTable schedule={filteredSchedule} />
            )}
          </section>
          
          <section>
            <ConflictsList conflicts={conflicts} />
          </section>
        </>
      )}
    </div>
  );
};

export default SchedulePage; 