$(function () {
    // Mirrors format_duration()/time_indicator() in app/timetable/routes.py so the
    // badges stay in sync between the initial server render and this client-side tick.
    function formatDuration(minutes) {
        minutes = Math.round(minutes);
        var hours = Math.floor(minutes / 60);
        var mins = minutes % 60;
        if (hours) {
            return hours + 'u' + String(mins).padStart(2, '0') + 'm';
        }
        return mins + 'm';
    }

    function computeIndicator(eventTime, now) {
        var minutes = (eventTime.getTime() - now.getTime()) / 60000;

        if (minutes < -10) {
            return null;
        }
        if (minutes < 0) {
            return {label: '+' + formatDuration(-minutes), cssClass: 'tag is-danger'};
        }
        return {
            label: '-' + formatDuration(minutes),
            cssClass: minutes <= 15 ? 'tag is-danger' : 'tag is-success'
        };
    }

    function refreshEta() {
        var now = new Date();

        $('.js-eta').each(function () {
            var $el = $(this);
            var raw = $el.attr('data-event-time');
            if (!raw) {
                return;
            }

            var eventTime = new Date(raw.replace(' ', 'T'));
            if (isNaN(eventTime.getTime())) {
                return;
            }

            var indicator = computeIndicator(eventTime, now);
            if (indicator) {
                $el.html($('<span></span>').addClass(indicator.cssClass).text(indicator.label));
            } else {
                $el.empty();
            }
        });
    }

    refreshEta();
    setInterval(refreshEta, 10000);
});
