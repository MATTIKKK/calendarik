import React from 'react';
import { X, Clock, AlertCircle, Calendar, Plus } from 'lucide-react';
import { Event } from '../../types';

interface DayScheduleModalProps {
  date: Date;
  events: Event[];
  onClose: () => void;
}

export const DayScheduleModal: React.FC<DayScheduleModalProps> = ({ date, events, onClose }) => {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'deadline': return AlertCircle;
      case 'meeting': return Calendar;
      default: return Clock;
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const sortedEvents = events.sort((a, b) => a.startTime.getTime() - b.startTime.getTime());

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 animate-fade-in">
      <div className="bg-white rounded-2xl shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-xl font-bold text-gray-900">
              {date.toLocaleDateString('en-US', { 
                weekday: 'long',
                month: 'long',
                day: 'numeric'
              })}
            </h2>
            <p className="text-gray-600 text-sm">
              {events.length} {events.length === 1 ? 'event' : 'events'} scheduled
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200"
          >
            <X className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {/* Events List */}
        <div className="p-6">
          {sortedEvents.length > 0 ? (
            <div className="space-y-4">
              {sortedEvents.map((event) => {
                const Icon = getTypeIcon(event.type);
                return (
                  <div key={event.id} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200">
                    <div className={`w-3 h-3 rounded-full ${getPriorityColor(event.priority)} mt-2 flex-shrink-0`}></div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <Icon className="w-4 h-4 text-gray-600 flex-shrink-0" />
                        <h3 className="font-semibold text-gray-900 truncate">{event.title}</h3>
                      </div>
                      <div className="text-sm text-gray-600 mb-2">
                        {formatTime(event.startTime)} - {formatTime(event.endTime)}
                      </div>
                      {event.description && (
                        <p className="text-sm text-gray-500">{event.description}</p>
                      )}
                      <div className="flex items-center space-x-2 mt-2">
                        <span className={`px-2 py-1 text-xs rounded-full text-white ${getPriorityColor(event.priority)}`}>
                          {event.priority} priority
                        </span>
                        <span className="px-2 py-1 text-xs rounded-full bg-gray-200 text-gray-700 capitalize">
                          {event.type}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-8">
              <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No events scheduled</h3>
              <p className="text-gray-500 mb-4">This day is free for new appointments</p>
              <button className="px-4 py-2 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg hover:from-primary-600 hover:to-secondary-600 transition-all duration-200 flex items-center space-x-2 mx-auto">
                <Plus className="w-4 h-4" />
                <span>Add Event</span>
              </button>
            </div>
          )}
        </div>

        {/* Footer */}
        {events.length > 0 && (
          <div className="p-6 border-t bg-gray-50">
            <button className="w-full px-4 py-2 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg hover:from-primary-600 hover:to-secondary-600 transition-all duration-200 flex items-center justify-center space-x-2">
              <Plus className="w-4 h-4" />
              <span>Add New Event</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};