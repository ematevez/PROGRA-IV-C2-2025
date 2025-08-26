document.addEventListener('DOMContentLoaded', async function() {
    let business_events;
    try {
      let response = await makeRequest(`/api/events/`, method="GET")
      business_events = response.results
    }
    catch (err) {

    }
    
    var calendarEl = document.getElementById('calendar');

    var calendar = new FullCalendar.Calendar(calendarEl, {
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay'
      },
      initialDate: new Date(),
      navLinks: true, // can click day/week names to navigate views
      selectable: true,
      selectMirror: true,
      select: async function(arg) {
        var title = prompt('Event Title:');
        let eventData = {
          title: title,
          start: arg.start,
          end: arg.end,
          allDay: arg.allDay
        }
        if (title) {
          try {
            let response = await makeRequest(`/api/events/create/`, method="POST", data=eventData)
            calendar.addEvent(response.data)
          }
          catch (err) {

          }
        }
        calendar.unselect()
      },
      eventClick: function(arg) {
        if (confirm('Are you sure you want to delete this event?')) {
          try {
            makeRequest(`/api/events/${arg.event._def.publicId}/delete/`, method="DELETE")
            arg.event.remove()
          }
          catch (err) {

          }
        }
      },
      editable: true,
      dayMaxEvents: true, // allow "more" link when too many events
      events: business_events
    });

    calendar.render();
  });