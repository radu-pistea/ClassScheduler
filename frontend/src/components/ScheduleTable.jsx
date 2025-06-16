import React from 'react';

const ScheduleTable = ({ schedule }) => {
  if (!schedule || schedule.length === 0) {
    return (
      <div className="text-center text-gray-500 py-4">
        No schedule generated yet
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white border border-gray-200">
        <thead>
          <tr className="bg-gray-100">
            <th className="px-4 py-2 border">Module</th>
            <th className="px-4 py-2 border">Lecturer</th>
            <th className="px-4 py-2 border">Room</th>
            <th className="px-4 py-2 border">Day</th>
            <th className="px-4 py-2 border">Time</th>
          </tr>
        </thead>
        <tbody>
          {schedule.map((entry) => (
            <tr key={entry.id} className="hover:bg-gray-50">
              <td className="px-4 py-2 border">{entry.module?.name || 'N/A'}</td>
              <td className="px-4 py-2 border">{entry.lecturer?.name || 'N/A'}</td>
              <td className="px-4 py-2 border">{entry.room?.name || 'N/A'}</td>
              <td className="px-4 py-2 border">{entry.timeslot?.day || 'N/A'}</td>
              <td className="px-4 py-2 border">
                {entry.timeslot
                  ? `${entry.timeslot.start_time} - ${entry.timeslot.end_time}`
                  : 'N/A'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ScheduleTable; 