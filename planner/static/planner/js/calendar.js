document.addEventListener('DOMContentLoaded', () => {
  // ==========================================
  // 1. EXISTING MODAL & TIMELINE LOGIC
  // ==========================================
  const editModal = document.getElementById('editEventModal');
  if (editModal) {
    editModal.addEventListener('show.bs.modal', event => {
      const button = event.relatedTarget; 
      
      // Prevent modal from opening if we were just dragging/resizing
      if (!button.hasAttribute('data-bs-toggle')) return event.preventDefault();

      const eventId = button.getAttribute('data-id');
      document.getElementById('editEventForm').action = `/planner/event/update/${eventId}/`;
      document.getElementById('editTitle').value = button.getAttribute('data-title');
      document.getElementById('editStartDate').value = button.getAttribute('data-startdate');
      document.getElementById('editStartTime').value = button.getAttribute('data-starttime');
      document.getElementById('editEndDate').value = button.getAttribute('data-enddate');
      document.getElementById('editEndTime').value = button.getAttribute('data-endtime');
      document.getElementById('editCategory').value = button.getAttribute('data-category');
      document.getElementById('editDescription').value = button.getAttribute('data-description');
    });
  }

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

  // Prevent text highlighting when interacting with events
  document.querySelectorAll('.cal-event-abs').forEach(el => {
    el.style.userSelect = 'none';
    el.style.webkitUserSelect = 'none';
  });

  // ==========================================
  // 2. CREATING NEW EVENT LOGIC (DRAG ON EMPTY SPACE)
  // ==========================================
  const dayColumns = document.querySelectorAll('.cal-day-column');
  let isCreating = false;
  let createStartY = 0;
  let createCurrentY = 0;
  let activeCol = null;
  let selectionBox = null;
  let selectedDate = null;

  dayColumns.forEach(col => {
    col.addEventListener('mousedown', (e) => {
      if (e.target.closest('.cal-event-abs')) return;
      e.preventDefault(); 

      isCreating = true;
      activeCol = col;
      selectedDate = col.getAttribute('data-date');
      const rect = col.getBoundingClientRect();
      createStartY = e.clientY - rect.top;
      createCurrentY = createStartY;

      selectionBox = document.createElement('div');
      selectionBox.classList.add('position-absolute', 'w-100', 'bg-primary', 'rounded');
      selectionBox.style.opacity = '0.4';
      selectionBox.style.zIndex = '5';
      selectionBox.style.left = '0';
      selectionBox.style.top = `${createStartY}px`;
      selectionBox.style.height = '0px';
      selectionBox.style.pointerEvents = 'none';

      col.appendChild(selectionBox);
    });
  });

  // ==========================================
  // 3. EVENT DRAG & RESIZE LOGIC
  // ==========================================
  let activeEvent = null;
  let actionType = null; // 'drag-pending', 'drag', 'resize-top', 'resize-bottom'
  let eventStartY = 0;
  let eventStartTop = 0;
  let eventStartHeight = 0;
  let initialClickX = 0;
  let initialClickY = 0;
  const snapTo = 15; 

  document.addEventListener('mousedown', (e) => {
    const eventBlock = e.target.closest('.cal-event-abs');
    if (!eventBlock) return; 
    
    initialClickX = e.clientX;
    initialClickY = e.clientY;
    eventStartY = e.clientY;
    eventStartTop = parseInt(eventBlock.style.top || eventBlock.offsetTop);
    eventStartHeight = parseInt(eventBlock.style.height || eventBlock.offsetHeight);
    activeEvent = eventBlock;
    
    const isTopResize = !!e.target.closest('.resize-handle-top');
    const isBottomResize = !!e.target.closest('.resize-handle-bottom');
    
    if (isTopResize || isBottomResize) {
      // RESIZE: Grab instantly
      e.preventDefault();
      actionType = isTopResize ? 'resize-top' : 'resize-bottom';
      activeEvent.removeAttribute('data-bs-toggle');
      activeEvent.style.opacity = '0.7';
      activeEvent.style.zIndex = '50';
    } else {
      // DRAG: Mark as pending. We will check if they actually move the mouse before triggering.
      actionType = 'drag-pending';
    }
  });

  document.addEventListener('mousemove', (e) => {
    // A) Creating Event Math
    if (isCreating && activeCol && selectionBox) {
      const rect = activeCol.getBoundingClientRect();
      createCurrentY = Math.max(0, Math.min(e.clientY - rect.top, rect.height));
      const top = Math.min(createStartY, createCurrentY);
      const height = Math.abs(createCurrentY - createStartY);
      selectionBox.style.top = `${top}px`;
      selectionBox.style.height = `${height}px`;
    }

    // B) Dragging/Resizing Event Math
    if (activeEvent) {
      const deltaY = e.clientY - eventStartY;

      // 1. Upgrade 'drag-pending' to 'drag' if mouse moves more than 3px
      if (actionType === 'drag-pending') {
        const moveX = Math.abs(e.clientX - initialClickX);
        const moveY = Math.abs(e.clientY - initialClickY);
        
        if (moveX > 3 || moveY > 3) {
          actionType = 'drag';
          activeEvent.removeAttribute('data-bs-toggle');
          activeEvent.style.opacity = '0.8';
          activeEvent.style.transform = 'scale(1.02)';
          activeEvent.style.boxShadow = '0 6px 12px rgba(0,0,0,0.3)';
          activeEvent.style.zIndex = '50';
          activeEvent.style.pointerEvents = 'none'; // Temporarily ignore mouse so we can detect columns
        } else {
          return; // Haven't moved far enough to qualify as a drag yet
        }
      }

      // 2. Perform actions based on type
      if (actionType === 'resize-bottom') {
        let newHeight = eventStartHeight + deltaY;
        newHeight = Math.max(snapTo, Math.round(newHeight / snapTo) * snapTo);
        activeEvent.style.height = `${newHeight}px`;
      } 
      else if (actionType === 'resize-top') {
        let rawNewTop = eventStartTop + deltaY;
        let snappedTop = Math.max(0, Math.round(rawNewTop / snapTo) * snapTo);
        
        let topDiff = snappedTop - eventStartTop;
        let newHeight = eventStartHeight - topDiff;
        
        // Prevent inverting the event
        if (newHeight < snapTo) {
          newHeight = snapTo;
          snappedTop = eventStartTop + eventStartHeight - snapTo;
        }
        
        activeEvent.style.top = `${snappedTop}px`;
        activeEvent.style.height = `${newHeight}px`;
      }
      else if (actionType === 'drag') {
        let newTop = eventStartTop + deltaY;
        newTop = Math.max(0, Math.round(newTop / snapTo) * snapTo);
        if (newTop + eventStartHeight > 1440) newTop = 1440 - eventStartHeight;
        activeEvent.style.top = `${newTop}px`;

        const elementBelow = document.elementFromPoint(e.clientX, e.clientY);
        const targetCol = elementBelow ? elementBelow.closest('.cal-day-column') : null;
        if (targetCol && targetCol !== activeEvent.parentElement) {
          targetCol.appendChild(activeEvent); 
        }
      }
    }
  });

  document.addEventListener('mouseup', () => {
    // A) Finish Creating New Event
    if (isCreating) {
      isCreating = false;
      if (activeCol && selectionBox) {
        let top = Math.min(createStartY, createCurrentY);
        let height = Math.abs(createCurrentY - createStartY);
        top = Math.round(top / snapTo) * snapTo;
        height = height < 15 ? 30 : Math.round(height / snapTo) * snapTo;
        if (top + height > 1440) height = 1440 - top;

        const fmt = (h, m) => `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
        const startHour = Math.floor(top / 60);
        const startMin = Math.floor(top % 60);
        const endHour = Math.floor((top + height) / 60);
        const endMin = Math.floor((top + height) % 60);
        
        const form = document.getElementById('createEventForm');
        form.querySelector('input[name="start_date"]').value = selectedDate;
        form.querySelector('input[name="end_date"]').value = selectedDate; 
        form.querySelector('input[name="start_time"]').value = fmt(startHour, startMin);
        form.querySelector('input[name="end_time"]').value = fmt(endHour, endMin);

        bootstrap.Modal.getOrCreateInstance(document.getElementById('eventModal')).show();

        selectionBox.remove();
        selectionBox = null;
        activeCol = null;
      }
    }

    // B) Finish Dragging/Resizing Existing Event
    if (activeEvent) {
      // If they just clicked and didn't move it, let Bootstrap open the modal naturally
      if (actionType === 'drag-pending') {
        activeEvent = null;
        actionType = null;
        return; 
      }

      // Restore styling
      activeEvent.style.pointerEvents = '';
      activeEvent.style.transform = '';
      activeEvent.style.boxShadow = '';
      activeEvent.style.opacity = '0.9';
      activeEvent.style.zIndex = '10';

      const finalTop = parseInt(activeEvent.style.top);
      const finalHeight = parseInt(activeEvent.style.height);

      const fmt = (h, m) => `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
      const newStartTime = fmt(Math.floor(finalTop / 60), finalTop % 60);
      const newEndTime = fmt(Math.floor((finalTop + finalHeight) / 60), (finalTop + finalHeight) % 60);
      const newDate = activeEvent.closest('.cal-day-column').getAttribute('data-date');

      const eventId = activeEvent.getAttribute('data-id');
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      
      const formData = new FormData();
      formData.append('csrfmiddlewaretoken', csrfToken);
      formData.append('title', activeEvent.getAttribute('data-title'));
      formData.append('description', activeEvent.getAttribute('data-description'));
      formData.append('category', activeEvent.getAttribute('data-category'));
      formData.append('start_date', newDate);
      formData.append('start_time', newStartTime);
      formData.append('end_date', newDate);
      formData.append('end_time', newEndTime);

      const currentEventEl = activeEvent;

      // Background save
      fetch(`/planner/event/update/${eventId}/`, {
        method: 'POST',
        body: formData
      }).then(response => {
        if (response.ok || response.redirected) {
          currentEventEl.setAttribute('data-startdate', newDate);
          currentEventEl.setAttribute('data-enddate', newDate);
          currentEventEl.setAttribute('data-starttime', newStartTime);
          currentEventEl.setAttribute('data-endtime', newEndTime);

          const timeLabel = currentEventEl.querySelector('.time-label') || currentEventEl.querySelectorAll('span.small')[0];
          if (timeLabel) {
            timeLabel.textContent = `${newStartTime} - ${newEndTime}`;
          }
        }
      }).catch(err => console.error("Network error:", err));

      // Re-enable click-to-edit modal after a tiny delay so the release click doesn't trigger it
      const eventRef = activeEvent;
      setTimeout(() => eventRef.setAttribute('data-bs-toggle', 'modal'), 100);

      activeEvent = null;
      actionType = null;
    }
  });
});
