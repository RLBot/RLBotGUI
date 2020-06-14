
const CITIES = {
    'INTRO': 1,
}

export default {
    name: 'story-challenges',
    props: { saveState: Object },
    template: `
    <div class="pt-2">
        <b-card class="mx-auto" style="width: 600px;"
            title="Are you ready?">
            <b-card-text>
            So you've got some wheels. You think that gives you the right to compete with the
            best? <strong>Your car doesn't even have boost!</strong>
            </b-card-text>

            <b-card-text>
            You are going to have to earn some cred by beating some nobody's like you first.
            </b-card-text>

            <b-button block @click="$emit('launch_challenge', 'INTRO-1')" variant="primary">
            Let's do it!
            </b-button>
        </b-card>
    </div>
    `,
    data() {
        return {
            saveState: { // python StoryState class is canonical defintion of this object
            },
            uiState: {

            }
        }
    },
    computed: {
        show_intro_popup: function () {
            if (!saveState['cities'] || !saveState['cities']['INTRO'] || !saveState['cities']['INTRO']['won']) {
                return true
            }
        }
    },
    methods: {
        log: function () {
            console.log(this.saveState);
            this.$bvModal.show('INTRO-modal')
        }
    }
}
