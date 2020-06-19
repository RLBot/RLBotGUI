
import StoryStart from './story-mode-start.js';
import StoryChallenges from './story-challenges.js';

import AlterSaveState from './story-alter-save-state.js';

const UI_STATES = {
    'LOAD_SAVE': 0,
    'START_SCREEN': 1,
    'STORY_CHALLENGES': 2
};
const DEBUG_STORY_STATE = true; // only changes the UI state


export default {
    name: 'story',
    template: `
    <b-container fluid>
        <story-start v-on:started="startStory" v-if="ui_state === ${UI_STATES.START_SCREEN}">
        </story-start>

        <story-challenges
            @launch_challenge="launchChallenge"
            @purchase_upgrade="purchaseUpgrade"
            @recruit="recruit"
            v-bind:saveState="saveState"
            v-if="ui_state == ${UI_STATES.STORY_CHALLENGES}">
        </story-challenges>

        <b-button @click="deleteSave" variant="danger" v-if="ui_state > ${UI_STATES.START_SCREEN}">Delete Save</b-button>
        <b-button @click="startMatch()" class="mt-2">Test</b-button>

        <alter-save-state v-model="saveState" v-if="debugStoryState"/>
    </b-container>
    `,
    components: {
        'story-start': StoryStart,
        'story-challenges': StoryChallenges,
        'alter-save-state': AlterSaveState,
    },
    data() {
        return {
            ui_state: UI_STATES.LOAD_SAVE,
            saveState: null,
            debugStoryState: DEBUG_STORY_STATE,
            debugStateHelper: ''
        };
    },
    methods: {
        storyStateMachine(targetState) {
            console.log(`Going from ${this.ui_state} to ${targetState}`);
            this.ui_state = targetState;
        },
        startMatch: async function (event) {
            console.log("startMatch");
            setTimeout(() => {
                console.log("gonna call eel");
                eel.story_story_test();
            }, 0);
        },
        startStory: async function (event) {
            console.log(event);
            let state = await eel.story_new_save(event.teamname, event.teamcolor)();
            this.saveState = state;
            this.storyStateMachine(UI_STATES.CITY_MAP);
        },
        deleteSave: async function () {
            await eel.story_delete_save()();
            this.saveState = null;
            this.storyStateMachine(UI_STATES.START_SCREEN);
        },
        launchChallenge: function ({ id, pickedTeammates }) {
            console.log("Starting match", name);
            eel.launch_challenge(id, pickedTeammates);
        },
        purchaseUpgrade: function ({ id, currentCurrency }) {
            // Send eel a message to add id to purchases and reduce currency
            console.log("Will purchase: ", id);
            eel.purchase_upgrade(id, currentCurrency);
        },
        recruit: function ({ id, currentCurrency }) {
            console.log("Will recruit ", id);
            eel.recruit(id, currentCurrency);
        }
    },
    created: async function () {
        let state = await eel.story_load_save()();
        console.log(state);
        if (!state) {
            this.storyStateMachine(UI_STATES.START_SCREEN);
        }
        else {
            this.saveState = state;
            this.storyStateMachine(UI_STATES.STORY_CHALLENGES);
        }

        let self = this;
        eel.expose(loadUpdatedSaveState);
        function loadUpdatedSaveState(saveState) {
            self.saveState = saveState;
            console.log(saveState);
        }

    },
};