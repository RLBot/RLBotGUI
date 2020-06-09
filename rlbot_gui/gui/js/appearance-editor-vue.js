import ItemField from './item-field-vue.js';

export default {
	name: 'appearance-editor',
	components: {
		'item-field': ItemField
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
		<b-row v-if="colors" class="mb-3">
			<b-col v-for="team in teams">
				<span v-for="colorType in colorTypes">
					<b-dropdown :text="colorType.name">
						<b-dropdown-text>
							<table style="border-spacing: 0;">
								<tr v-for="i in colorType.rows">
									<td v-for="j in colorType.columns" :style="{'background-color': colorStyleFromRowAndColumn(colorType, team, i, j)}">
										<div class="colorpicker-color"
											 :class="{'selected-color':
												config[team][colorType.key] == getColorIDFromRowAndColumn(i, j, colorType)}"
											 @click="config[team][colorType.key] = getColorIDFromRowAndColumn(i, j, colorType);">
										</div>
									</td>
								</tr>
							</table>
						</b-dropdown-text>
					</b-dropdown>
					<span class="color-indicator" :style="{'background-color': colorStyle(colorType, team)}"></span>
				</span>
			</b-col>
		</b-row>
		<b-row v-if="Object.keys(config.blue).length" class="mb-4">
			<b-col class="blue-team">
				<div v-for="itemType in itemTypes">
					<item-field :item-type="itemType" :items="items[itemType.category]" team="blue" v-model="config.blue"></item-field>
				</div>
			</b-col>
			<b-col class="orange-team">
				<div v-for="itemType in itemTypes">
					<item-field :item-type="itemType" :items="items[itemType.category]" team="orange" v-model="config.orange"></item-field>
				</div>
			</b-col>
		</b-row>

		<div>
			<b-form inline>
				<b-button @click="spawnCarForViewing(0)" class="mr-1">
					<b-icon icon="eye"></b-icon>
					View blue car in game
				</b-button>
				<b-button @click="spawnCarForViewing(1)" class="mr-1">
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
					<b-icon icon="check"></b-icon>
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
					{name: 'Paint Finish', category: 'PaintFinish', itemKey: 'paint_finish_id', paintKey: null},
					{name: 'Accent Paint Finish', category: 'PaintFinish', itemKey: 'custom_finish_id', paintKey: null},
					{name: 'Engine Audio', category: 'EngineAudio', itemKey: 'engine_audio_id', paintKey: null},
					{name: 'Trail', category: 'SupersonicTrail', itemKey: 'trails_id', paintKey: 'trails_paint_id'},
					{name: 'Goal Explosion', category: 'GoalExplosion', itemKey: 'goal_explosion_id', paintKey: 'goal_explosion_paint_id'},
				],
				teams: ['blue', 'orange'],
				colorTypes: [
					{primary: true, name: 'Primary Color', key: 'team_color_id', rows: 7, columns: 10},
					{primary: false, name: 'Accent Color', key: 'custom_color_id', rows: 7, columns: 15}
				],
				colors: null,
				showcaseTypes: [
					{id: "back-center-kickoff-blue", name: "Static (Back-center kickoff - Blue)"},
					{id: "back-center-kickoff-orange", name: "Static (Back-center kickoff - Orange)"},
					{id: "static", name: "Static (Center)"},
					{id: "throttle", name: "Drive around center"},
					{id: "boost", name: "Boost around center"},
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
			getColors: async function() {
				let response = await fetch('json/colors.json');
				this.colors = await response.json();
			},
			saveAppearance: function() {
				eel.save_looks(this.config, this.path)();
				this.$emit('appearance-editor-closed');
			},
			spawnCarForViewing: function(team) {
				eel.spawn_car_for_viewing(this.config, team, this.selectedShowcaseType, this.map);
			},
			getColorRGB: function(colorID, colorType, team) {
				let colors = colorType.primary ? this.colors[team] : this.colors.secondary;
				return colors[colorID];
			},
			getColorIDFromRowAndColumn(row, column, colorType) {
				return (row - 1) * colorType.columns + (column - 1);
			},
			colorStyle: function(colorType, team) {
				let id = this.config[team][colorType.key];
				let rgb = this.getColorRGB(id, colorType, team);
				return 'rgb(' + (rgb ? rgb.toString() : '') + ')';
			},
			colorStyleFromRowAndColumn: function (colorType, team, row, column) {
				let id = this.getColorIDFromRowAndColumn(row, column, colorType);
				let rgb = this.getColorRGB(id, colorType, team);
				return 'rgb(' + (rgb ? rgb.toString() : '') + ')';
			},
			loadLooks: async function (path) {
				this.config = await eel.get_looks(path)();
			}
		},

	created: function() {
			this.getAndParseItems();
			this.getColors();
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
