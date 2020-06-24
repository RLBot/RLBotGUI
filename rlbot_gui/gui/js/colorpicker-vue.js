export default {
	name: 'colorpicker',
    props: {
        value: String,
        primary: Boolean,
        team: String,
        text: String,
    },
	template: `
        <span v-if="colors">
            <b-dropdown :text="text">
                <b-dropdown-text>
                    <table style="border-spacing: 0;">
                        <tr v-for="i in rows">
                            <td v-for="j in columns" :style="getColorStyle(getColorID(i, j))">
                                <div class="colorpicker-color"
                                     :class="{'selected-color': value == getColorID(i, j)}"
                                     @click="$emit('input', getColorID(i, j));">
                                </div>
                            </td>
                        </tr>
                    </table>
                </b-dropdown-text>
            </b-dropdown>
            <span class="color-indicator" :style="indicatorColorStyle"></span>
        </span>
	`,
	data () {
        return {
            colors: null,
            rows: 7,
            columns: this.primary ? 10 : 15
        }
    },

	methods: {
        getColorStyle: function(colorID) {
            let colors = this.primary ? this.colors[this.team] : this.colors.secondary;
            let rgb = colors[colorID];
            return {'background-color': `rgb(${rgb ? rgb.toString() : ''})`};
        },
        getColorID(row, column) {
            return (row - 1) * this.columns + (column - 1);
        },
    },

    computed: {
        indicatorColorStyle: function() {
            return this.getColorStyle(this.value);
        },
    },

	beforeMount: async function() {
        let response = await fetch('json/colors.json');
        this.colors = await response.json();
    },
}
