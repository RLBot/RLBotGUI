import Colorpicker from './colorpicker-vue.js'

export default {
    name: 'story-start',
    components: {
        'colorpicker': Colorpicker,
    },
    template: /*html*/`
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

        <b-form-group label="Difficulty" label-cols="auto">
            <b-form-select v-model="form.story_id" :options="storyIdOptions"/>
        </b-form-group>

        <b-form-group label="Custom Story Config" v-if="form.story_id == 'custom'" label-class="font-weight-bold">
            <b-form-group label="Challenge Config" label-cols="3">
                <b-button @click="pickFile" value="challenge">Pick File</b-button>
                <span>{{this.form.custom_story.challenge}}</span>
            </b-form-group>
            <b-form-group label="Bots Config (Optional)" label-cols="3">
                <b-button @click="pickFile" value="bots">Pick File</b-button>
                <span>{{this.form.custom_story.bots}}</span>
            </b-form-group>
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
                teamcolor: 0,
                story_id: 'default',
                custom_story: {
                    challenge: '',
                    bots: ''
                }
            },
            storyIdOptions: [
                { value: "easy", text: "Easy"},
                { value: "default", text: "Default"},
                { value: "custom", text: "Custom"}
            ]
        };
    },
    methods: {
        pickFile: async function(event) {
            let field = event.target.value;

            let path = await eel.pick_location(false, 'JSON files (*.json)')(); // is_folder=False
            if (path) {
                this.form.custom_story[field] = path
            }
        },
        submit: function (event) {
            console.log("Submitting story-start");
            event.preventDefault();
        },
    }
};
