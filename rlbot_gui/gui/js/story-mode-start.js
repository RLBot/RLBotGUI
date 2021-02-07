import Colorpicker from './colorpicker-vue.js'
import LauncherPreferenceModal from './launcher-preference-vue.js'

export default {
    name: 'story-start',
    components: {
        'colorpicker': Colorpicker,
        'launcher-preference-modal': LauncherPreferenceModal,
    },
    template: /*html*/`
    <b-container class="pt-5">
    <b-jumbotron header="Story Mode" lead="Go on a Rocket League adventure">
    </b-jumbotron>
    <b-card>
    <b-card-text>
    <b-form @submit.prev="$emit('started', form)">
        <b-form-group label="Teamname" label-for="teamname_entry" label-cols="3">
            <b-form-input 
                type="text"
                required
                placeholder="Enter team name"
                id="teamname_entry" v-model="form.teamname">
            </b-form-input>

        </b-form-group>

        <b-form-group label="Team Color" label-cols="3">
            <colorpicker v-model="form.teamcolor" text="Pick color"/>
        </b-form-group>

        <b-form-group label="Use Custom Maps" label-cols="3" v-if="false">
            <b-form-checkbox v-model="form.use_custom_maps" size="lg">
                <small> May require large downloads</small>
            </b-form-checkbox>
        </b-form-group>

        <b-form-group label="Config" label-cols="3" >
            <b-form-select v-model="form.story_id" :options="storyIdOptions"/>
        </b-form-group>

        <b-form-group label="User Provided" v-if="form.story_id == 'custom'" label-class="font-weight-bold">
            <b-form-group label="Story Config" label-cols="3">
                <b-button @click="pickFile" value="storyPath">Pick File</b-button>
                <span>{{this.form.custom_story.storyPath}}</span>
            </b-form-group>
        </b-form-group>
        
        <b-form-group label="Launcher" label-cols="3">
            <b-button v-b-modal.launcher-modal-story>
                Choose Steam or Epic
            </b-button>
        </b-form-group>

        <b-button type="submit" variant="primary" class="mt-2">Get Started</b-button>
    </b-form>
    </b-card-text>
    </b-card>
    <b-modal title="Preferred Rocket League Launcher" id="launcher-modal-story" size="md" hide-footer centered>
<!--    Modal id is intentionally different from the one on the main page in main-vue.js-->
        <launcher-preference-modal modal-id="launcher-modal-story" />
    </b-modal>
    </b-container>
    `,
    data() {
        return {
            form: {
                teamname: '',
                teamcolor: 0,
                story_id: 'default',
                custom_story: {
                    storyPath: ''
                },
                use_custom_maps: false
            },
            storyIdOptions: [
                { value: "easy", text: "Easy"},
                { value: "default", text: "Default"},
                { value: "custom", text: "User Provided Config"}
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
