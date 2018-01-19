<template>
    <div class="container">
        <h1 class="title is-1">Upload pictures or videos to PYBOSSA</h1>
        <b-field label="Project Name">
            <b-select placeholder="Select a name" v-model="project_id">
                <option
                      v-for="option in projectNameOptions"
                      :value="option.id"
                      :key="option.id">
                {{ option.name}}
                </option>
            </b-select>
        </b-field>
        <b-field label="Project's camera">
            <b-select placeholder="Select a camera" v-model="camera_id">
                <option
                      v-for="option in projectCameras"
                      :value="option.cameraID"
                      :key="option.cameraID">
                {{ option.cameraID}}
                </option>
            </b-select>
        </b-field>
        <b-field label="Deployments">
            <b-select placeholder="Select a deployment" v-model="deploymentLocationID">
                <option
                      v-for="option in projectLocations"
                      :value="option.deploymentLocationID"
                      :key="option.deploymentLocationID">
                {{ option.deploymentLocationID }}
                </option>
            </b-select>
        </b-field>

        <dropzone ref="myuploader" id="myVueDropzone" 
                  url="/upload" acceptedFileTypes='image/*,.h264,.mp4'
                  :maxFileSizeInMB=10 
                  :maxNumberOfFiles=1000
                  v-on:vdropzone-success="showIt">
                <input type="hidden" name="project_id" v-model="project_id">
                <input type="hidden" name="project_name" v-model="project_name">
                <input type="hidden" name="camera_id" v-model="camera_id">
                <input type="hidden" name="room" v-model="room">
                <input type="hidden" name="deploymentLocationID" v-model="deploymentLocationID">
        </dropzone>
        <h2 class="title is-2">List of created tasks</h2>
        <b-table
            :data="isEmpty ? [] : tableDataSimple"
            >

            <template scope="props">
                <b-table-column label="ID" width="40" numeric>
                    <button v-if="props.row.id === 'processing'" class="button is-white is-loading" disabled> Processing </button>
                    <a v-else :href="apiUrl(props.row.id)" target="_blank">{{ props.row.id }}</a>
                </b-table-column>

                <b-table-column label="link">
                    <button v-if="props.row.id === 'processing'" class="button is-white is-loading" disabled> Processing </button>
                    <a v-else :href="props.row.info.link" target="_blank">{{ props.row.info.link}}</a>
                </b-table-column>

                <b-table-column label="Video link" centered>
                    <button v-if="props.row.id === 'processing'" class="button is-white is-loading" disabled> Processing </button>
                    <a v-else :ref="props.row.info.video" target="_blank">{{ props.row.info.video }}</a>
                </b-table-column>
            </template>

            <template slot="empty">
                <section class="section">
                    <div class="content has-text-grey has-text-centered">
                        <p>
                            <b-icon
                                icon="sentiment_very_dissatisfied"
                                size="is-large">
                            </b-icon>
                        </p>
                        <p>Nothing here.</p>
                    </div>
                </section>
            </template>
        </b-table>
    </div>
</template>
<script>
import Dropzone from 'vue2-dropzone'
import axios from 'axios'
import _ from 'lodash'
import io from 'socket.io-client'
import uid from 'uid-safe'

export default {
    data(){
        return {
            socket: null,
            room: '',
            projects: [],
            project_id: null,
            camera_id: null,
            deploymentLocationID: null,
            tableDataSimple: [],
            isEmpty: true,
            }
    },
    components: {Dropzone},
    computed: {
        project_name() {
            let project = _.find(this.projects, {id: this.project_id})
            if (project !== undefined) {
                return project.name
            }
            else {
                return ""
            }
        },
        projectNameOptions(){
            var tmp = []
            for (var project of this.projects) {
                tmp.push({id: project.id, name: project.short_name})
            }
            return tmp
        },
        projectCameras(){
            let project = _.find(this.projects, {id: this.project_id})
            if (project && project.info.cameras) return project.info.cameras
            else return []
        },
        projectLocations(){
            let project = _.find(this.projects, {id: this.project_id})
            if (project && project.info.deploymentlocations) return project.info.deploymentlocations
            else return []
        }

    }  ,
    methods: {
        showIt(file, response) {
          this.isEmpty = false
          this.tableDataSimple.push({id: 'processing', info: {link: 'processing', 'filename': file.name}})
        },
        apiUrl(id) {
            return "https://instantwildadmin.zsl.org/api/task/" + id
        }
    },
    sockets: {
      connect() {
        console.log('connected to socketio')
        console.log('Joining room:' + this.room)
        this.$socket.emit('join', {room: this.room})
      },
      jobStatus (data) {
        console.log('job completed')
        this.isEmpty = false
        let index = _.findIndex(this.tableDataSimple, function (n) {
          return n.info.filename === data.task.info.filename
        })

        this.tableDataSimple.splice(index, 1, data.task)
      }
    },
    created(){
        this.room = uid.sync(18)
        var url = '/projects'
        var self = this
        axios.get(url)
            .then(response => {
                self.projects = response.data
                var projectNames = []
                for (var project of self.projects) {
                    projectNames.push({id: project.id, name: project.short_name})
                }
            })
            .catch(error => {console.log(error)})
    },
    watch: {
        'project_id': function(newVal) {
            this.deploymentLocationID = null
            this.camera_id = null
        }
    }
}
</script>
<style>
</style>
