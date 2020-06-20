
export default {
    name: 'alter-save-state',
    props: { 'value': Object },
    template: `
    <div>
    <b-button id="debug-state-target">
        Alter State
    </b-button>
    <b-popover target="debug-state-target">
        <template v-slot:title>
        Update UI state
        </template>
            <textarea cols="40" v-bind:value="JSON.stringify(value, null, 2)" v-on:input="handleInput"></textarea>
            <b-button @click="sendJSON">Update</textarea>
    </b-popover>
    </div>
    `,
    data: {
        "text": ''
    },
    methods: {
        handleInput: function (event) {
            this.text = event.target.value;
        },
        sendJSON: function () {
            let state = JSON.parse(this.text)
            console.log(state);
            this.$emit('input', JSON.parse(this.text));
            eel.story_save_fake_state(state)
        }
    }
};