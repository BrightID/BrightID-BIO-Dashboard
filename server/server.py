from serverbase import ErrorToClient, revoked_store, ACCESS_EXPIRES, REFRESH_EXPIRES
from flask import Blueprint, request, g, jsonify, send_from_directory, session
from web3 import Web3, HTTPProvider
from eth_keys import keys
import nacl.encoding
import nacl.signing
import requests
import base64
import config
import json
import uuid
import sha3
import os

from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token, get_jti,
    jwt_refresh_token_required, get_jwt_identity, jwt_required, get_raw_jwt
)

w3 = Web3(HTTPProvider(config.INFURA_URL))

bp = Blueprint('server', __name__)


def check_eth_addr(address):
    try:
        return w3.toChecksumAddress(address)
    except Exception:
        raise ErrorToClient('Invalid Address')


def priv2addr(private_key):
    pk = keys.PrivateKey(bytes.fromhex(private_key))
    return pk.public_key.to_checksum_address()


def hex2int(s):
    assert s.startswith('0x')
    return int(s[2:], 16)


def pad32(n):
    return format(n, '064X')


@bp.route('/get-info', methods=['POST'])
@jwt_required
def get_info():
    data = json.loads(request.data)
    if 'publicKey' not in data:
        session['publicKey'] = None
        raise ErrorToClient('Error in connection - No publicKey Founded')
    # TODO: check if needed
    res = g.db.members.find_one({'publicKey': data['publicKey']})
    if not res:
        session['publicKey'] = None
        raise ErrorToClient('No data')
    for key in ['_id', 'signedMessage', 'timestamp']:
        del res[key]
    session['publicKey'] = data['publicKey']
    return json.dumps({'status': True, 'data': res, 'brightid_confirm': True})


@bp.route('/submit-ethereum', methods=['POST'])
@jwt_required
def submit_ethereum():
    data = json.loads(request.data)
    if 'publicKey' not in data:
        raise ErrorToClient('Error in connection - No publicKey Founded')
    if 'account' not in data:
        raise ErrorToClient('Error in connection - No Account Founded')
    check_eth_addr(data['account'])
    res = g.db.members.find_one({'publicKey': data['publicKey']})
    if not res:
        raise ErrorToClient('No Public Key Founded')
    g.db.members.update_one({
        '_id': res['_id']
    }, {'$set': {
        'ethereum_address': data['account'],
    }},
        upsert=False)
    return json.dumps({'status': True})


@bp.route('/is-login')
@jwt_required
def is_login():
    return json.dumps(
        {'status': True, 'login_status': True, 'msg': 'You are login'})


def add_brightid_score(publicKey, brightid_level_reached=False, score=0):
    g.db.members.update_one({
        'publicKey': publicKey
    }, {'$set': {
        'score': score,
    }},
        upsert=False)
    if brightid_level_reached:
        return True
    score = True if score >= 90 else False
    g.db.members.update_one({
        'publicKey': publicKey
    }, {'$set': {
        'brightid_level_reached': score,
    }},
        upsert=False)
    if not score:
        return False
    return True


def init_types(data):
    data['brightid_level_reached'] = False
    data['bio_token_address'] = None
    data['received_bio'] = False
    return data


def jwt_create_token(publicKey):
    # Create our JWTs
    access_token = create_access_token(identity=publicKey)
    refresh_token = create_refresh_token(identity=publicKey)
    access_jti = get_jti(encoded_token=access_token)
    refresh_jti = get_jti(encoded_token=refresh_token)
    revoked_store.set(access_jti, 'false', ACCESS_EXPIRES * 1.2)
    revoked_store.set(refresh_jti, 'false', REFRESH_EXPIRES * 1.2)
    ret = {
        'access_token': access_token,
        'refresh_token': refresh_token
    }
    return ret


def save_photo(photo):
    filename = str(uuid.uuid4())
    # user photo its not important, so we save it in tmp folder
    path = '/tmp/brightid-user-images'
    if not os.path.exists(path):
        os.mkdir(path)
    data = photo.split(',')[1]
    data = base64.b64decode(data)
    with open('{}/{}.png'.format(path, filename), 'wb') as f:
        f.write(data)
    return filename


@bp.route('/user-photo/<file>')
def user_photo(file):
    return send_from_directory('/tmp/brightid-user-images/', file + '.png')


@bp.route('/login', methods=['POST'])
def submit_member():
    data = json.loads(request.data)
    if not verify_message(data['publicKey'], data['timestamp'],
                          data['signedMessage']):
        raise ErrorToClient('Invalid Data')

    res = g.db.members.find_one({'publicKey': data['publicKey']})
    r = {'status': True, 'publicKey': data['publicKey']}
    if res:
        add_brightid_score(data['publicKey'],
                           res['brightid_level_reached'], data['score'])
        token = jwt_create_token(data['publicKey'])
        r.update(token)
        return jsonify(r)

    data = init_types(data)
    data['photoURL'] = save_photo(data['photo'])
    del data['photo']
    g.db.members.insert_one(data)
    add_brightid_score(data['publicKey'], False, data['score'])
    token = jwt_create_token(data['publicKey'])
    r.update(token)
    return jsonify(r)


@bp.route('/logout')
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    revoked_store.set(jti, 'true', ACCESS_EXPIRES * 1.2)
    return json.dumps({'status': True, 'msg': 'Logout Successfully'})


@bp.route('/new-code')
def new_code():
    try:
        r = requests.get('http://127.0.0.1:2200/new-code')
        return r.text
    except Exception:
        raise ErrorToClient('Cant Get New Connection')


@bp.route('/check-code', methods=['POST'])
def check_code():
    data = json.loads(request.data)
    r = requests.post('http://127.0.0.1:2200/check-code', data=data)
    return r.text


@bp.route('/check-account', methods=['POST'])
def check_account():
    data = json.loads(request.data)
    account = check_eth_addr(data['account'])
    res = g.db.referrers.find_one({'account': account})
    if res:
        if res['registered']:
            raise ErrorToClient('Your account has already been registered',
                                {'referrer': res['referrer']})
    return json.dumps({'status': True, 'msg': 'Allow'})


def verify_message(public_key, timestamp, sig):
    message = bytearray(
        public_key + config.BRIGHTID_PUBLIC_KEY + str(timestamp), 'utf8')
    try:
        verify_key = nacl.signing.VerifyKey(
            public_key, encoder=nacl.encoding.URLSafeBase64Encoder)
        encoder = nacl.encoding.URLSafeBase64Encoder
        verify_key.verify(message, encoder.decode(sig))
        return True
    except Exception:
        return False


@bp.route('/bio-license', methods=['POST'])
@jwt_required
def bio_license():
    data = json.loads(request.data)
    publicKey = session.get('publicKey', None)
    if publicKey is None:
        raise ErrorToClient('Not login')
    res = g.db.members.find_one({'publicKey': publicKey})
    if not res:
        raise ErrorToClient('Cant find this id')
    elif not res['brightid_level_reached']:
        raise ErrorToClient('Low BrightID score')
    elif not res['ethereum_address']:
        raise ErrorToClient('First submit your Ethereum address')
    elif res['received_bio']:
        raise ErrorToClient('You have got BIO token before')
    elif data['currentAddress'] != res['ethereum_address']:
        raise ErrorToClient('You have submited another Ethereum address before')
    elif res['bio_token_address'] and res['bio_token_address'] != data['tokenAddress']:
        raise ErrorToClient('You have got license for another BIO token before')
    msg = '{0}{1}'.format(pad32(hex2int(res['ethereum_address'])), pad32(
        hex2int(data['tokenAddress'])))
    message_hash = sha3.keccak_256(bytes.fromhex(msg)).digest()
    signed_message = w3.eth.account.signHash(message_hash,
                                             private_key=config.NODE_PRIVATE)
    g.db.members.update_one({
        'publicKey': publicKey
    }, {'$set': {
        'bio_token_address': data['tokenAddress'],
    }},
        upsert=False)
    return json.dumps({'status': True, 'sig': {
        'r': '0x' + pad32(signed_message['r']),
        's': '0x' + pad32(signed_message['s']),
        'v': signed_message['v'],
    }})


@bp.route('/recive-bio')
@jwt_required
def recive_bio():
    publicKey = session.get('publicKey', None)
    if publicKey is None:
        raise ErrorToClient('Not login')
    g.db.members.update_one({
        'publicKey': publicKey
    }, {'$set': {
        'received_bio': True,
    }},
        upsert=False)
    return json.dumps({'msg': True})
