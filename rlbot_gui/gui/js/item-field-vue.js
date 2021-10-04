export default {
	name: 'item-field',
	props: ['value', 'items', 'itemType', 'team'],
	template: `
	<b-row>
		<b-col class="pr-1">
			<b-form-group :label="itemType.name" label-cols="4">
				<b-input-group>
						
					<b-input-group-prepend>
						<b-button variant="secondary" size="sm" v-b-tooltip.hover title="Set random" @click="selectRandomItem">
							<b-icon icon="shuffle"/>
						</b-button>
					</b-input-group-prepend>

					<b-form-input
						v-model="itemSelection"
						:list="'list' + itemType.name + team"
						autocomplete="off"
						:state="validationState"
						@mousedown="itemSelection = '';"
					/>
					<b-form-datalist :id="'list' + itemType.name + team" :options="items" value-field="itemKey" text-field="name"></b-form-datalist>

				</b-input-group>
			</b-form-group>
		</b-col>

		<b-col cols="3">
			<md-field v-if="itemType.paintKey">
				<b-form-select v-model="selectedPaint" class="paint-color" :class="selectedPaintColorClass">
					<b-form-select-option v-for="color in paintColors" :value="color.id" :class="color.class" class="paint-color">
						{{ color.name }}
					</b-form-select-option>
				</b-form-select>
			</md-field>
		</b-col>
	</b-row>
	`,
	data: function() {
		return {
			itemSelection: null,
			validationState: null,
			paintColors: [
				{id: 0, class: '', name: 'No Paint'},
				{id: 1, class: 'crimson', name: 'Crimson'},
				{id: 2, class: 'lime', name: 'Lime'},
				{id: 3, class: 'black', name: 'Black'},
				{id: 4, class: 'skyblue', name: 'Sky Blue'},
				{id: 5, class: 'cobalt', name: 'Cobalt'},
				{id: 6, class: 'burntsienna', name: 'Burnt Sienna'},
				{id: 7, class: 'forestgreen', name: 'Forest Green'},
				{id: 8, class: 'purple', name: 'Purple'},
				{id: 9, class: 'pink', name: 'Pink'},
				{id: 10, class: 'orange', name: 'Orange'},
				{id: 11, class: 'grey', name: 'Grey'},
				{id: 12, class: 'titaniumwhite', name: 'Titanium White'},
				{id: 13, class: 'saffron', name: 'Saffron'},
			]
		}
	},
	methods: {
		loadItemSelection: function() {
			let id = this.value[this.itemType.itemKey];
			let item = this.items.find(el => el.id === id);
			this.itemSelection = item ? item.name : '';
		},
		selectRandomItem: function() {
			let randomIndex = Math.floor(Math.random() * this.items.length);
			this.itemSelection = this.items[randomIndex].name;
		},
		selectRandomPaintColor: function() {
			let randomIndex = Math.floor(Math.random() * this.paintColors.length);
			this.selectedPaint = this.paintColors[randomIndex].id;
		},
	},
	created: function() {
		this.loadItemSelection();
	},
	watch: {
		itemSelection: {
			handler: function(val) {
				let item = this.items.find(el => el.name === val);
				this.value[this.itemType.itemKey] = item ? item.id : '0';
				this.validationState = item || val === '' ? null : false;
				this.$emit('input', this.value);
			}
		},
		value: {
			handler: function() {
				this.loadItemSelection();
			}
		}
	},
	computed: {
		selectedPaint: {
			get() {
				return this.value[this.itemType.paintKey];
			},
			set(val) {
				this.value[this.itemType.paintKey] = val;
				this.$emit('input', this.value);
			}
		},
		selectedPaintColorClass: function() {
			let color = this.paintColors.find(el => el.id == this.selectedPaint);
			return color ? color.class : '';
		}
	}
};
