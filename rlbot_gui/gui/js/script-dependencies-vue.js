import BotCard from './bot-card-vue.js'
import ScriptCard from './script-card-vue.js'

function prefixFilter(arr, prefix) {
	// cut prefix from strings and remove those which don't have the prefix
	return arr.filter(str => str.startsWith(prefix)).map(str => str.substring(prefix.length));
} 

export default {
	name: 'script-dependencies',
	components: {
		'bot-card': BotCard,
		'script-card': ScriptCard,
	},
	props: ['bots', 'scripts', 'nameFilter'],
	template: /*html*/`
		<div>

			<div class="scripts-header">Scripts</div>
			<div>
				<script-card v-for="script in uninvolvedScripts" :script="script" v-show="passesFilter(script)"/>
			</div>

			<div class="scripts-header">Scripts with dependencies</div>
			<div v-for="dependency in dependencies" class="d-flex align-items-center" v-if="dependency.visible">

				<script-card :script="dependency.script" class="flex-shrink-0"/>

				<b-icon
					icon="arrow-left"
					variant="primary"
					font-scale="2"
					v-b-tooltip.hover
					:title="'The bots/scripts (on the right) are designed to play with ' + dependency.script.name"
				/>

				<div>
					<bot-card v-for="bot in dependency.supportedBots"
						:bot="bot"
						@click="$emit('bot-clicked', bot)"
						:disabled="!dependency.script.enabled"
					/>

					<script-card v-for="script in dependency.supportedScripts"
						:script="script"
						:disabled="!dependency.script.enabled"
					/>
				</div>

			</div>
		</div>
	`,
	methods: {
		passesFilter: function(runnable) {
			return runnable.name.toLowerCase().includes(this.nameFilter.toLowerCase());
		}
	},
	computed: {
		dependencies: function() {
			// array of objects, which contain a script and bots/scripts that support/require it
			return this.scripts.map(script => {
				let enableTags = prefixFilter(script.info.tags, "enables-");
				let enableTagFilter = runnable => runnable.info && enableTags.some(tag =>
					prefixFilter(runnable.info.tags, "supports-").includes(tag) ||
					prefixFilter(runnable.info.tags, "requires-").includes(tag)
				);
				
				let supportedBots = this.bots.filter(enableTagFilter);
				let supportedScripts = this.scripts.filter(enableTagFilter);
				let visible = [script, ...supportedBots, ...supportedScripts].some(this.passesFilter);

				return {script, supportedBots, supportedScripts, visible};

			}).filter(d => d.supportedScripts.length + d.supportedBots.length > 0);
		},
		uninvolvedScripts: function() {
			// scripts that don't require another script and arent supported/required by anything else
			return this.scripts.filter(script => this.dependencies.every(
				d => d.script != script && !script.info.tags.some(tag => tag.startsWith("requires-"))
			));
		},
	},
}
