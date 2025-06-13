import React, { useState } from 'react';
import { Calendar, ChevronLeft, ChevronRight, Plus, Clock, AlertCircle, X } from 'lucide-react';
import { Event } from '../../types';
import { DayScheduleModal } from './DayScheduleModal';

const mockEvents: Event[] = [
  {
    id: '1',
    title: 'Team Meeting',
    description: 'Weekly team sync',
    startTime: new Date(2024, 0, 15, 10, 0),
    endTime: new Date(2024, 0, 15, 11, 0),
    priority: 'high',
    type: 'meeting',
    userId: '1',
  },
  {
    id: '2',
    title: 'Project Deadline',
    description: 'Submit final report',
    startTime: new Date(2024, 0, 16, 17, 0),
    endTime: new Date(2024, 0, 16, 18, 0),
    priority: 'high',
    type: 'deadline',
    userId: '1',
  },
  {
    id: '3',
    title: 'Lunch Break',
    description: 'Team lunch at downtown restaurant',
    startTime: new Date(2024, 0, 15, 12, 0),
    endTime: new Date(2024, 0, 15, 13, 0),
    priority: 'medium',
    type: 'personal',
    userId: '1',
  },
];

export const CalendarView: React.FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events] = useState<Event[]>(mockEvents);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [showDayModal, setShowDayModal] = useState(false);

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days: (Date | null)[] = [];
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }
    
    return days;
  };

  const getEventsForDate = (date: Date) => {
    return events.filter(event => 
      event.startTime.toDateString() === date.toDateString()
    );
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(prev => {
      const newDate = new Date(prev);
      if (direction === 'prev') {
        newDate.setMonth(prev.getMonth() - 1);
      } else {
        newDate.setMonth(prev.getMonth() + 1);
      }
      return newDate;
    });
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const handleDayClick = (day: Date) => {
    setSelectedDate(day);
    setShowDayModal(true);
  };

  const days = getDaysInMonth(currentDate);
  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <>
      <div className="bg-white rounded-xl shadow-lg p-4 lg:p-6">
        {/* Calendar Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 space-y-4 sm:space-y-0">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full flex items-center justify-center">
              <Calendar className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl lg:text-2xl font-bold text-gray-900">
                {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
              </h2>
              <p className="text-gray-600 text-sm lg:text-base">Manage your schedule and deadlines</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => navigateMonth('prev')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200"
            >
              <ChevronLeft className="w-5 h-5 text-gray-600" />
            </button>
            <button
              onClick={() => navigateMonth('next')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200"
            >
              <ChevronRight className="w-5 h-5 text-gray-600" />
            </button>
            <button className="ml-4 px-3 lg:px-4 py-2 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg hover:from-primary-600 hover:to-secondary-600 transition-all duration-200 flex items-center space-x-2">
              <Plus className="w-4 h-4" />
              <span className="hidden sm:inline">Add Event</span>
            </button>
          </div>
        </div>

        {/* Day Names Header */}
        <div className="grid grid-cols-7 gap-1 mb-2">
          {dayNames.map(day => (
            <div key={day} className="p-2 lg:p-3 text-center text-xs lg:text-sm font-semibold text-gray-500">
              <span className="hidden sm:inline">{day}</span>
              <span className="sm:hidden">{day.charAt(0)}</span>
            </div>
          ))}
        </div>

        {/* Calendar Grid */}
        <div className="grid grid-cols-7 gap-1">
          {days.map((day, index) => {
            if (!day) {
              return <div key={index} className="p-2 h-16 lg:h-24"></div>;
            }

            const dayEvents = getEventsForDate(day);
            const isToday = day.toDateString() === new Date().toDateString();

            return (
              <div
                key={index}
                onClick={() => handleDayClick(day)}
                className={`p-1 lg:p-2 h-16 lg:h-24 border border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors duration-200 ${
                  isToday ? 'bg-primary-50 border-primary-200' : ''
                }`}
              >
                <div className={`text-xs lg:text-sm font-semibold mb-1 ${
                  isToday ? 'text-primary-600' : 'text-gray-900'
                }`}>
                  {day.getDate()}
                </div>
                
                <div className="space-y-1">
                  {dayEvents.slice(0, 1).map(event => (
                    <div
                      key={event.id}
                      className="text-xs px-1 lg:px-2 py-1 rounded bg-opacity-20 border-l-2 border-opacity-100"
                      style={{
                        backgroundColor: getPriorityColor(event.priority).replace('bg-', '').replace('-500', '') + '20',
                        borderLeftColor: getPriorityColor(event.priority).replace('bg-', '').replace('-500', '')
                      }}
                    >
                      <div className="flex items-center space-x-1">
                        {event.type === 'deadline' ? (
                          <AlertCircle className="w-2 h-2 lg:w-3 lg:h-3" />
                        ) : (
                          <Clock className="w-2 h-2 lg:w-3 lg:h-3" />
                        )}
                        <span className="truncate text-xs">{event.title}</span>
                      </div>
                    </div>
                  ))}
                  {dayEvents.length > 1 && (
                    <div className="text-xs text-gray-500 px-1 lg:px-2">
                      +{dayEvents.length - 1} more
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Day Schedule Modal */}
      {showDayModal && selectedDate && (
        <DayScheduleModal
          date={selectedDate}
          events={getEventsForDate(selectedDate)}
          onClose={() => setShowDayModal(false)}
        />
      )}
    </>
  );
};