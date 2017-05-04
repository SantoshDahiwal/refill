<template>
  <div class="main-content">
    <h1>{{ msg('result') }}</h1>
    <md-card class="progress-card">
      <md-card-content>
        <div class="icon-wrapper">
          <md-spinner :md-size="50" v-if="!loaded || running" md-indeterminate class="icon md-accent"></md-spinner>
          <md-icon v-else-if="state == 'PENDING'" class="icon">hourglass_empty</md-icon>
          <md-icon v-else-if="state == 'SUCCESS'" class="icon successful">done</md-icon>
          <md-icon v-else-if="state == 'FAILURE'" class="icon unsuccessful">error</md-icon>
          <md-icon v-else-if="state == 'REVOKED'" class="icon unsuccessful">cancel</md-icon>
          <md-icon v-else-if="state == 'BACKEND_ERROR'" class="icon unsuccessful">cloud_off</md-icon>
          <md-icon v-else class="icon">help</md-icon>
        </div>
        <div v-if="loaded" class="progress-wrapper">
          {{ msg('state-' + state) }}
          <div v-if="state != 'SUCCESS'" class="progress-description">{{ msg('state-' + state + '-description') }}</div>
        </div>
      </md-card-content>
      <md-progress v-if="loaded" :md-progress="stepPercentage * 100"></md-progress>
    </md-card>
    <div v-if="loaded">
      <div ref="diff" v-if="origWikicode && wikicode" v-html="diff">
      </div>
      <md-input-container>
        <md-textarea v-model="wikicode"></md-textarea>
      </md-input-container>

      <md-card v-if="errors.length > 0">
        <md-card-content>
          {{ msg('errorlist') }}
          <ul>
            <li v-for="error in errors">
              {{ error }}
            </li>
          </ul>
        </md-card-content>
      </md-card>

      <md-card class="action-card">
        <md-card-expand>
          <md-card-actions>
            <span class="tip">{{ msg('chancetoreview') }}</span>
            <md-button class="md-primary md-raised" @click.native="savePage" :disabled="!wikiAction">{{ msg('previewandsave') }}</md-button>
            <md-button class="md-icon-button" md-expand-trigger>
              <md-icon>keyboard_arrow_down</md-icon>
            </md-button>
          </md-card-actions>
          <md-card-content>
            <h2>{{ msg('taskinfo') }}</h2>
            <ul>
              <li>{{ msg('taskinfo-name') }}: {{ taskName }}</li>
              <li>{{ msg('taskinfo-id') }}: {{ taskId }}</li>
              <li>{{ msg('taskinfo-state') }}: {{ state }}</li>
              <li>{{ msg('taskinfo-percentage') }}: {{ percentage }}</li>
              <li>{{ msg('taskinfo-running') }}: {{ running }}</li>
              <li>{{ msg('taskinfo-submiturl') }}: {{ wikiAction }}</li>
            </ul>
          </md-card-content>
        </md-card-expand>
      </md-card>
    </div>
    <form class="fake-editform" ref="form" name="editform" method="post" v-bind:action="wikiAction">
      <textarea type="hidden" name="wpTextbox1">{{ wikicode }}</textarea>
      <input type="hidden" name="wpAutoSummary" value="fakehash">
      <input type="hidden" name="wpSummary" v-bind:value="summary">
      <input type="hidden" name="wpStarttime" v-bind:value="startTime">
      <input type="hidden" name="wpEdittime" v-bind:value="editTime">
      <input type="hidden" name="wpDiff" value="Show changes">
    </form>
    </div>
  </div>
</template>
<script>
import oboe from 'oboe';
import get from 'lodash/get';
import isEmpty from 'lodash/isEmpty';
import WikEdDiff from 'wdiff';
import URI from 'urijs';
export default {
  data () {
    return {
      loaded: false,
      running: false,
      state: 'UNKNOWN',
      percentage: 0,
      stepPercentage: 0,
      taskName: 'unknown',
      taskId: '',
      task: {},
      errors: [],
      wikicode: '',
      origWikicode: '',
      diff: '',
      summary: '',
      startTime: '',
      editTime: '',
      wikiAction: '',
    }
  },
  created () {
    this.fetchData();
  },
  watch: {
    '$route': 'fetchData'
  },
  methods: {
    fetchData () {
      this.loaded = false;
      this.taskId = this.$route.params.taskId;
      this.taskName = this.$route.params.taskName;
      this.origWikitext = '';

      // Stream status with Oboe.js
      oboe({
        url: this.$config.api + '/statusStream/' + this.taskName + '/' + this.taskId
      })
      .node('{state info}', (node) => {
        this.loaded = true;
        this.task = node;
        this.state = this.task.state;
        switch (this.state) {
          case 'PROGRESS':
            // Show progress for the whole task and the current step
            let stepPercentage = get(this.task.info.transforms,
              [this.task.info.overall.currentTransform, 'percentage']
            )
            if (stepPercentage) {
              this.stepPercentage = stepPercentage;
            }

            this.percentage = this.task.info.overall.percentage;
            this.running = true;
            break;
          case 'SUCCESS':
            this.percentage = 1;
            this.stepPercentage = 1;
            this.running = false;
            break;
          case 'FAILURE':
          case 'REVOKED':
          case 'PENDING':
            this.running = false;
            return;
        }

        // Show result and compute diff
        this.wikicode = this.task.info.wikicode;
        let origWikicode = get(this.task, 'info.origWikicode');
        if (origWikicode) {
          this.origWikicode = origWikicode;
        }
        let wdiff = new WikEdDiff();
        this.diff = wdiff.diff(this.origWikicode, this.wikicode);

        // Show errors
        let fillRefErrors = get(this.task, 'info.transforms.FillRef.metadata.errors');
        if (fillRefErrors) {
          this.errors = fillRefErrors;
        }

        // Construct fake edit form
        let wikipage = get(this.task, 'info.wikipage');
        if (!isEmpty(wikipage)) {
          this.wikiAction = URI(wikipage.path)
            .domain(wikipage.domain)
            .protocol(wikipage.protocol)
            .query({
              'title': wikipage.upage,
              'action': 'submit'
            })
            .toString();
          this.editTime = wikipage.editTime;
          this.startTime = wikipage.startTime;
        }

        // Generate edit summary
        // FIXME: Use `toollink`
        let fillCount = get(this.task, 'info.transforms.FillRef.metadata.count', 0);
        this.summary = this.msg('summary', fillCount, 0, 'reFill 2');
      })
      .done((json) => {
        if (this.state == 'PROGRESS') {
          console.log('Not done yet - Initiating another request');
          this.fetchData();
        }
      })
      .fail(() => {
        this.loaded = true;
        this.running = false;
        this.state = 'BACKEND_ERROR';
      });
    },
    savePage() {
      this.$refs.form.submit();
    }
  }
}
</script>
<style lang="scss" scoped>
.md-input-container textarea {
  transition: all 0s;
  font-family: monospace !important;
  min-height: 400px;
  overflow: scroll !important;
}
.icon-wrapper {
  position: relative;
  display: inline-block;
  padding: 0;
  width: 50px;
  height: 50px;
  line-height: 50px;
  vertical-align: top;

  .icon {
    position: absolute;
    font-size: 50px;
    line-height: 50px;
  }
  .successful {
    color: green;
  }
  .unsuccessful {
    color: red;
  }
}
.progress-wrapper {
  position: relative;
  display: inline-block;
  font-size: 20px;
  line-height: 50px;
  vertical-align: top;
}
.progress-description {
  font-size: 15px;
}
.fake-editform {
  display: none;
}
.action-card {
  padding-top: 8px;
  .tip {
    margin-right: 8px;
  }
}
</style>
<style lang="scss">
/* Materialize */
.wikEdDiffFragment {
  box-shadow: 0 1px 5px rgba(0,0,0,.2), 0 2px 2px rgba(0,0,0,.14), 0 3px 1px -2px rgba(0,0,0,.12) !important;
  border-radius: 2px !important;
  border: none !important;
}
</style>
