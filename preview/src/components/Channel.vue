<template>
    <div class="channel" v-bind:class="{ on: active }" ref="myDraggable" :style="styleObject">
        <h1>{{label}}</h1>
        <p>{{ active ? "Active" : "Inactive" }}</p>
    </div>
</template>

<script>
import interact from "interactjs";

export default {
    name: "Channel",
    props: ['label', 'active', 'idx'],
    data() {
        var idx = parseInt(this.idx);

        var row = Math.floor(idx/5);
        var rowPos = idx - (row*5);

        return {
            screenX: 0,
            screenY: 0,
            screenWidth: 120,
            screenHeight: 120,
            row: row,
            rowPos: rowPos,
            styleObject: {
                left: rowPos*125 + 'px',
                top: row*125 + 'px',
            }
        }
    },
    mounted: function() {
        let myDraggable = this.$refs.myDraggable;
        myDraggable.style.left = this.left;
        this.initInteract(myDraggable);
    },
    methods: {
        initInteract: function(selector) {
            interact(selector).draggable({
                inertia: true,

                restrict: {
                    restriction: "parent",
                    endOnly: true,
                    elementRect: { top: 0, left: 0, bottom: 1, right: 1 }
                },
                // enable autoScroll
                autoScroll: true,

                // call this function on every dragmove event
                onmove: this.dragMoveListener,
                // call this function on every dragend event
                onend: this.onDragEnd
            })
            .resizable({
                edges: { left: true, top: true, right: true, bottom: true },

                restrictEdges: {
                    outer: "parent",
                    endOnly: true,
                },
                inertia: true,
            })
            .on('resizemove', this.resizeMoveListener)
            ;
        },
        dragMoveListener: function(event) {
            var target = event.target,
            // keep the dragged position in the data-x/data-y attributes
            x = (parseFloat(target.getAttribute("data-x")) || this.screenX) + event.dx,
            y = (parseFloat(target.getAttribute("data-y")) || this.screenY) + event.dy;

            // translate the element
            target.style.webkitTransform = target.style.transform = "translate(" + x + "px, " + y + "px)";

            // update the posiion attributes
            target.setAttribute("data-x", x);
            target.setAttribute("data-y", y);
        },
        resizeMoveListener: function (event) {
            var target = event.target,
                x = (parseFloat(target.getAttribute('data-x')) || 0),
                y = (parseFloat(target.getAttribute('data-y')) || 0);

            // update the element's style
            target.style.width  = event.rect.width + 'px';
            target.style.height = event.rect.height + 'px';

            // translate when resizing from top or left edges
            x += event.deltaRect.left;
            y += event.deltaRect.top;

            target.style.webkitTransform = target.style.transform = 'translate(' + x + 'px,' + y + 'px)';

            target.setAttribute('data-x', x);
            target.setAttribute('data-y', y);
            target.setAttribute('data-width', event.rect.width);
            target.setAttribute('data-height', event.rect.height);
        },
        onDragEnd: function(event) {
            var target = event.target;
            // update the state
            this.screenX = target.getBoundingClientRect().left;
            this.screenY = target.getBoundingClientRect().top;
        }
    }
}
</script>

<style>
.channel {
    border: 1px solid rgba(0, 0, 0, 0.5);
    background: rgba(0, 0, 0, 0.3);
    font-size: 14px;
    color: black;
    width: 120px;
    height: 120px;
    position: absolute;
    display: block;
    left: 0;
    top: 0;
    margin: 5px;
}
.channel h1 {
    font-size: 16px;
}
.channel.on {
    border: 1px solid rgba(255, 13, 255, 0.7);
    background: rgba(255, 13, 255, 0.5);
}
</style>