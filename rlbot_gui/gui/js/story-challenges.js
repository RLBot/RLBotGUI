
import StoryUpgrades from './story-upgrades.js' 

const CITIES = {
    'INTRO': 1,
}

const CITY_STATE = {
    'LOCKED': 0,
    'OPEN': 1,
    'DONE': 2
}

const CITY_ICON_MAP = [
    'imgs/story/lock-100px.png', // LOCKED
    '',
    'imgs/story/checkmark-100px.png' // DONE
]

// clickArea's generated using https://www.image-map.net/
const CITY_DISPLAY_INFO = {
    'INTRO': {
        displayName: "Beginner's Park",
        overlayLocation: [390, 630],
        clickArea: "649,380,601,379,586,457,566,479,599,525,635,546,718,566,718,514",
        prereqs: []
    },
    'URBAN': {
        displayName: 'Urban Central',
        overlayLocation: [350, 700],
        clickArea: "650,3,671,141,585,221,643,354,724,509,801,437,829,221,779,9",
        prereqs: ['INTRO']
    },
    'WASTELAND': {
        displayName: 'Demolishing Wastelands',
        overlayLocation: [85, 155],
        clickArea: "4,59,109,5,268,62,199,269,166,532,3,547",
        prereqs: ['URBAN']
    },
    'CAMPANDSNIPE': {
        displayName: 'Commonwealth of Campandsnipe',
        overlayLocation: [300, 500],
        clickArea: "295,158,254,198,232,302,255,366,270,502,351,525,446,508,562,473,595,384,641,331,578,229,404,294,332,226,323,187,348,149,326,143",
        prereqs: ['URBAN']
    },
    'CHAMPIONSIAN': {
        displayName: 'Championsian Federation',
        overlayLocation: [64, 540],
        clickArea: "401,92,334,176,405,285,579,217,668,125,637,4,469,21",
        prereqs: ['WASTELAND', 'CAMPANDSNIPE']
    }
}

const DONE_REQS = {
    'INTRO': ['INTRO-1'],
    'URBAN': ['URBAN-1'],
    'WASTELAND': ['WASTELAND-1'],
    'CAMPANDSNIPE': ['CAMPANDSNIPE-1'],
    'CHAMPIONSIAN': ['CHAMPIONSIAN-1']
}



export default {
    name: 'story-challenges',
    props: { saveState: Object, game_in_progress: Object },
    components:  {
        "story-upgrades": StoryUpgrades
    },
    template: /*html*/`
    <div class="pt-2">
        <b-overlay :show="game_in_progress.name" rounded="sm" variant="dark">
            <b-card v-if="showIntroPopup()" class="mx-auto story-card-text" 
                style="width: 600px;"
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

            <b-container fluid v-if="!showIntroPopup()" >
                <b-row>
                <b-col cols="auto">
                    <img src="imgs/story/story-mode-map.png" usemap="#story-image-map">
                    <map name="story-image-map">
                        <area v-for="(city, cityId) in cityDisplayInfo"
                            class="story-clicky"
                            @click.prev="handleCityClick(cityId)"
                            v-bind:id="cityId.toLowerCase() + '-area'"
                            v-bind:alt="city.displayName"
                            v-bind:title="city.displayName"
                            v-bind:coords="city.clickArea"
                            shape="poly">
                    </map>

                    <b-tooltip v-for="(city, cityId) in cityDisplayInfo"
                        v-bind:target="cityId.toLowerCase() + '-area'"
                        triggers="hover">
                        {{getCityStateTooltip(cityId)}}
                    </b-tooltip>
                    <img v-for="(city, cityId) in cityDisplayInfo"
                        class="story-map-icon"
                        v-bind:src="getOverlayForCity(cityId)"
                        v-bind:style="{top: city.overlayLocation[0] + 'px', left: city.overlayLocation[1] + 'px'}" 
                        v-if="getCityState(cityId) !== ${CITY_STATE.OPEN}" />
                </b-col>
                <b-col cols-xl="auto" class="story-dark-bg" style="min-width:200px; max-width:800px;">
                    <b-row class="h-50">
                        <b-card header="City Info" bg-variant="dark" class="w-100">
                        <b-card-text>
                            Click on a City to get started.
                        </b-card-text>
                        </b-card>
                    </b-row>
                    <b-row class="h-50">
                    <b-card no-body bg-variant="dark w-100">
                        <b-tabs content-class="mt-3" fill>
                            <b-tab title="Upgrades" active class="story-card-text">
                                <story-upgrades 
                                    v-bind:upgradeSaveState="saveState.upgrades"
                                    @purchase_upgrade="$emit('purchase_upgrade', $event)">
                                </story-upgrades>
                            </b-tab>
                            <b-tab title="Teammates"><p>I'm the second tab</p></b-tab>
                        </b-tabs>
                    </b-card>
                    </b-row>
                </b-col>
                </b-row>
            </b-container>
        </b-overlay>
    </div>
    `,
    data() {
        return {
            saveState: { // python StoryState class is canonical defintion of this object
            },
            game_in_progress: {},
            gameCompleted: false,
            cityDisplayInfo: CITY_DISPLAY_INFO
        }
    },
    methods: {
        getCityStateTooltip: function (city) {
            let state = this.getCityState(city)
            let displayName = CITY_DISPLAY_INFO[city].displayName

            const suffix = [
                'is still locked.',
                'is open to challenge!',
                'has been completed!'
            ]
            return displayName + ' ' + suffix[state]
        },
        handleCityClick: function (city) {
            console.log(CITY_DISPLAY_INFO[city].displayName)
        },
        showIntroPopup: function () {
            return this.saveState.challenges_completed["INTRO-1"] == undefined
        },
        getCityState: function (city) {
            let state = CITY_STATE.LOCKED

            let prereqs = this.cityDisplayInfo[city].prereqs
            if (prereqs.every(c => (this.getCityState(c) === CITY_STATE.DONE))) {
                state = CITY_STATE.OPEN

                // only need to check completion of challenges if we are open
                let donereqs = DONE_REQS[city]
                if (donereqs.every(c => this.saveState.challenges_completed[c] != undefined)) {
                    state = CITY_STATE.DONE
                }
            }
            console.log(city, state)
            return state;
        },
        getOverlayForCity: function (city) {
            return CITY_ICON_MAP[this.getCityState(city)]
        }
    },
}
