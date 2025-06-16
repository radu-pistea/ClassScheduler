import React, { useState } from 'react';
import GenerateButton from '../components/GenerateButton';
import ScheduleTable from '../components/ScheduleTable';
import ConflictsList from '../components/ConflictsList';
import LoadingIndicator from '../components/LoadingIndicator';
import ErrorMessage from '../components/ErrorMessage';

const SchedulePage = () => {
  const [schedule, setSchedule] = useState([]);
  const [conflicts, setConflicts] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:5000/api/schedule/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to generate schedule');
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
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Class Schedule</h1>
        <GenerateButton onClick={handleGenerate} isLoading={isLoading} />
      </div>

      <ErrorMessage message={error} />

      {isLoading ? (
        <LoadingIndicator />
      ) : (
        <>
          <ScheduleTable schedule={schedule} />
          <ConflictsList conflicts={conflicts} />
        </>
      )}
    </div>
  );
};

export default SchedulePage; 