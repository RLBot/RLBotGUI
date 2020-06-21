

export default {
    name: 'story-start',
    template: `
    <b-container class="pt-5">
    <b-jumbotron header="Story Mode" lead="Go on a Rocket League adventure">
    </b-jumbotron>
    <b-card>
    <b-card-text>
    <b-form @submit.prev="$emit('started', form)">
        <b-form-group label="Teamname" label-for="teamname_entry" label-cols="auto">
            <b-form-input 
                type="text"
                required
                placeholder="Enter team name"
                id="teamname_entry" v-model="form.teamname">
            </b-form-input>

        </b-form-group>

        <b-form-group label="Team Color" label-cols="auto" v-if="colors">
        <b-dropdown text="Pick color" id="team-color-picker">
            <b-dropdown-text>
                <table style="border-spacing: 0;">
                    <tr v-for="i in accent_color_info.rows">
                        <td v-for="j in accent_color_info.columns" :style="{'background-color': colorStyleFromRowAndColumn(i, j)}">
                            <div class="colorpicker-color"
                                    :class="{'selected-color':
                                    form.teamcolor == getColorIDFromRowAndColumn(i, j)}"
                                    @click="form.teamcolor = getColorIDFromRowAndColumn(i, j);">
                            </div>
                        </td>
                    </tr>
                </table>
            </b-dropdown-text>
        </b-dropdown>
        <span class="color-indicator" :style="{'background-color': colorStyle()}"></span>
        </b-form-group>

        <b-button type="submit" variant="primary" class="mt-2">Get Started</b-button>
    </b-form>
    </b-card-text>
    </b-card>
    </b-container>
    `,
    data() {
        return {
            form: {
                teamname: '',
                teamcolor: 0
            },
            accent_color_info: { primary: false, name: 'Accent Color', key: 'custom_color_id', rows: 7, columns: 15 },
            colors: null,
        };
    },
    methods: {
        submit: function (event) {
            console.log("Submitting story-start");
            event.preventDefault();
        },
        getColors: async function () {
            let response = await fetch('json/colors.json');
            console.log("Got colors");
            this.colors = await response.json();
        },
        getColorRGB: function (colorID) {
            let colors = this.colors.secondary;
            return colors[colorID];
        },
        getColorIDFromRowAndColumn(row, column) {
            return (row - 1) * this.accent_color_info.columns + (column - 1);
        },
        colorStyle: function () {
            let id = this.form.teamcolor;
            let rgb = this.getColorRGB(id);
            return 'rgb(' + (rgb ? rgb.toString() : '') + ')';
        },
        colorStyleFromRowAndColumn: function (row, column) {
            let id = this.getColorIDFromRowAndColumn(row, column);
            let rgb = this.getColorRGB(id);
            return 'rgb(' + (rgb ? rgb.toString() : '') + ')';
        },
    },
    beforeMount: function () {
        console.log("Getting colors");
        this.getColors();
    }
};
