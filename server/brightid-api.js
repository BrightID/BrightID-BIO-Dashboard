const image2base64 = require('image-to-base64');
const randomBytes = require('randombytes');
const fetch = require("node-fetch");
const nacl = require('tweetnacl');
const qrcode = require("qrcode");
const crypto = require("crypto");
const B64 = require('base64-js');
var Promise = require('promise');
const axios = require('axios');


var ipAddress = "68.183.76.106";
var serverIp = "*"; //Set it after launch
var brightidPublicKey = "e3748d3z-t281-vx73-u9qc-zu9ee8b9m1h0";


// server init
const express = require('express');
var bodyParser = require("body-parser");
const app = express();
const port = 2200;

app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(express.json());
app.all('*', function (req, res, next) {
  //if (!req.get('Origin')) return next();

  res.set('Access-Control-Allow-Origin', serverIp);
  res.set('Access-Control-Allow-Methods', 'GET,POST');
  res.set('Access-Control-Allow-Headers', 'X-Requested-With,Content-Type');

  if ('OPTIONS' == req.method) return res.send(200);

  next();
});


// routes
app.get('/new-code', (req, res) => {
  const aesKey = randomBytes(16).toString('base64');
  const uuid = b64ToUrlSafeB64(randomBytes(9).toString('base64'));
  const qrString = `${aesKey}${uuid}${b64Ip}`;
  const channel = uuid + "1";
  postData(channel, aesKey);
  res.setHeader('Content-Type', 'application/json');
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  res.send(JSON.stringify({ status: true, 'qr': qrString, uuid: uuid, ae: aesKey }));
});

app.post('/check-code', (req, res) => {
  let uuid = req.body.uuid;
  let ae = req.body.ae;
  uuid = uuid + "2";
  console.log(uuid, ae)
  getResponse(uuid, ae).then(function (data) {
    res.send(JSON.parse(data));
  });
});


app.listen(port, () => console.log(`Server listening on port ${port}!`))



// app functions
function uuid4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

function strToUint8Array(str) {
  return new Uint8Array(Buffer.from(str, 'ascii'));
}

function b64ToUint8Array(str) {
  // B64.toByteArray might return a Uint8Array, an Array or an Object depending on the platform.
  // Wrap it in Object.values and new Uint8Array to make sure it's a Uint8Array.
  let arr = B64.toByteArray(str);
  arr = Object.values(arr);
  arr = new Uint8Array(arr);
  return arr;
}

function uInt8ArrayToB64(array) {
  const b = Buffer.from(array);
  return b.toString('base64');
}

function b64ToUrlSafeB64(s) {
  const alts = {
    '/': '_',
    '+': '-',
    '=': ''
  };
  return s.replace(/[/+=]/g, (c) => alts[c]);
}

function getResponse(channel, aesKey) {
  return new Promise(function (resolve) {
    fetch(`http://${ipAddress}/profile/download/${channel}`).then(res => res.json()).
      then(function (data) {
        if (!data.data) {
          resolve(JSON.stringify({ status: false, msg: 'No data' }));
          return;
        }

        const decipher = crypto.createDecipher('aes128', aesKey);
        const decrypted =
          decipher.update(data.data, 'base64', 'utf8') + decipher.final('utf8');
        const decryptedObj = JSON.parse(decrypted);

        var publicKey2 = decryptedObj.publicKey;
        var timestamp = decryptedObj.timestamp;


        const message = strToUint8Array(publicKey2 + brightidPublicKey + timestamp);
        const sig = decryptedObj.signedMessage;

        if (nacl.sign.detached.verify(message, b64ToUint8Array(sig), b64ToUint8Array(publicKey2))) {
          resolve(JSON.stringify({ status: true, msg: 'verified', data: decryptedObj }));
        }
        else {
          resolve(JSON.stringify({ status: false, msg: 'Your bright id not verified' }));
        }
      });
  });
}

function postData(channel, aesKey) {
  image2base64("../ui/assets/image/avatar.jpg").then(function (res) {
    var photo = `data:image/jpeg;base64,${res}`;
    const dataObj = {
      publicKey: brightidPublicKey,
      photo,
      name: "BrightID",
      score: 10,
      signedMessage: null,
      timestamp: Date.now(),
    };

    const dataStr = JSON.stringify(dataObj);

    const cipher = crypto.createCipher('aes128', aesKey);

    let encrypted =
      cipher.update(dataStr, 'utf8', 'base64') + cipher.final('base64');

    // upload data to server
    fetch(`http://${ipAddress}/profile/upload`, {
      method: 'POST', // or 'PUT'
      body: JSON.stringify({ data: encrypted, uuid: channel }),
      headers: {
        'Content-Type': 'application/json',
      },
    }).then((res) => {
      if (res.status === 200) {
        console.log('successfully uploaded data')
      }
    }).catch((err) => {
      console.log(err);
    });
  });
}

const b64Ip = Buffer.from(
  ipAddress.split('.').map((octet) => parseInt(octet, 10)),
)
  .toString('base64')
  .substring(0, 6);
