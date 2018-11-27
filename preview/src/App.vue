<template>
    <div id="app">
        <div class="file-upload-form">
            Upload an image file:
            <input type="file" @change="previewImage" accept="image/*">
            <input type="file" @change="loadConfig" accept="application/json">
            <button @click="play">Play</button>
        </div>
        <div id="command">
            <p v-if="currentCommand >= 0">
                {{ JSON.stringify(scriptCommands[currentCommand]) }}
            </p>
            <p v-else>
                Total Commands: {{scriptCommands.length}}
            </p>
        </div>
        <div id="display" class="image-preview">
            <img class="preview" :src="imageData">
            <Channel v-for="(item, key) in channels" :id="key" :key="key" v-bind:label="key" v-bind:active="item.active" v-bind:idx="item.idx" />
        </div>
    </div>
</template>

<script>
import Channel from "./components/Channel";

function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

export default {
    name: 'App',
    components: {
        Channel
    },
    data() {
        return {
            imageData: "",
            scriptCommands: [],
            currentCommand: -1,
            channels: {}
        }
    },
    methods: {
        previewImage: function(event) {
            var input = event.target;
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.onload = (e) => {
                    // Note: arrow function used here, so that "this.imageData" refers to the imageData of Vue component
                    // Read image as base64 and set to imageData
                    this.imageData = e.target.result;
                }
                reader.readAsDataURL(input.files[0]);
            }
        },
        loadConfig: function(event) {
            var input = event.target;
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.onload = (e) => {
                    try {
                        this.scriptCommands = JSON.parse(e.target.result);
                        this.createChannels();
                    } catch (ex) {
                        alert('Failed to parse JSON: ' + ex);
                    }
                }
                reader.readAsText(input.files[0]);
            }
        },
        createChannels: function() {
            var counter = 0;
            for (var i = 0; i < this.scriptCommands.length; i++) {
                for (var idx in this.scriptCommands[i].changes) {
                    if (idx in this.channels) {
                        continue;
                    }

                    this.channels[idx] = { 'active': false, 'idx': counter++ }
                }
            }
        },
        play: async function() {
            for (this.currentCommand = 0; this.currentCommand < this.scriptCommands.length; this.currentCommand++) {
                let cmd = this.scriptCommands[this.currentCommand]
                await sleep(cmd.timeout * 1000);

                for (var idx in cmd.changes) {
                    if (idx in this.channels) {
                        this.channels[idx].active = cmd.changes[idx]
                    }
                }
            }
        }
    }
}
</script>

<style lang="scss">
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  text-align: center;
}

#command {
    font-family: monospace;
}

#display {
    position: relative;
    padding: 0;
    margin: 0;
    border: 1px solid red;
    min-width: 800px;
    min-height: 600px;
}

img.preview {
    width: 800px;
    background-color: black;
    border: 1px solid #DDD;
    opacity: 0.8;
}
</style>