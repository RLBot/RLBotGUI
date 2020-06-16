
import StoryStart from './story-mode-start.js'
import StoryChallenges from './story-challenges.js'

const UI_STATES = {
    'LOAD_SAVE': 0,
    'START_SCREEN': 1,
    'STORY_CHALLENGES': 2
};
const DEBUG_STORY_STATE = true; // only changes the UI state

let JsonToTextArea = {
    'name': 'json-to-text',
    'props': {'value': Object},
    'template':`
    <div>
        <textarea v-bind:value="JSON.stringify(value, null, 2)" v-on:input="handleInput"></textarea>
        <b-button @click="sendJSON">Update</textarea>
    </div>
    `,
    data: {
        "text": ''
    },
    methods: {
        handleInput: function(event) {
            this.text = event.target.value;
        },
        sendJSON: function(){
            console.log(this.text)
            this.$emit('input', JSON.parse(this.text))
        }
    }
};

export default {
    name: 'story',
    template: `
    <b-container fluid>
        <story-start v-on:started="startStory" v-if="ui_state === ${UI_STATES.START_SCREEN}">
        </story-start>

        <story-challenges
            v-on:launch_challenge="launchChallenge"
            v-bind:saveState="saveState"
            v-bind:game_in_progress="game_in_progress"
            v-bind:gameCompleted="gameCompleted"
            v-if="ui_state == ${UI_STATES.STORY_CHALLENGES}">
        </story-challenges>

        <b-button @click="deleteSave" variant="danger" v-if="ui_state > ${UI_STATES.START_SCREEN}">Delete Save</b-button>
        <b-button @click="startMatch()" class="mt-2">Test</b-button>

        <b-button id="debug-state-target" v-if="debugStoryState">
            Alter State
        </b-button>
        <b-popover target="debug-state-target">
            <template v-slot:title>
            Update UI state
            </template>
            <json-to-text v-model="saveState"/>
        </b-popover>
    </b-container>
    `,
    components: {
        'story-start': StoryStart,
        'story-challenges': StoryChallenges,
        'json-to-text': JsonToTextArea,
    },
    data() {
        return {
            ui_state: UI_STATES.LOAD_SAVE,
            saveState: null,
            game_in_progress: {},
            gameCompleted: false,
            debugStoryState: DEBUG_STORY_STATE,
            debugStateHelper: ''
        }
    },
    methods: {
        storyStateMachine(targetState) {
            console.log(`Going from ${this.ui_state} to ${targetState}`)
            this.ui_state = targetState;
        },
        startMatch: async function (event) {
            console.log("startMatch")
            setTimeout(() => {
                console.log("gonna call eel")
                eel.story_story_test()
            }, 0);
        },
        startStory: async function (event) {
            console.log(event)
            let state = await eel.story_new_save(event.teamname, event.teamcolor)()
            this.saveState = state
            this.storyStateMachine(UI_STATES.CITY_MAP)
        },
        deleteSave: async function() {
            await eel.story_delete_save()()
            this.saveState = null
            this.storyStateMachine(UI_STATES.START_SCREEN)
        },
        launchChallenge: function(name) {
            console.log(name)
            let attempts = this.saveState.challenges_attempts[name] 
            this.game_in_progress = {
                name: name,
                target_count: (attempts ? attempts.length : 0) + 1
            }
            console.log(this.game_in_progress)
            eel.launch_challenge(name)
        }
    },
    created: async function () {
        let state = await eel.story_load_save()();
        console.log(state);
        if (!state) {
            this.storyStateMachine(UI_STATES.START_SCREEN)
        }
        else {
            this.saveState = state
            this.storyStateMachine(UI_STATES.STORY_CHALLENGES)
        }

        let self = this;
        eel.expose(loadUpdatedSaveState)
        function loadUpdatedSaveState(saveState) {
            self.saveState = saveState

            if (self.game_in_progress.name) {
                console.log("Game was in progress so will disable it")
                let name = self.game_in_progress.name
                let status = self.saveState.challenges_attempts[name]
                console.log(status)
                console.log(status.length)
                if (status && status.length == self.game_in_progress.target_count) {
                    console.log("New results match target count!")
                    let results = status[self.game_in_progress.target_count - 1]
                    self.gameCompleted = {
                        name: name,
                        completed: results.challenge_completed
                    }
                    self.game_in_progress = {}
                }
            }
            console.log(saveState)
        }

    },
}