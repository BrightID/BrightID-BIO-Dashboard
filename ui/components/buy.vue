<template type="text/x-template">
  <div class>
    <h3 style="margin-left:60px;">Buy</h3>
    <hr>
    <div class="row justify-content-center" style="margin-top: 5%;">
      <div class="row col col-12 justify-content-center">
        <div class="col col-3">
          <div class="col col-12">
            <label class="token-label">Please select a token</label>
          </div>
          <div class="input-group mb-3 col col-12">
            <div class="input-group-prepend">
              <label class="input-group-text" for="coinSelect">Tokens</label>
            </div>
            <select class="custom-select" id="coinSelect" @change="selectToken($event)">
              <option value>Select a coin</option>
              <option value="bio">BIO</option>
              <option value="bio10">BIO 10</option>
            </select>
          </div>
        </div>
      </div>
      <div class="col col-6"></div>
    </div>
    <div>
      <bio v-if="symbol" v-bind:biosymbol="symbol"></bio>
    </div>
  </div>
</template>

<script>
module.exports = {
  data: function() {
    return {
      page: null,
      symbol: null,
      minterAddress: null,
      tokenAddress: null
    };
  },
  props: [],
  methods: {
    init() {
      this.$root.loader = false;
      metaMaskInit();
    },
    resetSymbol() {
      this.symbol = null;
    },
    selectToken(event) {
      if (!this.$root.publicKey) {
        router.push("/");
        return;
      }
      if (!web3.eth.defaultAccount) {
        Swal.fire({
          type: "error",
          title: "Can't detected your metamask"
        });
        return;
      }
      this.symbol = event.target.value;
    }
  },
  components: {
    bio: httpVueLoader("components/bio.vue")
  },
  mounted() {
    this.$root.isLogin();
    let app = this;
    setTimeout(function() {
      app.init();
    }, 1000);
  }
};
</script>


<style lang="css" scoped>
.brightid-logo {
  height: 60px;
}
@media only screen and (max-width: 600px) {
  .brightid-logo {
    height: 60px;
    margin-bottom: 10px;
  }
}
.token-label {
  font-size: 16px;
}
.btn-block {
  display: block;
  width: 100%;
}
</style>
