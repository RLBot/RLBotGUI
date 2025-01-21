import RunnableCard from './runnable-card-vue.js'

export default {
	name: 'script-card',
	props: {
		script: Object,
		disabled: Boolean,
		favorited: Boolean,
	},
	components: {
		'runnable-card': RunnableCard,
	},
	template: `
		<runnable-card :runnable="script" class="script-card" :disabled="disabled" :favorited="favorited">
			<b-form inline>
				<b-form-checkbox v-model="script.enabled" class="script-switch" switch :disabled="disabled">
					<img :src="script.logo">
					{{ script.name }}
					<span v-if="script.uniquePathSegment" class="unique-bot-identifier">
						&nbsp;({{ script.uniquePathSegment }})
					</span>
				</b-form-checkbox>
			</b-form>
		</runnable-card>
	`,
}
