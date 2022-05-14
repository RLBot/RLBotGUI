import RunnableCard from './runnable-card-vue.js'

export default {
	name: 'team-card',
    components: {
		'runnable-card': RunnableCard,
	},
	props: ['value', 'team-class'],
	template: `
		<b-card class="team-card md-elevation-8" :class="teamClass">
            <div class="team-label">
                <slot></slot>
            </div>
            <draggable v-model="team" class="team-entries" :options="{group:'bots'}" @change="$event.added ? $emit('botadded', $event.added.element) : 0">
                <runnable-card
                    v-for="(bot, index) in team" :runnable="bot" class="draggable"
                    removable @remove="team.splice(index, 1)">
                </runnable-card>
            </draggable>
        </b-card>
    `,
    computed: {
        team: {
            get() {
                return this.value;
            },
            set(val) {
                this.$emit('input', val);
            }
        },
    },
}
