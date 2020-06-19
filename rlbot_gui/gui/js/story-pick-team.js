
const DEBUG = false;

export default {
    'name': 'story-pick-team',
    'props': {
        'challenge': Object,
        'teammates': Array
    },
    'template': /*html*/`
        <div>
            <b-button v-if="${DEBUG}" @click="$bvModal.show('pick_team_popup')">
                Open Pick Team Modal
            </b-button>
            <b-modal id="pick_team_popup" 
                title="Pick your teammates"
                :ok-disabled="!enoughAvailableTeammates"
                :ok-variant="enoughAvailableTeammates ? 'success' : 'dark'"
                :body-bg-variant="enoughAvailableTeammates ? 'default' : 'danger'"
                :body-text-variant="enoughAvailableTeammates ? 'dark' : 'light'"
                @ok="$emit('teamPicked', {'id': challenge.id, pickedTeammates})"
                >
                <div class="d-block text-center">
                    <div v-if="!enoughAvailableTeammates">
                    <p>You do not have enough teamamtes to create a team for this challenge.
                    Recruit teammates from the "teammate" tab or play older matches to earn
                    more currency</p>

                    </div>
                    <div v-if="enoughAvailableTeammates">
                    Pick your teammates!
                    </div>
                </div>
            </b-modal>
        </div>
    `,
    'data': function() {
        return {
            pickedTeammates: []
        }
    },
    computed: {
        'enoughAvailableTeammates': function() {
            return this.teammates.length >=  (this.challenge.humanTeamSize - 1)
        }
    },
    'methods': {
        show: function(challenge) {
            this.challenge = challenge
            this.$bvModal.show('pick_team_popup')
        }
    }
}