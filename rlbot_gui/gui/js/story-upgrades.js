
const UPGRADES = [
    {
        "id": "boost-33",
        "text": "Boost Capacity: 33%",
    },
    {
        "id": "boost-100",
        "text": "Boost Capacity: 100%",
    },
    {
        "id": "boost-recharge",
        "text": "Auto-Recharge Boost",
    },
    {
        "id": "rumble",
        "text": "Rumble Powerups",
    }
];

export default {
    name: 'story-upgrades',
    props: { upgradeSaveState: Object },
    template: /*html*/`
    <b-list-group>
        <b-list-group-item 
            v-for="upgrade in upgrades_ui"
            class="d-flex justify-content-between align-items-center"
            v-bind:variant="upgrade.purchased ? 'success' : upgrade.available ? 'default' : 'dark'">
            {{upgrade.text}}
            <b-button v-if="!upgrade.purchased"
                v-bind:id="upgrade.id"
                variant="success"
                v-bind:disabled="!upgrade.available"
                @click="purchase(upgrade.id)">
                Purchase
            </b-button>
        </b-list-group-item>
    </b-list-group>
    `,
    computed: {
        upgrades_ui: function () {
            let currency = this.upgradeSaveState.currency;
            let result = UPGRADES.map((item) => ({
                id: item.id,
                text: item.text,
                purchased: Boolean(this.upgradeSaveState[item.id]),
                available: currency > 0
            }));

            // Screw it, hard coding it is
            if (!result[0].purchased) {
                // If boost-33 is not purchased, 
                // boost-100, boost-recharge is disabled
                result[1].available = false;
                result[2].available = false;
            }
            return result;
        },
    },
    methods: {
        purchase: function (id) {
            console.log("In purchases", id);
            this.$emit('purchase_upgrade', {
                id,
                currentCurrency: this.upgradeSaveState.currency
            });
        }
    }
};