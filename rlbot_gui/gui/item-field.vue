<template>
	<div class="md-layout md-gutter">
		<div class="md-layout-item md-size-70">

			<md-autocomplete v-model="selectedItem" :md-options="itemNames">
				<label>{{ itemType.name }}</label>

				<template slot="md-autocomplete-item" slot-scope="{ item, term }">
					<md-highlight-text :md-term="term">{{ item }}</md-highlight-text>
				</template>
		
				<template slot="md-autocomplete-empty" slot-scope="{ term }">
					No {{ itemType.name }} matching "{{ term }}" found.
				</template>
			</md-autocomplete>

		</div>
		<div v-if="itemType.paintKey" class="md-layout-item md-size-30">

			<md-field :class="selectedPaintColorClass" class="paint-color">
				<md-select v-model="selectedPaint">
					<md-option v-for="color in paintColors" :value="color.id" :class="color.class" class="paint-color">
						{{ color.name }}
					</md-option>
				</md-select>
			</md-field>

		</div>
	</div>
</template>

<script>
	module.exports = {
		name: 'item-field',
		props: ['value', 'items', 'itemType'],
		data: function() {
			return {
				itemNames: this.items.map(el => el.name),
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
			selectedItem: {
				get() {
					let item = this.items.find(el => el.id == this.value[this.itemType.itemKey]);
					return item ? item.name : '';
				},
				set(val) {
					let item = this.items.find(el => el.name == val);
					this.value[this.itemType.itemKey] = item ? item.id : '0';
					this.$emit('input', this.value);
				}
			},
			selectedPaintColorClass: function() {
				let color = this.paintColors.find(el => el.id == this.selectedPaint);
				return color ? color.class : '';
			}
		}
	};
</script>
