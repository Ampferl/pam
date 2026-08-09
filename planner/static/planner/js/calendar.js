document.addEventListener('DOMContentLoaded', () => {
  function updateCurrentTimeLine() {
    const timeLines = document.querySelectorAll('.current-time-line');
    if (timeLines.length === 0) return;
    const now = new Date();
    const topPx = (now.getHours() * 60) + now.getMinutes();
    timeLines.forEach(line => {
      line.style.top = `${topPx}px`;
      line.style.display = 'block';
    });
  }
  updateCurrentTimeLine();
  setInterval(updateCurrentTimeLine, 60000);

  // ==========================================
  // CLICK-TO-CREATE
  // ==========================================
  const eventModalEl = document.getElementById('eventModal');
  const createForm = document.getElementById('createEventForm');

  function fmtTime(h, m) {
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
  }

  function openCreateModal({ startDate, endDate, startTime, endTime }) {
    createForm.querySelector('input[name="start_date"]').value = startDate;
    createForm.querySelector('input[name="end_date"]').value = endDate;
    createForm.querySelector('input[name="start_time"]').value = startTime;
    createForm.querySelector('input[name="end_time"]').value = endTime;
    bootstrap.Modal.getOrCreateInstance(eventModalEl).show();
  }

  // Reset the form when the modal is opened via the "+" button,
  // so leftover values from a previous click-to-create don't stick around.
  eventModalEl.addEventListener('show.bs.modal', (event) => {
    if (event.relatedTarget && event.relatedTarget.hasAttribute('data-bs-toggle')) {
      createForm.reset();
    }
  });

  // Week/Day view: click an empty spot in the time grid
  document.querySelectorAll('.cal-day-column').forEach(col => {
    col.addEventListener('click', (e) => {
      if (e.target.closest('.cal-event-abs')) return;

      const rect = col.getBoundingClientRect();
      const offsetY = e.clientY - rect.top;
      const snapTo = 30;

      let startMinutes = Math.round(offsetY / snapTo) * snapTo;
      startMinutes = Math.max(0, Math.min(startMinutes, 1440 - snapTo));
      const endMinutes = Math.min(startMinutes + 60, 1440);

      const date = col.getAttribute('data-date');
      openCreateModal({
        startDate: date,
        endDate: date,
        startTime: fmtTime(Math.floor(startMinutes / 60), startMinutes % 60),
        endTime: fmtTime(Math.floor(endMinutes / 60), endMinutes % 60),
      });
    });
  });

  // Month view: click an empty spot in a day cell
  document.querySelectorAll('.calendar-day').forEach(day => {
    day.addEventListener('click', (e) => {
      if (e.target.closest('.cal-event') || e.target.closest('a')) return;

      const date = day.getAttribute('data-date');
      openCreateModal({
        startDate: date,
        endDate: date,
        startTime: '09:00',
        endTime: '10:00',
      });
    });
  });
});
