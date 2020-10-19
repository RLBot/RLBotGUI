export default {
	name: 'team-card',
	props: ['value', 'team-class'],
	template: `
		<b-card class="team-card md-elevation-8" :class="teamClass">
            <div class="team-label">
                <slot></slot>
            </div>
            <draggable v-model="team" class="team-entries" :options="{group:'bots'}">
                <b-card class="bot-card draggable center-flex md-elevation-3" v-for="(bot, index) in team">
                    <img v-if="!bot.logo" class="darkened" v-bind:src="bot.image">
                    <img v-if="bot.logo" v-bind:src="bot.logo">
                    <span class="bot-name">{{ bot.name }} <span v-if="bot.uniquePathSegment" class="unique-bot-identifier">({{ bot.uniquePathSegment }})</span></span>
                    <b-button size="sm" variant="outline-danger" class="icon-button" @click="team.splice(index, 1)">
                        <b-icon icon="x"></b-icon>
                    </b-button>
                </b-card>
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
