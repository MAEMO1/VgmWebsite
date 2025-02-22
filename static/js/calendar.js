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

        const monthNames = ["January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"];

        let html = `
            <div class="calendar-header">
                <button onclick="previousMonth()">&lt;</button>
                <h2>${monthNames[currentMonth]} ${currentYear}</h2>
                <button onclick="nextMonth()">&gt;</button>
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
                    html += `<div class="day" data-date="${currentYear}-${(currentMonth + 1).toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}">${day}</div>`;
                    day++;
                }
            }
        }

        html += '</div>';
        calendar.innerHTML = html;
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
