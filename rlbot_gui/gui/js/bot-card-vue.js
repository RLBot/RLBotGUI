import RunnableCard from './runnable-card-vue.js'

export default {
	name: 'bot-card',
	components: {
		'runnable-card': RunnableCard,
	},
	props: {
		bot: Object,
		disabled: Boolean,
		draggable: {
			type: Boolean,
			default: true,
		},
	},
	template: /*html*/`
		<draggable v-model="draggableModel" :options="draggableOptions" style="display: inline;">
			<runnable-card :runnable="bot" v-bind="[$props,$attrs]" :class="{draggable: draggable}" @click="$emit('click')">
		</draggable>
	`,
	computed: {
		draggableModel: function() {
			return [this.bot];
		},
		draggableOptions: function() {
			return {
				group: {
					name: 'bots',
					pull: 'clone',
					put: false,
				},
				sort: false,
				disabled: !this.draggable || this.disabled,
			};
		},
	},
}
