import React from 'react';

const ConflictsList = ({ conflicts }) => {
  if (!conflicts || conflicts.length === 0) {
    return null;
  }

  const getConflictMessage = (conflict) => {
    switch (conflict.type) {
      case 'lecturer_unavailable':
        return `Lecturer is not available at the selected timeslot`;
      case 'room_over_capacity':
        return `Room capacity (${conflict.capacity}) is less than required (${conflict.required})`;
      case 'lecturer_overlap':
        return `Lecturer has another class at this timeslot`;
      default:
        return 'Unknown conflict';
    }
  };

  return (
    <div className="mt-4">
      <h3 className="text-lg font-semibold text-red-600 mb-2">Conflicts Found:</h3>
      <ul className="list-disc list-inside space-y-2">
        {conflicts.map((conflict, index) => (
          <li key={index} className="text-red-500">
            {getConflictMessage(conflict)}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ConflictsList; 