export default {
	name: 'mutator-field',
	props: ['label', 'options', 'value'],
	template: `
	<b-form-group :label="label">
		<b-form-select v-model="model" :id="id"v-on:change="$emit('input', $event)"
			:class="{'highlighted-mutator-field': value != options[0]}"
		>
			<b-form-select-option v-for="opt in options" :key="opt" :value="opt">{{opt}}</b-form-select-option>
		</b-form-select>
	</b-form-group>
	`,
	data: function() {
		return {
			id: Math.floor(Math.random() * 1000000000).toString(),
			model: this.value
		}
	},
	watch: {
		value: function(newVal, oldVal) {
			this.model = newVal;
		}
	},
};
