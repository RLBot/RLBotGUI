export default {
	name: 'runnable-card',
	props: {
		runnable: Object,
		disabled: Boolean,
		removable: Boolean,
		hidewarning: Boolean,
	},
	template: /*html*/`
		<b-card class="bot-card" @click="disabled || $emit('click')" :class="{disabled: disabled}">

			<slot>
				<img v-if="runnable.logo" :src="runnable.logo">
				<img v-else class="darkened" :src="runnable.image">
				<span class="bot-name">
					{{ runnable.name }}
					<span v-if="runnable.uniquePathSegment" class="unique-bot-identifier">
						&nbsp;({{ runnable.uniquePathSegment }})
					</span>
				</span>
			</slot>

			<b-button size="sm" class="icon-button warning-icon" v-if="runnable.warn && !hidewarning" variant="outline-warning"
						@click.stop="$store.commit('setActiveBot', runnable)" v-b-modal.language-warning-modal>
				<b-icon icon="exclamation-triangle-fill"/>
			</b-button>

			<b-button size="sm" variant="outline-primary" class="bot-hover-reveal icon-button" v-if="runnable.info"
						@click.stop="$store.commit('setActiveBot', runnable)" v-b-modal.bot-info-modal>
				<b-icon icon="info-circle"/>
			</b-button>

			<b-button v-if="removable" size="sm" variant="outline-danger" class="icon-button" @click="$emit('remove')">
				<b-icon icon="x"></b-icon>
			</b-button>

		</b-card>
	`,
}
