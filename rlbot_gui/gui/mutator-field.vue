<template>
	<md-field>
		<label :for="id">{{label}}</label>
		<md-select v-model="model" :id="id" v-on:md-selected="$emit('input', $event)">
			<md-option v-for="opt in options" :key="opt" :value="opt">{{opt}}</md-option>
		</md-select>
	</md-field>
</template>

<script>

	module.exports = {
		name: 'mutator-field',
		props: ['label', 'options', 'value'],
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
</script>
