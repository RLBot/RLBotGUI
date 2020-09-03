
import StoryStart from './story-mode-start.js';
import StoryChallenges from './story-challenges.js';

import AlterSaveState from './story-alter-save-state.js';

const UI_STATES = {
    'LOAD_SAVE': 0,
    'START_SCREEN': 1,
    'STORY_CHALLENGES': 2
};


export default {
    name: 'story',
    template: `
    <div>
    <b-navbar class="navbar">
        <b-navbar-brand>
            <img class="logo" src="imgs/rlbot_logo.png">
            <span class="rlbot-brand" style="flex: 1">Story Mode</span>
        </b-navbar-brand>
        <b-navbar-nav class="ml-auto">
            <alter-save-state v-model="saveState" v-if="debugMode"/>
            <b-dropdown class="ml-4" right variant="dark">
				<template v-slot:button-content>
					Menu
				</template>
                <b-dropdown-item @click="toggleDebugMode" v-if="ui_state > ${UI_STATES.START_SCREEN}">Debug Mode</b-dropdown-item>
                <b-dropdown-item @click="deleteSave" v-if="ui_state > ${UI_STATES.START_SCREEN}">Delete Save</b-dropdown-item>
			</b-dropdown>
			<b-button class="ml-4" @click="watching = false; $router.replace('/')" variant="dark">
                Back
            </b-button>
        </b-navbar-nav>
    </b-navbar>

    <b-container fluid>
        <story-start v-on:started="startStory" v-if="ui_state === ${UI_STATES.START_SCREEN}">
        </story-start>

        <story-challenges
            @launch_challenge="launchChallenge"
            @purchase_upgrade="purchaseUpgrade"
            @recruit="recruit"
            v-bind:saveState="saveState"
            v-bind:debugMode="debugMode"
            v-if="ui_state == ${UI_STATES.STORY_CHALLENGES}">
        </story-challenges>
    </b-container>
    </div>
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
            debugMode: false,
            debugStateHelper: ''
        };
    },
    methods: {
        toggleDebugMode() {
            this.debugMode = !this.debugMode;
        },
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
            let state = await eel.story_new_save(
                event.teamname,
                event.teamcolor,
                event.story_id,
                event.custom_story)();
            this.saveState = state;
            this.storyStateMachine(UI_STATES.STORY_CHALLENGES);
        },
        deleteSave: async function () {
            await eel.story_delete_save()();
            this.saveState = null;
            this.storyStateMachine(UI_STATES.START_SCREEN);
        },
        launchChallenge: function ({ id, pickedTeammates }) {
            console.log("Starting match", id);
            eel.launch_challenge(id, pickedTeammates);
        },
        purchaseUpgrade: function ({ id, currentCurrency, cost }) {
            // Send eel a message to add id to purchases and reduce currency
            console.log("Will purchase: ", id);
            eel.purchase_upgrade(id, currentCurrency, cost);
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
