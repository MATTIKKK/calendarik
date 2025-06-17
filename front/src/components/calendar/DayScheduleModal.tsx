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
      case 'high': return 'bg-[var(--color-accent-dark)]';
      case 'medium': return 'bg-[var(--color-secondary)]';
      case 'low': return 'bg-[var(--color-primary-dark)]';
      default: return 'bg-[var(--color-text-light)]';
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
      <div className="bg-[var(--color-bg)] rounded-2xl shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-xl font-bold text-[var(--color-text)]">
              {date.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
            </h2>
            <p className="text-[var(--color-text-light)] text-sm">
              {events.length} {events.length === 1 ? 'event' : 'events'} scheduled
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-[var(--color-primary-light)] rounded-lg transition-colors duration-200"
          >
            <X className="w-5 h-5 text-[var(--color-text-light)]" />
          </button>
        </div>

        {/* Events List */}
        <div className="p-6">
          {sortedEvents.length > 0 ? (
            <div className="space-y-4">
              {sortedEvents.map((event) => {
                const Icon = getTypeIcon(event.type);
                return (
                  <div key={event.id} className="flex items-start space-x-4 p-4 bg-[var(--color-bg-gradient-middle)] rounded-lg hover:bg-[var(--color-bg-gradient-start)] transition-colors duration-200">
                    <div className={`w-3 h-3 rounded-full ${getPriorityColor(event.priority)} mt-2 flex-shrink-0`}></div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <Icon className="w-4 h-4 text-[var(--color-text-light)] flex-shrink-0" />
                        <h3 className="font-semibold text-[var(--color-text)] truncate">{event.title}</h3>
                      </div>
                      <div className="text-sm text-[var(--color-text-light)] mb-2">
                        {formatTime(event.startTime)} - {formatTime(event.endTime)}
                      </div>
                      {event.description && (
                        <p className="text-sm text-[var(--color-text-light)]">{event.description}</p>
                      )}
                      <div className="flex items-center space-x-2 mt-2">
                        <span className={`px-2 py-1 text-xs rounded-full text-white ${getPriorityColor(event.priority)}`}>
                          {event.priority} priority
                        </span>
                        <span className="px-2 py-1 text-xs rounded-full bg-[var(--color-secondary-light)] text-[var(--color-secondary-dark)] capitalize">
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
              <Calendar className="w-12 h-12 text-[var(--color-secondary-light)] mx-auto mb-4" />
              <h3 className="text-lg font-medium text-[var(--color-text)] mb-2">No events scheduled</h3>
              <p className="text-[var(--color-text-light)] mb-4">This day is free for new appointments</p>
              <button className="px-4 py-2 bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-secondary)] text-white rounded-lg hover:opacity-90 transition-all duration-200 flex items-center space-x-2 mx-auto">
                <Plus className="w-4 h-4" />
                <span>Add Event</span>
              </button>
            </div>
          )}
        </div>

        {/* Footer */}
        {events.length > 0 && (
          <div className="p-6 border-t bg-[var(--color-bg-gradient-end)]">
            <button className="w-full px-4 py-2 bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-secondary)] text-white rounded-lg hover:opacity-90 transition-all duration-200 flex items-center justify-center space-x-2">
              <Plus className="w-4 h-4" />
              <span>Add New Event</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};