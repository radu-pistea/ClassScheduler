import React from 'react';

const FilterBar = ({ 
  rooms, 
  lecturers, 
  days, 
  selectedRoom, 
  selectedLecturer, 
  selectedDay,
  onRoomChange,
  onLecturerChange,
  onDayChange
}) => {
  return (
    <div className="flex flex-wrap gap-4 mb-6">
      <div className="flex-1 min-w-[200px]">
        <label htmlFor="room-filter" className="block text-sm font-medium text-gray-700 mb-1">
          Room
        </label>
        <select
          id="room-filter"
          value={selectedRoom}
          onChange={(e) => onRoomChange(e.target.value)}
          className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        >
          <option value="">All Rooms</option>
          {rooms.map((room) => (
            <option key={room} value={room}>
              {room}
            </option>
          ))}
        </select>
      </div>

      <div className="flex-1 min-w-[200px]">
        <label htmlFor="lecturer-filter" className="block text-sm font-medium text-gray-700 mb-1">
          Lecturer
        </label>
        <select
          id="lecturer-filter"
          value={selectedLecturer}
          onChange={(e) => onLecturerChange(e.target.value)}
          className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        >
          <option value="">All Lecturers</option>
          {lecturers.map((lecturer) => (
            <option key={lecturer} value={lecturer}>
              {lecturer}
            </option>
          ))}
        </select>
      </div>

      <div className="flex-1 min-w-[200px]">
        <label htmlFor="day-filter" className="block text-sm font-medium text-gray-700 mb-1">
          Day
        </label>
        <select
          id="day-filter"
          value={selectedDay}
          onChange={(e) => onDayChange(e.target.value)}
          className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        >
          <option value="">All Days</option>
          {days.map((day) => (
            <option key={day} value={day}>
              {day}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default FilterBar; 