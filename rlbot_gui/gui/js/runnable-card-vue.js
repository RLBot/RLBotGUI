export default {
	name: 'runnable-card',
	props: ['runnable', 'disabled'],
	template: /*html*/`
		<b-card class="bot-card" @click="disabled || $emit('click')" :class="{disabled: disabled}">

			<slot>{{ runnable.name }}</slot>

			<b-button size="sm" class="icon-button warning-icon" v-if="runnable.warn" variant="outline-warning"
						@click.stop="$store.commit('setActiveBot', runnable)" v-b-modal.language-warning-modal>
				<b-icon icon="exclamation-triangle-fill"/>
			</b-button>

			<b-button size="sm" variant="outline-primary" class="bot-hover-reveal icon-button" v-if="runnable.info"
						@click.stop="$store.commit('setActiveBot', runnable)" v-b-modal.bot-info-modal>
				<b-icon icon="info-circle"/>
			</b-button>

		</b-card>
	`,
}
