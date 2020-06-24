import Colorpicker from './colorpicker-vue.js'

export default {
    name: 'story-start',
    components: {
        'colorpicker': Colorpicker,
    },
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

        <b-form-group label="Team Color" label-cols="auto">
            <colorpicker v-model="form.teamcolor" text="Pick color"/>
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
        };
    },
    methods: {
        submit: function (event) {
            console.log("Submitting story-start");
            event.preventDefault();
        },
    }
};
