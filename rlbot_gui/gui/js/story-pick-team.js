
const DEBUG = false;

export default {
    'name': 'story-pick-team',
    'props': {
        'challenge': Object,
        'teammates': Array,
        'botInfo': Object
    },
    'template': /*html*/`
        <div>
            <b-button v-if="${DEBUG}" @click="$bvModal.show('pick_team_popup')">
                Open Pick Team Modal
            </b-button>
            <b-modal id="pick_team_popup" 
                :title="'Pick ' + (challenge.humanTeamSize - 1).toString() + ' teammate(s)'"
                :ok-disabled="blockOkay"
                :ok-variant="!blockOkay ? 'success' : 'dark'"
                :body-bg-variant="enoughAvailableTeammates ? 'default' : 'danger'"
                :body-text-variant="enoughAvailableTeammates ? 'dark' : 'light'"
                @ok="ok"
                @hidden="reset"
                >
                <div class="d-block text-center">
                    <div v-if="!enoughAvailableTeammates">
                    <p>You do not have enough teammates to create a team for this challenge.
                    Recruit teammates from the "teammate" tab or play older matches to earn
                    more currency</p>

                    </div>
                    <div v-if="enoughAvailableTeammates">
                        <b-list-group>
                            <b-list-group-item
                                v-for="teammate in teammates"
                                class="d-flex justify-content-between align-items-center"
                                v-bind:variant="pickedTeammates.includes(teammate) ? 'success' : 'default'"
                            >
                            {{botInfo[teammate].name}}
                            <b-button
                                v-if="!pickedTeammates.includes(teammate)"
                                @click="pick(teammate)"
                            >
                            Pick
                            </b-button>
                            </b-list-group-item>
                        </b-list-group>
                    </div>
                </div>
            </b-modal>
        </div>
    `,
    'data': function () {
        return {
            pickedTeammates: []
        };
    },
    computed: {
        'enoughAvailableTeammates': function () {
            return this.teammates.length >= (this.challenge.humanTeamSize - 1);
        },
        'pickedEnough': function () {
            return this.pickedTeammates.length == (this.challenge.humanTeamSize - 1);
        },
        'blockOkay': function () {
            return (!this.enoughAvailableTeammates || !this.pickedEnough);
        }
    },
    'methods': {
        ok: function (id) {
            // let the popup close first
            let event = {
                id: this.challenge.id,
                pickedTeammates: this.pickedTeammates
            };
            setTimeout(() => this.$emit('teamPicked', event), 50);
        },
        show: function (challenge) {
            // we can remove this if we show other info in this screen
            if (challenge.humanTeamSize == 1) {
                this.$emit('teamPicked', { id: challenge.id });
                return;
            }
            this.challenge = challenge;
            this.$bvModal.show('pick_team_popup');
        },
        pick: function (id) {
            this.pickedTeammates.push(id);
        },
        reset: function () {
            this.pickedTeammates = [];
        }
    }
};
