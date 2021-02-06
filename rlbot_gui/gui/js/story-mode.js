
import StoryStart from './story-mode-start.js';
import StoryChallenges from './story-challenges.js';

import AlterSaveState from './story-alter-save-state.js';

const UI_STATES = {
    'LOAD_SAVE': 0,
    'START_SCREEN': 1,
    'VALIDATE_PRECONDITIONS': 2,
    'STORY_CHALLENGES': 3
};

export default {
    name: 'story',
    template: /*html*/`
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

        <b-card v-if="ui_state == ${UI_STATES.VALIDATE_PRECONDITIONS}" title="Download Needed Content">
        <b-card-text>

        <b-overlay :show="download_in_progress" rounded="sm" variant="dark">
            <b-list-group>
                <b-list-group-item
                    v-for="conf in validationUIHelper()"
                    v-if="conf.condition">
                    <div class="row">
                        <div class="col">
                            {{conf.text}}
                        </div>
                        <div class="col-2">
                            <b-button variant="primary" @click="conf.handler">Download</button>
                        </div>
                    </div>
                </b-list-group-item>
            </b-list-group>
        </b-overlay>
        </b-card-text>
        </b-card>

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
            validationState: {
                mapPack: {
                    downloadNeeded: false,
                    updateNeeded: false
                },
                botPack: {
                    downloadNeeded: false
                }
            },
            debugMode: false,
            debugStateHelper: '',
            download_in_progress: false
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
            let team_settings = {
                name: event.teamname,
                color: event.teamcolor,
            }
            let story_settings = {
                story_id: event.story_id,
                custom_config: event.custom_story,
                use_custom_maps: event.use_custom_maps
            }
            let state = await eel.story_new_save(team_settings, story_settings)();
            this.saveState = state;

            await this.run_validation()
        },
        run_validation: async function () {
            // check things like map pack and bot pack are downloaded
            let settings = await eel.get_story_settings_json(this.saveState.story_config)();

            // check min map pack version
            let key = "min_map_pack_revision"
            let min_version = settings[key]

            let cur_version = await eel.get_map_pack_revision()()
            let maps_required = (min_version != null)

            let need_maps_download = false
            let need_maps_update = false
            if (maps_required) {
                need_maps_download = (min_version && !cur_version)
                need_maps_update = (min_version > cur_version)
            }

            // check botpack condition
            // we could do version checks with "release tag" but whatever
            // just doing existence checks
            let commit_id = await eel.get_downloaded_botpack_commit_id()()
            let need_bots_download = (commit_id == null)

            this.validationState.mapPack.downloadNeeded = need_maps_download
            this.validationState.mapPack.updateNeeded = need_maps_update
            this.validationState.botPack.downloadNeeded = need_bots_download

            if (need_maps_download || need_maps_update || need_bots_download) {
                this.storyStateMachine(UI_STATES.VALIDATE_PRECONDITIONS);
            }
            else {
                this.storyStateMachine(UI_STATES.STORY_CHALLENGES)
            }
        },
        validationUIHelper: function() {
            let mapPack = this.validationState.mapPack;
            let botPack = this.validationState.botPack;
            const downloadButtonsHelper = [
                {
                    "condition": mapPack.downloadNeeded,
                    "text": "Download Map Pack",
                    "handler": this.downloadMapPack
                },
                {
                    "condition": !mapPack.downloadNeeded && mapPack.updateNeeded,
                    "text": "Update Map Pack",
                    "handler": this.downloadMapPack
                },
                {
                    "condition": botPack.downloadNeeded,
                    "text": "Download Bot Pack",
                    "handler": this.downloadBotPack
                }
            ];
            return downloadButtonsHelper;
        },
        downloadBotPack: function() {
            this.download_in_progress = true
			eel.download_bot_pack()(this.handle_download_updates);
        },
        downloadMapPack: function() {
            this.download_in_progress = true
            eel.update_map_pack()(this.handle_download_updates);
        },
        handle_download_updates: function(finished) {
            this.download_in_progress = false
            this.run_validation()
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
            this.run_validation()
        }

        let self = this;
        eel.expose(loadUpdatedSaveState);
        function loadUpdatedSaveState(saveState) {
            self.saveState = saveState;
            console.log(saveState);
        }

    },
};
