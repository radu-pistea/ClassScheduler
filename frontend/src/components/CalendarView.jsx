import React from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';

const CalendarView = ({ schedule }) => {
  // Convert schedule entries to FullCalendar events
  const events = schedule.map(entry => ({
    id: entry.id,
    title: `${entry.module_name} (${entry.module_code})`,
    start: `${entry.day}T${entry.start_time}`,
    end: `${entry.day}T${entry.end_time}`,
    extendedProps: {
      room: entry.room_name,
      lecturer: entry.lecturer_name
    }
  }));

  // Custom event rendering
  const renderEventContent = (eventInfo) => {
    return (
      <div className="p-1 text-xs">
        <div className="font-semibold truncate">{eventInfo.event.title}</div>
        <div className="text-gray-600 truncate">
          {eventInfo.event.extendedProps.room}
        </div>
        <div className="text-gray-600 truncate">
          {eventInfo.event.extendedProps.lecturer}
        </div>
      </div>
    );
  };

  return (
    <div className="calendar-container h-[600px]">
      <FullCalendar
        plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
        initialView="timeGridWeek"
        headerToolbar={{
          left: 'prev,next today',
          center: 'title',
          right: 'dayGridMonth,timeGridWeek,timeGridDay'
        }}
        slotMinTime="08:00:00"
        slotMaxTime="20:00:00"
        allDaySlot={false}
        events={events}
        eventContent={renderEventContent}
        height="100%"
        slotDuration="00:30:00"
        slotLabelInterval="01:00"
        expandRows={true}
        stickyHeaderDates={true}
        dayHeaderFormat={{ weekday: 'long' }}
        eventTimeFormat={{
          hour: '2-digit',
          minute: '2-digit',
          hour12: false
        }}
      />
    </div>
  );
};

export default CalendarView; 