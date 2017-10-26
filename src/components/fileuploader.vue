<template>
    <div class="container">
        <h1 class="title is-1">Upload pictures to PYBOSSA</h1>
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
        <dropzone ref="myuploader" id="myVueDropzone" 
                  url="/upload" acceptedFileTypes='image/*,.h264'
                  :maxFileSizeInMB=10 
                  :maxNumberOfFiles=1000
                  v-on:vdropzone-success="showIt">
                <input type="hidden" name="project_id" v-model="project_id">
                <input type="hidden" name="camera_id" v-model="camera_id">
        </dropzone>
        <h2 class="title is-2">List of created tasks</h2>
        <b-table
            :data="isEmpty ? [] : tableDataSimple"
            >

            <template scope="props">
                <b-table-column label="ID" width="40" numeric>
                    <a :href="apiUrl(props.row.id)" target="_blank">{{ props.row.id }}</a>
                </b-table-column>

                <b-table-column label="link">
                    <a :href="props.row.info.link" target="_blank">{{ props.row.info.link}}</a>
                </b-table-column>

                <b-table-column label="Video link" centered>
                    <a :ref="props.row.info.video" target="_blank">{{ props.row.info.video }}</a>
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
export default {
    data(){
        return {
            projects: [],
            project_id: null,
            camera_id: null,
            tableDataSimple: [],
            isEmpty: true,
            }
    },
    components: {Dropzone},
    computed: {
        projectNameOptions(){
            var tmp = []
            for (var project of this.projects) {
                console.log(project)
                tmp.push({id: project.id, name: project.short_name})
            }
            return tmp
        },
        projectCameras(){
            let project = _.find(this.projects, {id: this.project_id})
            if (project) return project.info.cameras
            else return []
        }
    },
    methods: {
        showIt(file, response) {
            console.log(file)
            console.log(response)
            this.isEmpty = false
            this.tableDataSimple.push(response.task)
        },
        apiUrl(id) {
            return "https://instantwildadmin.zsl.org/api/task/" + id
        }
    },
    created(){
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
}
</script>
