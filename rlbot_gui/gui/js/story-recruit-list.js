
export default {
    name: 'story-recruit-list',
    props: {
        recruitables: Array,
        currency: 0
    },
    template: /*html*/ `
    <b-list-group>
        <b-list-group-item
            v-for="recruit in recruitables"
            class="d-flex justify-content-between align-items-center"
            v-bind:variant="recruit.recruited ? 'success' : 'default'">
            {{recruit.name}}
            <b-button v-if="!recruit.recruited"
                variant="success"
                :disabled="currency < 1"
                @click="$emit('recruit', recruit.id)">
                Recruit
            </b-button>
        </b-list-group-item>
    </b-list-group>
    `,
};