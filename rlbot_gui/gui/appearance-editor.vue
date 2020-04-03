<template>
	<md-dialog :md-active.sync="active" id="appearance-editor-dialog">
		<md-dialog-title style="margin-bottom: 0px;">
			<span v-if="activeBot && activeBot.name">Appearance loadout of {{ activeBot.name }}</span>
			<span v-else>{{ path }}</span>
			<md-button class="md-icon-button" @click="$emit('appearance-editor-closed')" style="float: right;">
				<md-icon>close</md-icon>
			</md-button>
		</md-dialog-title>

		<md-dialog-content style="padding-bottom: 0px;">
			<table class="appearance-editor-table">
				<tr>
					<td style="height: 5px; background-color: rgb(0, 153, 255);"></td>
					<td style="height: 5px; background-color: orange;"></td>
				</tr>
				<tr v-if="colors">
					<td v-for="team in teams">
						<div class="md-layout md-gutter">
							<div v-for="colorType in colorTypes" class="md-layout-item md-size-50">
								<label>{{ colorType.name }}</label>
								<md-avatar style="margin-left: 20px;"
									:style="{'background-color': colorStyle(colorType, team)}">
								</md-avatar>
								<md-menu md-size="auto" style="vertical-align: top;">
									<md-button md-menu-trigger class="md-icon-button">
										<md-icon>edit</md-icon>
									</md-button>
									<md-menu-content class="colorpicker-menu">
										<table style="border-spacing: 0;">
											<tr v-for="i in colorType.rows">
												<td v-for="j in colorType.columns">
													<div class="colorpicker-color"
														:style="{'background-color': colorStyleFromRowAndColumn(colorType, team, i, j)}"
														:class="{'selected-color':
															config[team][colorType.key] == getColorIDFromRowAndColumn(i, j, colorType)}"
														@click="config[team][colorType.key] = getColorIDFromRowAndColumn(i, j, colorType);">
													</div>
												</td>
											</tr>
										</table>
									</md-menu-content>
								</md-menu>
							</div>
						</div>
					</td>
				</tr>
				<tr v-for="itemType in itemTypes">
					<td class="blue-team">
						<item-field :item-type="itemType" :items="items[itemType.category]" v-model="config.blue"></item-field>
					</td>
					<td class="orange-team">
						<item-field :item-type="itemType" :items="items[itemType.category]" v-model="config.orange"></item-field>
					</td>
				</tr>
			</table>
		</md-dialog-content>

		<md-dialog-actions>
			<md-button class="md-raised md-accent" @click="spawnCarForViewing(0)">
				<md-icon>remove_red_eye</md-icon>
				View blue car in game
			</md-button>
			<md-button class="md-raised md-accent" @click="spawnCarForViewing(1)">
				<md-icon>remove_red_eye</md-icon>
				View orange car in game
			</md-button>

			<div class="showcase-select-wrapper">
				<md-field style="margin: 0;">
					<md-select v-model="selectedShowcaseType">
						<md-option v-for="showcaseType in showcaseTypes" :value="showcaseType.id">
							{{ showcaseType.name }}
						</md-option>
					</md-select>
				</md-field>
			</div>

			<md-button class="md-primary md-raised" @click="saveAppearance">
				<md-icon>check</md-icon>
				Save and close
			</md-button>
			<md-button @click="loadLooks(path)">
				<md-icon>clear</md-icon>
				Revert changes
			</md-button>
		</md-dialog-actions>
	</md-dialog>
</template>

<script>
	const ItemField = httpVueLoader('item-field.vue');

	module.exports = {
		name: 'appearance-editor',
		components: {
			'item-field': ItemField
		},
		props: ['active', 'path', 'activeBot', 'map'],
		data () {
			return {
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
				let lines = csv.split('\n');

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
			active: {
				handler: function(val) {
					if (val && this.path) {
						this.loadLooks(this.path);
					}
				}
			}
		}
	}
</script>
