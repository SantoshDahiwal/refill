<template>
  <div>
    <v-container fluid grid-list-lg>
      <v-layout row wrap>
        <v-flex xs12>
          <h1>{{ msg('appname') }}<sup class="ng">&alpha;</sup></h1>
          <h2 class="tagline">{{ msg('tagline') }}</h2>
        </v-flex>
      </v-layout>
      <v-layout row wrap>
        <v-flex xs12>
          <v-card>
            <v-card-title primary-title>
              <div class="headline">Here be dragons</div>
            </v-card-title>
            <v-card-text>
              <p>This is an unreleased version of reFill which may have numerous bugs and other oddities. Be sure to check every edit before saving.</p>
            </v-card-text>
            <v-card-actions>
              <v-btn flat href="https://tools.wmflabs.org/refill">Return to stable version</v-btn>
            </v-card-actions>
          </v-card>
        </v-flex>
      </v-layout>

      <v-layout row wrap>
        <v-flex xs12>
          <v-card>
            <v-card-title primary-title>
              <div class="headline">{{ msg('fixwikipage') }}</div>
            </v-card-title>
            <v-card-text>
              <div class="wikipage-form">
                <v-text-field
                  v-model="page"
                  class="page"
                  placeholder=""
                  :label="msg('fixwikipage-page')"
                ></v-text-field>
                <v-text-field
                  v-model="code"
                  class="code"
                  :label="msg('fixwikipage-code')"
                ></v-text-field>
                <v-text-field
                  v-model="fam"
                  class="fam"
                  :label="msg('fixwikipage-fam')"
                ></v-text-field>

                <v-btn fab @click="fixWikipage">
                  <v-icon>arrow_forward</v-icon>
                </v-btn>
              </div>
            </v-card-text>
          </v-card>
        </v-flex>
      </v-layout>

      <v-layout>
        <v-flex xs12>
          <v-card>
            <v-card-title>
              <div class="headline">{{ msg('fixwikicode') }}</div>
            </v-card-title>
            <v-card-text>
              <v-text-field
                v-model="wikicode"
                class="wikicode"
                :label="msg('fixwikicode-wikicode')"
                textarea
              ></v-text-field>
            </v-card-text>
            <v-card-actions>
              <v-btn flat @click="fixWikicode">
                {{ msg('fixwikicode-submit') }}
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-flex>
      </v-layout>
    </v-container>

    <v-snackbar
      ref="taskerror"
      v-model="showError"
    >
      <span>{{ error }}</span>
    </v-snackbar>
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
      error: '',
      showError: false,
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
        this.showError = true;
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
