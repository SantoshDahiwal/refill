<template>
  <div id="app">
    <md-toolbar>
      <h1 class="md-title"><router-link class="nl" to="/">{{ msg('appname') }}<sup>&alpha;</sup></router-link></h1>

      <md-button href="https://en.wikipedia.org/wiki/User:Zhaofeng_Li/reFill" class="md-icon-button">
        <md-icon>help</md-icon>
      </md-button>
      <md-button href="https://en.wikipedia.org/wiki/User_talk:Zhaofeng_Li" class="md-icon-button">
        <md-icon>bug_report</md-icon>
      </md-button>
      <md-button href="https://github.com/zhaofengli/refill" class="md-icon-button">
        <md-icon>code</md-icon>
      </md-button>
    </md-toolbar>

    <transition name="slide">
      <router-view></router-view>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'app',
  data () {
    return {
    }
  }
}
</script>

<style lang="scss">
.md-title {
  flex: 1;
}
.main-content {
  max-width: 960px;
  margin: 0 auto;
  padding: 16px;
}
.nl {
  color: inherit !important;
  text-decoration: none !important;
}
.md-card {
  margin-bottom: 16px;
}
</style>
