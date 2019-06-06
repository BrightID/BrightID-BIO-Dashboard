var bioMinter = bio10Minter = stableToken = null;
var enoughFund = false;

elementInit = function () {
  $('#myModal').modal({
    backdrop: 'static',
    keyboard: false
  });
  $('.confirm-icon').hide();
  $('.loader').hide();
}

metaMaskInit = function () {
  elementInit();
  enoughFund = false;
  if (typeof web3 === 'undefined') {
    Swal.fire({
      type: 'error',
      title: 'MetaMask is not installed',
      text: 'Please install MetaMask from below link',
      footer: '<a href="https://metamask.io">Install MetaMask</a>'
    });
    return;
  }

  web3.eth.getAccounts(function (err, accounts) {
    if (err != null) {
      Swal.fire({
        type: 'error',
        title: 'Something wrong',
        text: 'Check this error: ' + err,
        footer: ''
      });
    }
    else if (accounts.length === 0) {
      Swal.fire({
        type: 'info',
        title: 'MetaMask is locked',
        text: 'Please unlocked MetaMask',
        footer: ''
      });
    }
  });
  if (window.ethereum) {
    window.web3 = new Web3(ethereum);
    try {
      Web3.providers.HttpProvider.prototype.sendAsync = Web3.providers.HttpProvider.prototype.send;
      ethereum.enable();
    } catch (error) {
      console.log('User denied account access...');
      return;
    }
  }
  else if (window.web3) {
    window.web3 = new Web3(web3.currentProvider);
  }
  else {
    console.log('You should consider trying MetaMask!');
    return;
  }

  web3.eth.defaultAccount = web3.eth.accounts[0];

  var bio_contract = web3.eth.contract(bioMinterAbi)
  bioMinter = bio_contract.at(bioMinterAddress);

  var bio_ten_contract = web3.eth.contract(bio10MinterAbi)
  bio10Minter = bio_ten_contract.at(bio10MinterAddress);

  var stable_token_contract = web3.eth.contract(stableTokenAbi)
  stableToken = stable_token_contract.at(stableTokenAddress);

};
