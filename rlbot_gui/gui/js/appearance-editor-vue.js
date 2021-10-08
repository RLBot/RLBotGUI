import ItemField from './item-field-vue.js';
import Colorpicker from './colorpicker-vue.js'

export default {
	name: 'appearance-editor',
	components: {
		'item-field': ItemField,
		'colorpicker': Colorpicker,
	},
	props: ['path', 'activeBot', 'map'],
	template: `
	<b-modal id="appearance-editor-dialog" size="xl" v-model="appearanceModalActive" hide-footer centered>
		<template v-slot:modal-title>
			<span v-if="activeBot && activeBot.name">Appearance loadout of {{ activeBot.name }}</span>
			<span v-else>{{ path }}</span>
		</template>

		<b-row class="mb-2">
			<b-col>
				<div style="height: 7px; background-color: rgb(0, 153, 255);"></div>
			</b-col>
			<b-col>
				<div style="height: 7px; background-color: orange;"></div>
			</b-col>
		</b-row>

		<b-row class="mb-3">
			<b-col v-for="team in teams">
				<colorpicker text="Primary Color" v-model="config[team]['team_color_id']" primary :team="team"/>
				<colorpicker text="Accent Color" v-model="config[team]['custom_color_id']"/>
				<b-button class="float-right" @click="randomizeTeamLoadout(team)" v-b-tooltip.hover :title="'Randomize entire ' + team + ' team loadout'">
					<b-icon icon="shuffle"/>
				</b-button>
			</b-col>
		</b-row>

		<b-row v-if="Object.keys(config.blue).length" class="mb-4">
			<b-col v-for="team in teams">
				<div v-for="itemType in itemTypes">
					<item-field :item-type="itemType" :items="items[itemType.category]" :team="team" v-model="config[team]" :ref="team"/>
				</div>
			</b-col>
		</b-row>

		<div>
			<b-form inline>
				<b-button variant="outline-primary" @click="spawnCarForViewing(0)" class="mr-1">
					<b-icon icon="eye"></b-icon>
					View blue car in game
				</b-button>

				<b-button variant="outline-primary" @click="spawnCarForViewing(1)" class="mr-1">
					<b-icon icon="eye"></b-icon>
					View orange car in game
				</b-button>

				<b-form-select v-model="selectedShowcaseType">
					<b-form-select-option v-for="showcaseType in showcaseTypes" :value="showcaseType.id">
						{{ showcaseType.name }}
					</b-form-select-option>
				</b-form-select>

				<span style="flex-grow: 1"></span>

				<b-button variant="primary" @click="saveAppearance" class="mr-1">
					Save and close
				</b-button>

				<b-button @click="loadLooks(path)">
					Revert changes
				</b-button>
			</b-form>
		</div>
	</b-modal>
	`,
	data () {
			return {
				appearanceModalActive: false,
				config: {
					blue: {},
					orange: {},
				},
				items: {},
				itemTypes: [
					{name: 'Body', category: 'Body', itemKey: 'car_id', paintKey: 'car_paint_id'},
					{name: 'Decal', category: 'Skin', itemKey: 'decal_id', paintKey: 'decal_paint_id'},
					{name: 'Wheels', category: 'Wheels', itemKey: 'wheels_id', paintKey: 'wheels_paint_id'},
					{name: 'Boost', category: 'Boost', itemKey: 'boost_id', paintKey: 'boost_paint_id'},
					{name: 'Antenna', category: 'Antenna', itemKey: 'antenna_id', paintKey: 'antenna_paint_id'},
					{name: 'Topper', category: 'Hat', itemKey: 'hat_id', paintKey: 'hat_paint_id'},
					{name: 'Primary Finish', category: 'PaintFinish', itemKey: 'paint_finish_id', paintKey: null},
					{name: 'Accent Finish', category: 'PaintFinish', itemKey: 'custom_finish_id', paintKey: null},
					{name: 'Engine Audio', category: 'EngineAudio', itemKey: 'engine_audio_id', paintKey: null},
					{name: 'Trail', category: 'SupersonicTrail', itemKey: 'trails_id', paintKey: 'trails_paint_id'},
					{name: 'Goal Explosion', category: 'GoalExplosion', itemKey: 'goal_explosion_id', paintKey: 'goal_explosion_paint_id'},
				],
				teams: ['blue', 'orange'],
				showcaseTypes: [
					{id: "back-center-kickoff", name: "Static (Back-center kickoff)"},
					{id: "static", name: "Static (Center)"},
					{id: "throttle", name: "Drive around center"},
					{id: "boost", name: "Boost around center"},
					{id: "goal-explosion", name: "Goal explosion"},
				],
				selectedShowcaseType: "boost"
			}
		},

	methods: {
			getAndParseItems: async function() {
				let response = await fetch('csv/items.csv');
				let csv = await response.text();
				let lines = csv.split(/\r?\n/);

				let items = {};
				for (const key in this.itemTypes) {
					let category = this.itemTypes[key].category;
					items[category] = [];
				}

				for (const line of lines) {
					let columns = line.split(',');
					let category = columns[1];

					if (items[category])
						items[category].push({id: columns[0], name: columns[3]});
				}

				// rename duplicate item names (append them with (2), (3), ...)
				for (const category in items) {
					let nameCounts = {};
					for (let item of items[category]) {
						if (nameCounts[item.name]) {
							nameCounts[item.name]++;
							item.name = `${item.name} (${nameCounts[item.name]})`;
						} else {
							nameCounts[item.name] = 1;
						}
					}
				}

				this.items = items;
			},
			saveAppearance: function() {
				eel.save_looks(this.config, this.path)();
				this.$bvModal.hide('appearance-editor-dialog');
			},
			spawnCarForViewing: function(team) {
				eel.spawn_car_for_viewing(this.config, team, this.selectedShowcaseType, this.map);
			},
			loadLooks: async function (path) {
				this.config = await eel.get_looks(path)();
			},
			randomizeTeamLoadout: function(team) {
				this.config[team].team_color_id = Math.floor(Math.random() * 70);
				this.config[team].custom_color_id = Math.floor(Math.random() * 105);

				for (const itemField of this.$refs[team]) {
					itemField.selectRandomItem();
					itemField.selectRandomPaintColor();
				}
			},
		},

	created: function() {
			this.getAndParseItems();
		},

	watch: {
			appearanceModalActive: {
				handler: function(val) {
					if (val && this.path) {
						this.loadLooks(this.path);
					}
				}
			}
		},
}
