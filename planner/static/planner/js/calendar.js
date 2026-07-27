// CALENDAR VIEW SWITCHING
function switchCalendarView(viewType) {
  ['month', 'week', 'day'].forEach(v => {
    const el = document.getElementById(`cal-view-${v}`);
    if (v === viewType) {
      el.classList.remove('d-none');
      el.classList.add('d-block');
    } else {
      el.classList.add('d-none');
      el.classList.remove('d-block');
    }
  });
}
