<template>
  <div class="main-content">
    <h1>{{ msg('appname') }}<sup class="ng">&alpha;</sup></h1>
    <h2 class="tagline">{{ msg('tagline') }}</h2>
    <md-card class="md-accent">
      <md-card-header>
        <div class="md-title">Here be dragons</div>
      </md-card-header>
      <md-card-content>
        <p>This is an unreleased version of reFill which may have numerous bugs and other oddities. Be sure to check every edit before saving.</p>
      </md-card-content>
      <md-card-actions>
        <md-button href="https://tools.wmflabs.org/refill">Return to stable version</md-button>
      </md-card-actions>
    </md-card>

    <md-card>
      <md-card-header>
        <div class="md-title">{{ msg('fixwikipage') }}</div>
      </md-card-header>
      <md-card-content>
        <form class="wikipage-form" @submit="fixWikipage" v-on:submit.prevent>
          <md-input-container class="page">
            <label>{{ msg('fixwikipage-page') }}</label>
            <md-input required v-model="page"></md-input>
          </md-input-container>
          <md-input-container class="code">
            <label>{{ msg('fixwikipage-code') }}</label>
            <md-input v-model="code"></md-input>
          </md-input-container>
          <md-input-container class="fam">
            <label>{{ msg('fixwikipage-fam') }}</label>
            <md-input v-model="fam"></md-input>
          </md-input-container>
          <md-button type="submit" class="md-primary md-fab">
            <md-icon>arrow_forward</md-icon>
          </md-button>
        </form>
      </md-card-content>
    </md-card>

    <md-card>
      <md-card-header>
        <div class="md-title">{{ msg('fixwikicode') }}</div>
      </md-card-header>
      <md-card-content>
        <md-input-container>
          <label>{{ msg('fixwikicode-wikicode') }}</label>
          <md-textarea required v-model="wikicode"></md-textarea>
        </md-input-container>
      </md-card-content>
      <md-card-actions>
        <md-button @click.native="fixWikicode">{{ msg('fixwikicode-submit') }}</md-button>
      </md-card-actions>
    </md-card>

    <md-card>
      <md-card-header>
      </md-card-header>
      <md-card-expand>
        <md-card-actions>
          <span style="flex: 1"></span>
          <md-button class="md-icon-button" md-expand-trigger>
            <md-icon>settings</md-icon>
          </md-button>
        </md-card-actions>
        <md-card-content>
          <md-input-container>
            <label>{{ msg('apiendpoint') }}</label>
            <md-input v-model="api" required></md-input>
          </md-input-container>
        </md-card-content>
      </md-card-expand>
    </md-card>

    <md-snackbar ref="taskerror">
      <span>{{ error }}</span>
    </md-snackbar>
  </div>
</template>
<script>
export default {
  data () {
    return {
      fam: 'wikipedia',
      code: 'en',
      page: '',
      wikicode: '<ref>http://example.com</ref>',
      error: ''
    }
  },
  created () {
    this.api = this.$config.api;
  },
  methods: {
    fixWikipage() {
      this.submitTask('fixWikipage', {
        'page': this.page,
        'fam': this.fam,
        'code': this.code
      });
    },
    fixWikicode() {
      this.submitTask('fixWikicode', {
        'wikicode': this.wikicode
      });
    },
    submitTask(action, payload) {
      this.$http.post(this.api + '/' + action, payload).then(response => {
        if (response.status == 202) {
          this.$router.push('/result/' + action + '/' + response.data.taskId);
        }
      }, response => {
        this.error = response.data.message;
        this.$refs.taskerror.open();
      });
    }
  }
}
</script>
<style lang="scss" scoped>
.tagline {
  font-weight: normal;
}
.ng {
  color: #666;
}
.wikicode {
  min-height: 200px;
}
.wikipage-form {
  display: flex;

  .page {
    flex: 6;
  }
  .code {
    flex: 1;
  }
  .fam {
    flex: 2;
  }
}
</style>
