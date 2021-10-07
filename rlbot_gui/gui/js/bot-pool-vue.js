import BotCard from './bot-card-vue.js'
import ScriptCard from './script-card-vue.js'
import ScriptDependencies from './script-dependencies-vue.js'
import categories from './categories.js';

export default {
	name: 'bot-pool',
	components: {
		'bot-card': BotCard,
		'script-card': ScriptCard,
		'script-dependencies': ScriptDependencies,
	},
	props: ['bots', 'scripts', 'display-human'],
	template: /*html*/`
		<div class="p-1">
			<b-form inline class="mb-2">
				<b-form-radio-group buttons
					v-model="primaryCategorySelected"
					:options="primaryCategoryOptions"
					button-variant="outline-primary"
					size="sm"
					class="categories-radio-group"
				/>
				<b-form-radio-group buttons
					v-if="primaryCategorySelected.categories.length > 1"
					v-model="primaryCategorySelected.selected"
					:options="primaryCategorySelected.options"
					button-variant="outline-primary"
					size="sm"
					class="categories-radio-group"
				/>
				<b-form-input id="filter-text-input" v-model="botNameFilter" placeholder="Search..." size="sm" type="search"/>
			</b-form>
	
			<div class="overflow-auto">
				<bot-card v-for="bot in bots" :bot="bot" v-show="passesFilter(bot)" @click="$emit('bot-clicked', bot)"/>
	
				<span v-if="displayedBotsCount + displayedScriptsCount === 0">
					No bots available for this category.
				</span>
	
				<div v-if="displayedScriptsCount > 0" class="scripts-header">Scripts</div>
	
				<script-card v-for="script in scripts" :script="script" v-show="passesFilter(script)"/>
				
				<script-dependencies :bots="bots" :scripts="scripts"
					v-if="secondaryCategorySelected.displayScriptDependencies"
					@bot-clicked="$emit('bot-clicked', $event)"
					:name-filter="botNameFilter"
				/>
			</div>
		</div>
	`,
	data () {
		return {
			botNameFilter: '',
			categories: categories,
			primaryCategoryOptions: Object.values(categories).map(ctg => {
				ctg.options = ctg.categories.map(sc => ({text: sc.name, value: sc}));
				ctg.selected = ctg.categories[0];
				return {text: ctg.name, value: ctg};
			}),
			primaryCategorySelected: categories.all,
		};
	},
	methods: {
		passesFilter: function(runnable) {
			let category = this.secondaryCategorySelected;

			// hide runnable when its name doesn't match the search filter
			// if the filter is an empty string, anything matches
			if (!runnable.name.toLowerCase().includes(this.botNameFilter.toLowerCase()))
				return false;
			
			if (runnable.type === 'human')
				return this.displayHuman;

			// show psyonix bots only in specific categories
			if (runnable.type === 'psyonix')
				return category.includePsyonixBots;

			// if a script is enabled, display it regardless of which category is selected
			// except for the script dependencies, where all scripts are displayed already
			if (runnable.type === 'script' && !category.displayScriptDependencies && runnable.enabled)
				return true;

			let allowedTags = runnable.type === 'script' ? category.scripts : category.bots;
			if (allowedTags) {
				if (allowedTags === '*') {
					return true;
				}
				return runnable.info.tags.some(tag => allowedTags.includes(tag));
			}
			return false;
		},
		setDefaultCategory: function() {
			this.primaryCategorySelected = this.categories.standard;
			this.primaryCategorySelected.selected = this.primaryCategorySelected.categories[0];
		},
	},
	computed: {
		secondaryCategorySelected: function() {
			return this.primaryCategorySelected.selected;
		},
		displayedBotsCount: function() {
			return this.bots.filter(this.passesFilter).length;
		},
		displayedScriptsCount: function() {
			return this.scripts.filter(this.passesFilter).length;
		},
	},
}
