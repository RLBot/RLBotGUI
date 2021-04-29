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
			<runnable-card :runnable="bot" :disabled="disabled" :class="{draggable: draggable}" @click="$emit('click')">
				<img v-if="bot.logo" :src="bot.logo">
				<img v-else class="darkened" :src="bot.image">
				<span class="bot-name">
					{{ bot.name }}
					<span v-if="bot.uniquePathSegment" class="unique-bot-identifier">
						({{ bot.uniquePathSegment }})
					</span>
				</span>
			</runnable-card>
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
