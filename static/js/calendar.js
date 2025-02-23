document.addEventListener('DOMContentLoaded', function() {
    const calendar = document.getElementById('calendar');
    if (!calendar) return;

    let currentDate = new Date();
    let currentMonth = currentDate.getMonth();
    let currentYear = currentDate.getFullYear();

    function renderCalendar() {
        const firstDay = new Date(currentYear, currentMonth, 1);
        const lastDay = new Date(currentYear, currentMonth + 1, 0);
        const startingDay = firstDay.getDay();
        const monthLength = lastDay.getDate();
        const today = new Date();

        const monthNames = ["January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"];

        let html = `
            <div class="calendar-header">
                <button onclick="previousMonth()"><i class="fas fa-chevron-left"></i></button>
                <h2>${monthNames[currentMonth]} ${currentYear}</h2>
                <button onclick="nextMonth()"><i class="fas fa-chevron-right"></i></button>
            </div>
            <div class="calendar-grid">
                <div class="weekday">Sun</div>
                <div class="weekday">Mon</div>
                <div class="weekday">Tue</div>
                <div class="weekday">Wed</div>
                <div class="weekday">Thu</div>
                <div class="weekday">Fri</div>
                <div class="weekday">Sat</div>
        `;

        let day = 1;
        for (let i = 0; i < 6; i++) {
            for (let j = 0; j < 7; j++) {
                if (i === 0 && j < startingDay) {
                    html += '<div class="day empty"></div>';
                } else if (day > monthLength) {
                    html += '<div class="day empty"></div>';
                } else {
                    const isToday = day === today.getDate() && 
                                  currentMonth === today.getMonth() && 
                                  currentYear === today.getFullYear();
                    const hasEvents = false; // TODO: Implement event checking
                    const classes = ['day'];
                    if (isToday) classes.push('today');
                    if (hasEvents) classes.push('has-events');

                    html += `
                        <div class="${classes.join(' ')}" 
                             data-date="${currentYear}-${(currentMonth + 1).toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}">
                            ${day}
                        </div>`;
                    day++;
                }
            }
        }

        html += '</div>';
        calendar.innerHTML = html;

        // Add click event listeners to days
        document.querySelectorAll('.day:not(.empty)').forEach(dayElement => {
            dayElement.addEventListener('click', function() {
                const date = this.dataset.date;
                // TODO: Implement day click handling
                console.log('Selected date:', date);
            });
        });
    }

    window.previousMonth = function() {
        currentMonth--;
        if (currentMonth < 0) {
            currentMonth = 11;
            currentYear--;
        }
        renderCalendar();
    };

    window.nextMonth = function() {
        currentMonth++;
        if (currentMonth > 11) {
            currentMonth = 0;
            currentYear++;
        }
        renderCalendar();
    };

    renderCalendar();
});