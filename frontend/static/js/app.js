new Vue({
    el: '#app',
    data: {
        jobs: [],
        selectedJob: null,
        applicantContext: '',
        generatedResume: ''
    },
    mounted() {
        this.fetchJobs();
    },
    methods: {
        fetchJobs() {
            fetch('/jobs')
                .then(response => response.json())
                .then(data => {
                    this.jobs = data;
                });
        },
        generateResume() {
            if (!this.selectedJob || !this.applicantContext) return;

            fetch('/generate_resume', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    job_title: this.selectedJob.title,
                    job_description: this.selectedJob.description,
                    applicant_context: this.applicantContext
                }),
            })
            .then(response => response.json())
            .then(data => {
                this.generatedResume = marked.parse(data.resume);
            });
        }
    },
    template: `
        <div>
            <h2>Select a Job</h2>
            <select v-model="selectedJob">
                <option value="">Choose a job...</option>
                <option v-for="job in jobs" :key="job.id" :value="job">
                    {{ job.title }} at {{ job.company }}
                </option>
            </select>

            <div v-if="selectedJob">
                <h2>Job Description Summary</h2>
                <p>{{ selectedJob.description_summary }}</p>
            </div>

            <h2>Applicant Information</h2>
            <textarea v-model="applicantContext" rows="10" placeholder="Enter your information here..."></textarea>

            <button @click="generateResume">Generate Resume</button>

            <div v-if="generatedResume" class="resume-container">
                <h2>Generated Resume</h2>
                <div v-html="generatedResume"></div>
            </div>
        </div>
    `
})
