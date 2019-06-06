<template type="text/x-template">
  <div class>
    <div class="row justify-content-center">
      <h3 class="col col-lg-3 col-md-6 col-sm-12 dashboard-header">BrightID Dashboard</h3>
      <div
        class="offset-lg-7 col-md-6 col-lg-2 col-sm-12 profile"
        v-if="$root.accountInfo.data.photoURL"
      >
        <img :src="'user-photo/' + $root.accountInfo.data.photoURL">
        <p>{{$root.accountInfo.data.name}}</p>
      </div>
      <hr>
      <div class="col row col-sm-12 col-md-12 col-lg-4 box">
        <div class="item col col-6">
          <span>BrightId Score:</span>
        </div>
        <div class="col col-6 row">
          <div class="value col col-6">{{$root.accountInfo.data.score}}</div>
        </div>
      </div>
    </div>
    <hr>
    <div class="row justify-content-center" style="margin-top: 5%;">
      <div class="col col-12">
        <ul class="auth-items">
          <li
            class="row justify-content-center"
            :class="{ done: $root.accountInfo.data.ethereum_address }"
          >
            <div class="item-con">
              <a
                :href="$root.accountInfo.data.ethereum_address ? '#' : '#/ethereum-address'"
                class="auth-item"
              >Prove Your Ether Account</a>
              <img
                src="assets/image/confirm.png"
                height="25"
                class="confirm"
                v-if="$root.accountInfo.data.ethereum_address"
              >
              <span class="dot" v-else></span>
            </div>
          </li>
          <li
            class="row justify-content-center"
            :class="{ done: $root.accountInfo.data.brightid_level_reached }"
          >
            <div class="item-con">
              <a
                :disabled="$root.accountInfo.data.brightid_level_reached"
                href="#"
                class="auth-item"
              >+90 BrightID Score</a>
              <img
                src="assets/image/confirm.png"
                height="25"
                class="confirm"
                v-if="$root.accountInfo.data.brightid_level_reached"
              >
              <span class="dot" v-else></span>
            </div>
          </li>
          <li
            class="row justify-content-center"
            :class="{ done: $root.accountInfo.data.received_bio }"
          >
            <div class="item-con">
              <a
                :disabled="$root.accountInfo.data.received_bio "
                href="#"
                class="auth-item"
              >Earned BIO Token</a>
              <img
                src="assets/image/confirm.png"
                height="25"
                class="confirm"
                v-if="$root.accountInfo.data.received_bio "
              >
              <span class="dot" v-else></span>
            </div>
            <hr class="inside">
          </li>
        </ul>
      </div>
      <div>
        <a v-on:click="buy()" class="btn btn-primary buy-btn">Buy</a>
      </div>
    </div>
  </div>
</template>

<script>
module.exports = {
  data: function() {
    return {};
  },
  props: [],
  methods: {
    init() {
      this.$root.accountInfo.data;
    },
    buy() {
      if (!this.$root.accountInfo.data.ethereum_address) {
        Swal.fire({
          type: "info",
          title: "Please submit your ether account first",
          text: "Click <Prove Your Ether Account> on the top of the list"
        });
        return;
      }
      if (!this.$root.accountInfo.data.brightid_level_reached) {
        Swal.fire({
          type: "info",
          title: "Your BrightID score is less than 90",
          text: "You have to reach +90 score"
        });
        return;
      }
      router.push("/buy");
    }
  },
  mounted() {
    this.$root.isLogin();
    this.$root.publicKey = localStorage.getItem("publicKey");
    this.$root.getInfo();
    this.init();
  }
};
</script>


<style lang="css" scoped>
.dot {
  height: 25px;
  width: 25px;
  background-color: #bbb;
  border-radius: 50%;
  display: inline-block;
}
.auth-items {
  list-style-type: none;
}
.auth-items .done a {
  color: #000 !important;
  font-size: 1.5em;
  font-family: proxima-light;
  margin-right: 5%;
}
.auth-items a {
  color: #b9b9b9 !important;
  font-size: 1.5em;
  font-family: proxima-light;
  margin-right: 5%;
}
.btn-block {
  display: block;
  width: 100%;
}
.profile {
  position: relative;
  display: inline-flex;
}
.profile img {
  height: 60px;
  /*-webkit-filter: grayscale(100%);*/
  /*filter: grayscale(100%);*/
  border-radius: 100%;
  box-shadow: 0px 0px 10px 0 #000000;
}
.profile p {
  margin-top: 20px;
  margin-left: 10px;
  font-size: 12px;
}
.box {
  border: 1px solid black;
  height: 100%;
}
.box .item {
  height: 6vmin;
  left: -15px;
  background-color: #ed4e17;
}
.box .item span {
  -webkit-transform: translate(-50%, -50%);
  transform: translate(-50%, -50%);
  top: 50%;
  left: 50%;
  width: 100%;
  position: absolute;
  color: #000;
  font-size: 3vmin;
  font-family: proxima-light;
  text-align: center;
}
.box .value {
  font-size: 4vmin;
  margin: auto;
  font-family: proxima-regular;
}
.buy-btn {
  background-color: whitesmoke;
  width: 150px;
  border-color: black;
  color: white;
  font-size: 18px;
  font-weight: bold;
}
.item-con {
  width: 550px;
}
.item-con img {
  float: right;
  margin-right: 10%;
}
.item-con span {
  float: right;
  margin-right: 10%;
}
.dashboard-header {
  text-align: end;
}
</style>
