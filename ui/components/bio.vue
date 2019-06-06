<template type="text/x-template">
  <div class>
    <!-- The Donate Modal -->
    <div v-if="!steps" class="modal animated fadeIn" id="myModal">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content">
          <!-- Modal Header -->
          <div class="modal-header">
            <h4 class="modal-title m-title">Buy</h4>
            <button type="button" class="close" data-dismiss="modal">&times;</button>
          </div>
          <!-- Modal body -->
          <div class="modal-body">
            <div class="col col-12 bio-input">
              <form>
                <div class="input-group mb-3">
                  <div class="input-group-prepend">
                    <span class="input-group-text modal-input-txt">{{symbol}}</span>
                  </div>
                  <input
                    type="text"
                    id="bio"
                    class="form-control just-number"
                    placeholder="1"
                    v-model="value"
                    disabled
                  >
                </div>
                <div class="input-group mb-3">
                  <div class="input-group-prepend">
                    <span class="input-group-text modal-input-txt">DAI</span>
                  </div>
                  <input
                    type="text"
                    id="dai"
                    class="form-control just-number"
                    placeholder="Dai Amount"
                    disabled
                    v-model="daiAmount"
                  >
                </div>
                <div class="col col-12" style="margin-bottom: 4%;">
                  <span id="msg"></span>
                </div>
                <button
                  id="buy-btn"
                  type="button"
                  v-on:click="getLicense"
                  v-if="daiAmount"
                  class="btn btn-outline-secondary col col-12 modal-buy-btn"
                >Buy</button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>

    <st-progress v-if="steps" v-bind:data="steps"></st-progress>
  </div>
</template>

<script>
module.exports = {
  data: function() {
    return {
      value: 1,
      daiAmount: null,
      steps: null,
      symbol: "",
      minterAddress: "",
      cb: null,
      minter: null
    };
  },
  props: ["biosymbol"],
  methods: {
    init() {
      let app = this;
      $("#myModal").on("hidden.bs.modal", function() {
        app.$parent.resetSymbol();
      });
      if (!this.biosymbol) {
        Swal.fire({
          type: "error",
          title: "Wrong data pass to bio"
        });
        app.$parent.resetSymbol();
        return;
      }
      metaMaskInit();
      let minter;
      switch (this.biosymbol) {
        case "bio":
          this.symbol = "BIO";
          this.minterAddress = bioMinterAddress;
          this.tokenAddress = bioTokenrAddress;
          this.cb = this.confirmBuyBIO;
          this.minter = bioMinter;
          break;
        case "bio10":
          this.symbol = "BIO10";
          this.minterAddress = bio10MinterAddress;
          this.tokenAddress = bio10TokenrAddress;
          this.cb = this.confirmBuyBIOten;
          this.minter = bio10Minter;
          break;
      }
      this.getPrice(this.minter);
    },
    getLicense(publicKey, tokenAddress, minterAddress) {
      let data = {
        publicKey: this.$root.publicKey,
        minterAddress: this.minterAddress,
        tokenAddress: this.tokenAddress,
        currentAddress: web3.eth.defaultAccount
      };
      let headers = getHeaders();
      this.$http.post("/bio-license", data, headers).then(
        function(response) {
          if (!response.data.status) {
            Swal.fire({
              type: "error",
              title: "Error",
              text: "Details: " + response.data.msg,
              footer: ""
            });
            return;
          }
          this.sig = response.data.sig;
          this.buy();
          console.log(this.sig);
        }
      );
    },
    getPrice(minter) {
      let app = this;
      minter.PRICE(function(error, result) {
        if (error) {
          Swal.fire({
            type: "error",
            title: "Error in connection",
            text: "Please refresh the page"
          });
          return;
        }
        app.daiAmount = result.c[0] / 10000;
      });
    },
    checkTRX(hash, cb) {
      let app = this;
      web3.eth.getTransactionReceipt(hash, function(error, result) {
        if (error) {
          console.error(error);
          setTimeout(function() {
            app.checkTRX(hash, cb);
          }, 10000);
          return;
        }
        if (result == null) {
          setTimeout(function() {
            app.checkTRX(hash, cb);
          }, 5000);
          return;
        }
        if (cb) cb();
        app.$root.$emit("nextStep");
      });
    },
    buy() {
      let app = this;
      this.steps = [
        {
          type: "metamask",
          text: "Confirm approve " + this.daiAmount + " DAI"
        },
        {
          type: "trx",
          text: "Waiting for confirmation"
        },
        {
          type: "metamask",
          text: "Confirm buy the BIO token"
        },
        {
          type: "trx",
          text: "Waiting for confirmation"
        }
      ];
      stableToken.approve.sendTransaction(
        app.minterAddress,
        this.daiAmount * 10 ** 18,
        function(error, result) {
          console.log(error, result);
          if (error) {
            console.log(error);
            Swal.fire({
              type: "error",
              title: "Something wrong",
              text: "Error message: " + String(error)
            });
            return;
          }
          app.checkTRX(result, app.cb);
          app.$root.$emit("nextStep");
        }
      );
    },
    confirmBuyBIOten() {
      // We use the separate function because next tokens may have different methods
      let app = this;
      let s = this.sig;
      if (s.msg != null) {
        Swal.fire({
          type: "error",
          title: s.msg
        });
        return;
      }
      this.minter.buy.sendTransaction(s.r, s.s, s.v, function(error, result) {
        if (error) {
          console.log(error);
          return;
        }
        app.checkTRX(result, app.done);
        app.$root.$emit("nextStep");
      });
    },
    confirmBuyBIO() {
      // We use the separate function because next tokens may have different methods
      let app = this;
      let s = this.sig;
      if (s.msg != null) {
        Swal.fire({
          type: "error",
          title: s.msg
        });
        return;
      }
      this.minter.buy.sendTransaction(s.timestamp, s.r, s.s, s.v, function(
        error,
        result
      ) {
        if (error) {
          console.log(error);
          return;
        }
        app.checkTRX(result, app.done);
        app.$root.$emit("nextStep");
      });
    },
    done() {
      let headers = getHeaders();
      this.$http.get("/recive-bio", headers).then(function(response) {});
      Swal.fire({
        type: "success",
        title: "Successfuly Done"
      });
    }
  },
  components: {
    "st-progress": httpVueLoader("components/step-progress.vue")
  },
  mounted() {
    this.$root.isLogin();
    this.init();
  },
  beforeDestroy() {
    this.$parent.resetSymbol();
  }
};
</script>


<style lang="css" scoped>
</style>
