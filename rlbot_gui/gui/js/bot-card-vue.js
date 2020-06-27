export default {
	name: 'bot-card',
	props: ['bot'],
	template: `
		<b-card class="bot-card md-elevation-3" @click="$emit('click')">

            <slot>
                <img v-if="!bot.logo" class="darkened" v-bind:src="bot.image">
                <img v-if="bot.logo" v-bind:src="bot.logo">
                <span class="bot-name">{{ bot.name }}</span>
            </slot>

            <b-button size="sm" class="icon-button warning-icon" v-if="bot.warn" variant="outline-warning"
                        @click.stop="$emit('active-bot')" v-b-modal.language-warning-modal>
                <b-icon icon="exclamation-triangle-fill"/>
            </b-button>

            <b-button size="sm" variant="outline-primary" class="bot-hover-reveal icon-button" v-if="bot.info"
                        @click.stop="$emit('active-bot')" v-b-modal.bot-info-modal>
                <b-icon icon="info-circle"/>
            </b-button>
            
        </b-card>
	`,
}
