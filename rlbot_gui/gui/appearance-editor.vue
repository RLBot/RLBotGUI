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
				<tr>
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
				<tr v-for="item in itemTypes">
					<td class="blue-team">
						<item-field :name="item.name" :items="items" v-model="config.blue"
						:item-key="item.itemKey" :paint-key="item.paintKey"></item-field>
					</td>
					<td class="orange-team">
						<item-field :name="item.name" :items="items" v-model="config.orange"
						:item-key="item.itemKey" :paint-key="item.paintKey"></item-field>
					</td>
				</tr>
			</table>
		</md-dialog-content>

		<md-dialog-actions>
			<md-button class="md-raised md-accent" @click="spawnCarForViewing(0)">
				<md-icon>remove_red_eye</md-icon>
				View blue car in game
			</md-button>
			<md-button class="md-raised md-accent" @click="spawnCarForViewing(1)" style="margin-right: auto;">
				<md-icon>remove_red_eye</md-icon>
				View orange car in game
			</md-button>
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
		props: ['active', 'path', 'activeBot'],
		data () {
			return {
				config: {
					blue: {},
					orange: {},
				},
				itemsLoaded: false,
				items: [],
				itemTypes: [
					{name: 'Body', itemKey: 'car_id', paintKey: 'car_paint_id'},
					{name: 'Decal', itemKey: 'decal_id', paintKey: 'decal_paint_id'},
					{name: 'Wheels', itemKey: 'wheels_id', paintKey: 'wheels_paint_id'},
					{name: 'Rocket Boost', itemKey: 'boost_id', paintKey: 'boost_paint_id'},
					{name: 'Antenna', itemKey: 'antenna_id', paintKey: 'antenna_paint_id'},
					{name: 'Topper', itemKey: 'hat_id', paintKey: 'hat_paint_id'},
					{name: 'Paint Finish', itemKey: 'paint_finish_id', paintKey: null},
					{name: 'Accent Paint Finish', itemKey: 'custom_finish_id', paintKey: null},
					{name: 'Engine Audio', itemKey: 'engine_audio_id', paintKey: null},
					{name: 'Trail', itemKey: 'trails_id', paintKey: 'trails_paint_id'},
					{name: 'Goal Explosion', itemKey: 'goal_explosion_id', paintKey: 'goal_explosion_paint_id'},
				],
				teams: ['blue', 'orange'],
				colorTypes: [
					{primary: true, name: 'Primary Color', key: 'team_color_id', rows: 7, columns: 10},
					{primary: false, name: 'Accent Color', key: 'custom_color_id', rows: 7, columns: 15}
				]
			}
		},

		methods: {
			getAndParseItems: async function(url) {
				let response = await fetch(url);
				let data = await response.json();

				// rename duplicate item names
				for (let category of data.Slots) {
					let nameCounts = {};
					for (let item of category.Items) {
						if (nameCounts[item.Name]) {
							nameCounts[item.Name]++;
							item.Name = `${item.Name} (${nameCounts[item.Name]})`;
						} else {
							nameCounts[item.Name] = 1;
						}
					}
				}
				this.items = data.Slots;
			},
			loadItems: async function() {
				if (!this.itemsLoaded) {
					try {
						// try to fetch latest items from alphaconsole github
						await this.getAndParseItems('https://raw.githubusercontent.com/AlphaConsole/AlphaConsoleElectron/public/items.json');
					} catch (error) {
						// otherwise use local version
						await this.getAndParseItems('json/items.json');
					}
					this.itemsLoaded = true;
				}
			},
			saveAppearance: function() {
				eel.save_looks(this.config, this.path)();
				this.$emit('appearance-editor-closed');
			},
			spawnCarForViewing: function(team) {
				eel.spawn_car_for_viewing(this.config, team);
			},
			blueColors: i => { return {
				h: (i % 10) / 20.5 + .33,
				s: .8,
				v: .75 - (Math.floor(i / 10) / 10)
			}},
			orangeColors: i => { return {
				h: 0.2 - ((i % 10) / 35),
				s: 1,
				v: .79 - (Math.floor(i / 10) / 10)
			}},
			accentColors: i => { return {
				h: ((i % 15) / 13) - .12,
				s: i % 15 === 0 ? 0 : 0.9,
				v: i % 15 === 0 ? .75 - (Math.floor(i / 15) / 8) : .85 - (Math.floor(i / 15) / 8)
			}},
			colorStyleFromID: function(id, swatchFunction) {
				let hsl = swatchFunction(parseInt(id));
				let rgb = hslToRgb(hsl.h, hsl.s, hsl.v);
				return 'rgb(' + rgb.toString() + ')';
			},
			getSwatchFunction: function(colorType, team) {
				return colorType.primary ? (team == 'blue' ? this.blueColors : this.orangeColors) : this.accentColors;
			},
			getColorIDFromRowAndColumn(row, column, colorType) {
				return (row - 1) * colorType.columns + (column - 1);
			},
			colorStyle: function(colorType, team) {
				let id = this.config[team][colorType.key];
				return this.colorStyleFromID(id, this.getSwatchFunction(colorType, team));
			},
			colorStyleFromRowAndColumn: function (colorType, team, row, column) {
				let id = this.getColorIDFromRowAndColumn(row, column, colorType);
				return this.colorStyleFromID(id, this.getSwatchFunction(colorType, team));
			},
			loadLooks: async function (path) {
				this.config = await eel.get_looks(path)();
			}
		},

		created: function() {
			this.loadItems();
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
