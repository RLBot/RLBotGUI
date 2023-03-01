export default {
    name: 'community-events',
    template: /*html*/`
		<b-modal title="Community Events" id="community-events" size="lg" centered ok-only>
			<div v-if="events.length == 0">
				<p>There are no community events at this time.</p>
			</div>
			<div v-else v-for="event in events">
				<h3>{{ event.name }}</h3>
                <p v-if="event.timeUntilMs > 0" class="mb-1">
                    <b-icon icon="calendar-plus"/> Starts in <b>{{ event.timeUntil }}</b> ({{ event.time }})
                </p>
                <p v-else class="mb-1">
                    <b-icon icon="alarm"/> Started <b>{{ event.timeUntil }}</b> ago, but you can still join!
                </p>
				<p>
                    <b-icon icon="geo"/> <a :href="event.location" target="_blank">{{ event.location }}</a>
                </p>
			</div>
		</b-modal>
	`,
    data() {
        return {
            events: [],
            eventsNow: 0,
            eventsFuture: 0,
        }
    },
    methods: {
        dateTimeCheck: function (today, event) {
            const names = event.summary;
            const start = event.start.dateTime;
            let new_date = new Date(start);

            try {
                const recurrence = event.recurrence[0].split(";");
                const rec_type = recurrence[0].split("=")[1];
                const interval = recurrence[2].split("=")[1];
                const end_date_type = recurrence[2].split("=")[0];
                const end_date_raw = recurrence[2].split("=")[1];
                let end_date = new Date(new_date);
                if (end_date_type == "COUNT") {
                    if (rec_type == "WEEKLY") {
                        end_date.setDate(new_date.getDate() + 7 * interval * end_date_raw);
                    } else if (rec_type == "MONTHLY") {
                        end_date.setDate(new_date.getDate() + 4 * interval * end_date_raw);
                    }
                } else {
                    end_date.setDate(end_date_raw);
                }
                if (rec_type == "WEEKLY") {
                    while (new_date <= end_date) {
                        if (new_date > today) {
                            break;
                        }
                        new_date.setDate(new_date.getDate() + 7);
                    }
                } else if (rec_type == "MONTHLY") {
                    while (new_date <= end_date) {
                        if (new_date > today) {
                            break;
                        }
                        new_date.setDate(new_date.getDate() + 4);
                    }
                }
            }
            catch (e) {
                console.error("Error checking recurrence:" + e);
            }

            const time_untils = new_date.getTime() - today.getTime();
            return [names, new_date, time_untils];
        },
        formatFromNow: function(milliseconds) {
            let days = Math.floor(milliseconds / (1000 * 60 * 60 * 24));
            let hours = Math.floor(
                (milliseconds % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)
            );
            let minutes = Math.floor(
                (milliseconds % (1000 * 60 * 60)) / (1000 * 60)
            );
            let format = "";
            if (days > 0) {
                format += days;
                if (days > 1) {
                    format += " days ";
                } else {
                    format += " day ";
                }
            }
            if (hours > 0) {
                format += hours;
                if (hours > 1) {
                    format += " hours ";
                } else {
                    format += " hour ";
                }
            }
            if (minutes > 0) {
                format += minutes;
                if (minutes > 1) {
                    format += " minutes ";
                } else {
                    format += " minute ";
                }
            }
            return format;
        },
        fetchEvents: function () {
            const api_key = "AIzaSyBQ40UqlMPexzWxTNd7EYtTrkoFF_DqpqM";
            const to_check = new Date().toISOString();
            const url = `https://www.googleapis.com/calendar/v3/calendars/rlbotofficial@gmail.com/events?maxResults=10&timeMin=${to_check}&key=${api_key}`;

            fetch(url).then((response) => {
                response.json().then((data) => {
                    this.events = [];

                    // compute dates and times
                    for (let event of data.items) {
                        let [names, new_date, time_until_ms] = this.dateTimeCheck(new Date(), event);

                        if (time_until_ms > 0)
                            this.eventsFuture += 1;
                        else
                            this.eventsNow += 1;

                        // time_untils is the time until the event in milliseconds
                        // convert this to something human readable, like "in 2 days"
                        const format = this.formatFromNow(Math.abs(time_until_ms));

                        this.events.push({
                            name: names,
                            location: event.location,
                            time: new_date.toLocaleString(),
                            timeUntil: format,
                            timeUntilMs: time_until_ms,
                        });
                    }

                    // sort community events by start time
                    this.events.sort((a, b) => {
                        return new Date(a.timeUntilMs) - new Date(b.timeUntilMs);
                    });

                    // only show the first 3
                    this.events = this.events.slice(0, 3);
                });
            });
        },
    },
    mounted() {
        this.fetchEvents();
    },
}
