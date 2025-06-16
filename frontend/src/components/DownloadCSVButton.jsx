import React from 'react';
import Papa from 'papaparse';

const DownloadCSVButton = ({ schedule }) => {
  const handleDownload = () => {
    // Prepare data for CSV
    const csvData = schedule.map(entry => ({
      Module: `${entry.module_name} (${entry.module_code})`,
      Lecturer: entry.lecturer_name,
      Room: entry.room_name,
      Day: entry.day,
      'Start Time': entry.start_time,
      'End Time': entry.end_time
    }));

    // Convert to CSV
    const csv = Papa.unparse(csvData);

    // Create blob and download link
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    // Set filename with timestamp
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    link.setAttribute('href', url);
    link.setAttribute('download', `schedule_export_${timestamp}.csv`);
    
    // Trigger download
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <button
      onClick={handleDownload}
      disabled={!schedule || schedule.length === 0}
      className={`
        inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md
        shadow-sm text-white bg-indigo-600 hover:bg-indigo-700
        focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500
        disabled:opacity-50 disabled:cursor-not-allowed
      `}
    >
      <svg 
        className="w-4 h-4 mr-2" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          strokeWidth={2} 
          d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" 
        />
      </svg>
      Export CSV
    </button>
  );
};

export default DownloadCSVButton; 