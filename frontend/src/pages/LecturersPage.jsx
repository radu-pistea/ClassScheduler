import React, { useEffect, useState } from 'react';
import LoadingIndicator from '../components/LoadingIndicator';
import ErrorMessage from '../components/ErrorMessage';

const formatAvailability = (timeslots = []) => {
  // Group timeslots by day
  const grouped = timeslots.reduce((acc, ts) => {
    if (!acc[ts.day]) acc[ts.day] = [];
    acc[ts.day].push(ts);
    return acc;
  }, {});
  // Sort days for display
  const dayOrder = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  return dayOrder
    .filter(day => grouped[day])
    .map(day => (
      <div key={day}>
        <span className="font-semibold">{day}:</span>{' '}
        {grouped[day]
          .map(ts => `${ts.start_time} - ${ts.end_time}`)
          .join(', ')}
      </div>
    ));
};

const LecturersPage = () => {
  const [lecturers, setLecturers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchLecturers = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch('http://localhost:5000/api/lecturers');
        if (!res.ok) throw new Error('Failed to fetch lecturers');
        const data = await res.json();
        setLecturers(data.lecturers || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchLecturers();
  }, []);

  return (
    <div className="container mx-auto max-w-5xl py-8 px-4">
      <h1 className="text-2xl font-bold mb-8">Lecturers</h1>
      <ErrorMessage message={error} />
      {loading ? (
        <LoadingIndicator />
      ) : (
        <section className="overflow-x-auto">
          <table className="min-w-full bg-white border border-gray-200">
            <thead>
              <tr className="bg-gray-100">
                <th className="px-4 py-2 border">Name</th>
                <th className="px-4 py-2 border">Email</th>
                <th className="px-4 py-2 border">Availability</th>
              </tr>
            </thead>
            <tbody>
              {lecturers.map(lecturer => (
                <tr key={lecturer.id} className="hover:bg-blue-50 transition-colors">
                  <td className="px-4 py-2 border font-medium">{lecturer.name}</td>
                  <td className="px-4 py-2 border">{lecturer.email}</td>
                  <td className="px-4 py-2 border">
                    {lecturer.available_timeslots && lecturer.available_timeslots.length > 0 ? (
                      <div className="space-y-1 text-sm">
                        {formatAvailability(lecturer.available_timeslots)}
                      </div>
                    ) : (
                      <span className="text-gray-400">No availability set</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  );
};

export default LecturersPage; 