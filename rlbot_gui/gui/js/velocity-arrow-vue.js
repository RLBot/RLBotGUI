const VELOCITY_SCALE = 30;

export default {
    name: 'velocity-arrow',
    props: ['object', 'color', 'maxradius'],
    template: `
        <v-group>
            <v-line :config="lineConfig"></v-line>
            <v-wedge :config="wedgeConfig" @dragstart="onDragStart" @dragmove="onDragMove" @dragend="onDragEnd"></v-wedge>
        </v-group>
    `,
    data: function() {
        return {
            lineConfig: {
                points: [0, 0, 0, 0],
                stroke: this.color,
                strokeWidth: 5,
                lineCap: 'round'
            },
            wedgeConfig: {
                x: 0,
                y: 0,
                rotation: 0,
                draggable: true,
                radius: 15,
                angle: 60,
                fill: this.color,
                offset: {
                    x: 14,
                    y: 7.7
                }
            }
        }
    },
    methods: {
        onDragStart: function(evt) {
            this.$emit("dragstart", evt);
        },
        onDragEnd: function(evt) {
            this.$emit("dragend", this.object);
        },
        onDragMove: function(evt) {
            let pos = this.dragBounds({x: evt.target.x(), y: evt.target.y()});
            this.wedgeConfig.x = pos.x;
            this.wedgeConfig.y = pos.y;
            let dx = this.object.x - this.wedgeConfig.x;
            let dy = this.object.y - this.wedgeConfig.y;
            this.object.vx = dx * VELOCITY_SCALE;
            this.object.vy = dy * VELOCITY_SCALE;
            this.object.rotation = Math.atan2(dy, dx) * 180/Math.PI;

            this.update(this.object);
        },
        dragBounds: function(pos) {
            let dx = pos.x - this.object.x;
            let dy = pos.y - this.object.y;
            let distance = Math.hypot(dx, dy) * VELOCITY_SCALE;
            if (distance > this.maxradius) {
                return {
                    x: this.object.x + dx * this.maxradius/distance,
                    y: this.object.y + dy * this.maxradius/distance
                }
            } else {
                return pos;
            }
        },
        update: function(object) {
            let x = object.x;
            let y = object.y;
            let vx = object.vx;
            let vy = object.vy;

            this.lineConfig.points[0] = x;
            this.lineConfig.points[1] = y;

            this.wedgeConfig.x = x - vx/VELOCITY_SCALE;
            this.wedgeConfig.y = y - vy/VELOCITY_SCALE;

            this.lineConfig.points[2] = this.wedgeConfig.x;
            this.lineConfig.points[3] = this.wedgeConfig.y;

            if (Math.hypot(vx, vy) < 1 && this.object.rotation) {
                this.wedgeConfig.rotation = this.object.rotation - 30;
            } else {
                this.wedgeConfig.rotation = Math.atan2(-vy, -vx) * 180/Math.PI + 150;
            }
        }
    },
    watch: {
        object: {
            deep: true,
            handler: function(newVal) {
                this.update(newVal);
            }
        }
    }
};
